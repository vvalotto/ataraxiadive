"""
Seed-C UAT SP6 — Resultados restantes Buenos Aires 2025

Pre-requisito: F-07 y F-08 ejecutadas · torneo en estado EJECUCION.

Carga los resultados de los atletas que no fueron ingresados manualmente en F-07/F-08.
Salta performances que ya tienen estado != AnunciadaAP (ya procesadas).

Atletas con resultado en results.json → llamar + registrar-resultado + asignar-tarjeta BLANCA.
Atletas en grilla sin resultado (DNS candidates de schedules.json) → registrar-dns.

Uso:  uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <uuid>
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
PASSWORD = "Ba2025uat!"
EMAIL_DOMAIN = "@ba2025.uat"

DISCIPLINA_MAP = {"SPE": "SPE_2X50"}
DISCIPLINA_UNIDAD = {
    "DBF": "METROS",
    "DNF": "METROS",
    "DYN": "METROS",
    "SPE_2X50": "SEGUNDOS",
    "STA": "SEGUNDOS",
}

RESULTS_PATH = Path("data/datasets/buenos_aires_2025/results.json")
SCHEDULES_PATH = Path("data/datasets/buenos_aires_2025/schedules.json")
IDS_PATH = Path("quality/reports/uat/SP6/uat_ba2025_usuarios_ids.json")


def log(msg: str) -> None:
    print(f"  {msg}")


def assert_ok(resp: httpx.Response, context: str) -> dict:
    if resp.status_code not in (200, 201, 204):
        print(f"\n✗ ERROR en {context}: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)
    return resp.json() if resp.content else {}


def login(client: httpx.Client, email: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert_ok(resp, f"login {email}")
    return resp.json()["access_token"]


def parse_resultado(valor_str: str, disciplina: str) -> Decimal:
    """Convierte el resultado del dataset al valor Decimal en la unidad de la disciplina.

    DBF/DNF/DYN: coma decimal → metros (ej. '78,52' → 78.52)
    SPE: mm:ss,cs → segundos (ej. '02:29,39' → 149.39)
    STA: mm:ss.cs → segundos (ej. '03:16.29' → 196.29)
    """
    valor_str = valor_str.strip()

    if ":" in valor_str:
        # Formato mm:ss,cs o mm:ss.cs
        partes = valor_str.replace(",", ".").split(":")
        minutos = int(partes[0])
        segundos = Decimal(partes[1])
        return Decimal(minutos * 60) + segundos
    else:
        # Formato decimal con coma (metros)
        return Decimal(valor_str.replace(",", "."))


def cargar_resultados() -> dict[tuple[str, str], Decimal]:
    """Devuelve {(nombre, disciplina_plataforma): valor_decimal}."""
    data = json.loads(RESULTS_PATH.read_text())
    resultados: dict[tuple[str, str], Decimal] = {}
    for entry in data:
        disc_raw = entry["discipline"]
        if disc_raw == "OVERALL":
            continue
        disc = DISCIPLINA_MAP.get(disc_raw, disc_raw)
        nombre = entry["name"]
        if entry["result"] is not None:
            try:
                resultados[(nombre, disc)] = parse_resultado(entry["result"], disc)
            except (InvalidOperation, ValueError) as e:
                log(f"⚠ parse error {nombre} {disc} '{entry['result']}': {e}")
    return resultados


def cargar_dns_candidates() -> dict[str, set[str]]:
    """Devuelve {disciplina_plataforma: {nombre_atleta}} para DNS (en schedules pero no en results)."""
    schedules = json.loads(SCHEDULES_PATH.read_text())
    results = json.loads(RESULTS_PATH.read_text())

    por_schedule: dict[str, set[str]] = defaultdict(set)
    for s in schedules:
        disc = DISCIPLINA_MAP.get(s["discipline"], s["discipline"])
        por_schedule[disc].add(s["name"])

    por_result: dict[str, set[str]] = defaultdict(set)
    for r in results:
        if r["discipline"] == "OVERALL":
            continue
        disc = DISCIPLINA_MAP.get(r["discipline"], r["discipline"])
        if r["result"] is not None:
            por_result[disc].add(r["name"])

    dns: dict[str, set[str]] = {}
    for disc, atletas in por_schedule.items():
        missing = atletas - por_result[disc]
        if missing:
            dns[disc] = missing
    return dns


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed-C UAT SP6 — Resultados BA2025")
    parser.add_argument("--torneo-id", required=True, help="UUID del torneo en EJECUCION")
    args = parser.parse_args()
    torneo_id = args.torneo_id

    print("\n=== Seed-C UAT SP6 — Resultados restantes BA2025 ===\n")
    print(f"  torneo_id: {torneo_id}\n")

    resultados = cargar_resultados()
    dns_candidates = cargar_dns_candidates()
    log(f"Resultados en dataset: {len(resultados)} entradas")
    for disc, nombres in dns_candidates.items():
        log(f"DNS candidates {disc}: {sorted(nombres)}")
    print()

    ids_data = json.loads(IDS_PATH.read_text())
    atleta_ids: dict[str, str] = {
        nombre: info["atleta_id"] for nombre, info in ids_data["atletas"].items()
    }

    with httpx.Client(base_url=BASE, timeout=30) as client:

        # ── 1. Verificar estado del torneo ────────────────────────────────────
        print("▸ Verificando estado del torneo")
        org_token = login(client, f"organizador{EMAIL_DOMAIN}")
        resp = client.get(f"/torneos/{torneo_id}")
        assert_ok(resp, "obtener torneo")
        estado = resp.json().get("estado")
        if estado != "EJECUCION":
            print(f"\n✗ El torneo está en estado '{estado}' — debe estar en EJECUCION.")
            sys.exit(1)
        log(f"✓ estado: {estado}")
        print()

        # ── 2. Obtener competencias del torneo ────────────────────────────────
        print("▸ Obteniendo competencias del torneo")
        juez1_token = login(client, f"juez1{EMAIL_DOMAIN}")
        juez2_token = login(client, f"juez2{EMAIL_DOMAIN}")
        juez3_token = login(client, f"juez3{EMAIL_DOMAIN}")

        resp = client.get("/competencia", params={"torneo_id": torneo_id})
        assert_ok(resp, "competencias por torneo")
        competencias = resp.json()
        log(f"Competencias encontradas: {len(competencias)}")
        for c in competencias:
            log(f"  {c['disciplina']}: {c['competencia_id']}")
        print()

        # ── 3. Procesar cada competencia ──────────────────────────────────────
        total_ok = 0
        total_dns = 0
        total_skip = 0
        total_err = 0

        for comp in competencias:
            comp_id = comp["competencia_id"]
            disciplina = comp["disciplina"]
            print(f"▸ Procesando {disciplina} (comp_id={comp_id[:8]}...)")

            resp = client.get(
                f"/competencia/{comp_id}/grilla",
                params={"disciplina": disciplina},
            )
            assert_ok(resp, f"grilla {disciplina}")
            grilla = resp.json()

            for entrada in grilla:
                estado_perf = entrada.get("estado")
                nombre = entrada.get("nombre_atleta", "")
                participante_id = entrada.get("atleta_id")
                andarivel = entrada.get("andarivel", 1)
                posicion = entrada.get("posicion", 1)

                if estado_perf != "AnunciadaAP":
                    log(f"  ⏭ {nombre} — ya procesado ({estado_perf})")
                    total_skip += 1
                    continue

                # Juez según andarivel
                if andarivel == 3:
                    juez_token = juez3_token
                elif andarivel == 2:
                    juez_token = juez2_token
                else:
                    juez_token = juez1_token
                juez_h = {"Authorization": f"Bearer {juez_token}"}

                # ¿DNS?
                disc_dns = dns_candidates.get(disciplina, set())
                if nombre in disc_dns:
                    resp_dns = client.post(
                        f"/competencia/{comp_id}/registrar-dns",
                        json={"participante_id": participante_id, "disciplina": disciplina},
                        headers=juez_h,
                    )
                    if resp_dns.status_code == 204:
                        log(f"  ✓ {nombre} → DNS")
                        total_dns += 1
                    else:
                        log(f"  ✗ {nombre} DNS error: {resp_dns.status_code} {resp_dns.text[:200]}")
                        total_err += 1
                    continue

                # ¿Tiene resultado?
                resultado = resultados.get((nombre, disciplina))
                if resultado is None:
                    log(f"  ⚠ {nombre} — sin resultado en dataset, registrando DNS")
                    resp_dns = client.post(
                        f"/competencia/{comp_id}/registrar-dns",
                        json={"participante_id": participante_id, "disciplina": disciplina},
                        headers=juez_h,
                    )
                    if resp_dns.status_code == 204:
                        total_dns += 1
                    else:
                        log(f"  ✗ DNS error: {resp_dns.status_code}")
                        total_err += 1
                    continue

                # Llamar atleta
                ot_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                resp_llamar = client.post(
                    f"/competencia/{comp_id}/llamar",
                    json={
                        "participante_id": participante_id,
                        "disciplina": disciplina,
                        "ot_programado": ot_now,
                        "posicion_grilla": posicion,
                        "andarivel": andarivel,
                    },
                    headers=juez_h,
                )
                if resp_llamar.status_code not in (204, 409):
                    log(
                        f"  ✗ {nombre} llamar error: {resp_llamar.status_code} {resp_llamar.text[:200]}"
                    )
                    total_err += 1
                    continue

                # Registrar resultado
                unidad = DISCIPLINA_UNIDAD[disciplina]
                resp_rp = client.post(
                    f"/competencia/{comp_id}/registrar-resultado",
                    json={
                        "participante_id": participante_id,
                        "disciplina": disciplina,
                        "valor_rp": str(resultado),
                        "unidad": unidad,
                    },
                    headers=juez_h,
                )
                if resp_rp.status_code != 204:
                    log(
                        f"  ✗ {nombre} registrar-resultado error: {resp_rp.status_code} {resp_rp.text[:200]}"
                    )
                    total_err += 1
                    continue

                # Asignar tarjeta blanca
                resp_tarjeta = client.post(
                    f"/competencia/{comp_id}/asignar-tarjeta",
                    json={
                        "participante_id": participante_id,
                        "disciplina": disciplina,
                        "tipo": "Blanca",
                    },
                    headers=juez_h,
                )
                if resp_tarjeta.status_code != 204:
                    log(
                        f"  ✗ {nombre} asignar-tarjeta error: {resp_tarjeta.status_code} {resp_tarjeta.text[:200]}"
                    )
                    total_err += 1
                    continue

                log(f"  ✓ {nombre} — RP={resultado} {unidad} · Blanca")
                total_ok += 1

        print()
        print("=== Seed-C completo ===")
        print(f"  Registrados:    {total_ok}")
        print(f"  DNS:            {total_dns}")
        print(f"  Saltados:       {total_skip} (ya procesados)")
        print(f"  Errores:        {total_err}")
        if total_err > 0:
            print("\n  ⚠ Hay errores — revisar log antes de continuar F-09.")
        else:
            print("\n  Próximo paso: F-09 verificación de rankings y podios.")


if __name__ == "__main__":
    main()
