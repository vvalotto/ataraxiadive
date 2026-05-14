"""
Seed-C UAT SP6 — Resultados restantes Buenos Aires 2025

Pre-requisito: F-07 y F-08 ejecutadas · torneo en estado EJECUCION.

Carga los resultados de los atletas que no fueron ingresados manualmente en F-07/F-08.
Salta performances que ya tienen estado != AnunciadaAP (ya procesadas).

Tipos de resultado asignados (mix realista para validación):
  · Blanca               — resultado válido sin incidencias
  · BlancaConPenalización — RP medido con deducción INFRACCION_TECNICA
  · Roja BKO_SUPERFICIE  — blackout en superficie
  · Roja BKO_SUBACUATICO — blackout subacuático
  · DNS                  — atleta en grilla pero sin resultado real

Uso:
  uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <uuid>
  uv run python tests/uat/sp6/seed_ba2025_resultados.py --torneo-id <uuid> --disciplina STA
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

# ── Overrides de escenario ────────────────────────────────────────────────────
# Atletas seleccionados de los últimos puestos de su categoría para no afectar podios.
# Clave: (nombre_exacto, disciplina_plataforma)
# card: "Roja" | "Blanca" | "DNS"
# Para Roja: motivo_dq + distancia_blackout (opcional, solo disciplinas de distancia)
# Para Blanca con penal: penalizaciones list
# ─────────────────────────────────────────────────────────────────────────────
SCENARIO_OVERRIDES: dict[tuple[str, str], dict] = {
    # BKO_SUPERFICIE — distancia disciplines
    ("Matias Gonzalez Courtois", "DBF"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUPERFICIE",
        "distancia_blackout": "70",  # M-SENIOR rank 11 (78,20m real)
    },
    ("Nicolas Stafforini", "DNF"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUBACUATICO",
        "distancia_blackout": "35",  # M-SENIOR rank 8 (43,96m real)
    },
    ("Ezequiel Cuchiarelli", "DYN"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUPERFICIE",
        "distancia_blackout": "15",  # M-SENIOR rank 12 — último (17,70m real)
    },
    # BKO_SUBACUATICO — time disciplines (sin distancia_blackout)
    ("Matias Gonzalez Courtois", "SPE_2X50"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUBACUATICO",  # M-SENIOR rank 10 — último
    },
    ("Matias Gonzalez Courtois", "STA"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUPERFICIE",  # M-SENIOR rank 13 — último
    },
    # Blanca con penalización — INFRACCION_TECNICA (deducción en unidad de la disciplina)
    ("Diego Calvo", "DBF"): {
        "card": "Blanca",
        "penalizaciones": [{"tipo": "INFRACCION_TECNICA", "deduccion": "3"}],
        # M-SENIOR rank 12 (67,95m real) → RP final 64,95m
    },
    ("Diego Calvo", "DNF"): {
        "card": "Blanca",
        "penalizaciones": [{"tipo": "INFRACCION_TECNICA", "deduccion": "3"}],
        # M-SENIOR rank 9 (43,30m real) → RP final 40,30m
    },
    ("Sebastian Quintana", "DYN"): {
        "card": "Blanca",
        "penalizaciones": [{"tipo": "INFRACCION_TECNICA", "deduccion": "3"}],
        # M-SENIOR rank 11 (55,50m real) → RP final 52,50m
    },
    ("Nicolás Burgell", "SPE_2X50"): {
        "card": "Blanca",
        "penalizaciones": [{"tipo": "INFRACCION_TECNICA", "deduccion": "5"}],
        # M-SENIOR rank 9 (01:39,36 = 99,36s real) → RP final 94,36s
    },
    ("Nicolás Burgell", "STA"): {
        "card": "Blanca",
        "penalizaciones": [{"tipo": "INFRACCION_TECNICA", "deduccion": "5"}],
        # M-SENIOR rank 9 (03:07.22 = 187,22s real) → RP final 182,22s
    },
}


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


def parse_resultado(valor_str: str) -> Decimal:
    """Convierte el resultado del dataset a Decimal.

    Formato mm:ss,cs o mm:ss.cs → segundos totales.
    Formato decimal con coma → metros.
    """
    valor_str = valor_str.strip()
    if ":" in valor_str:
        partes = valor_str.replace(",", ".").split(":")
        return Decimal(int(partes[0]) * 60) + Decimal(partes[1])
    return Decimal(valor_str.replace(",", "."))


def cargar_resultados() -> dict[tuple[str, str], Decimal]:
    """Devuelve {(nombre, disciplina_plataforma): valor_decimal}."""
    data = json.loads(RESULTS_PATH.read_text())
    resultados: dict[tuple[str, str], Decimal] = {}
    for entry in data:
        disc_raw = entry["discipline"]
        if disc_raw == "OVERALL" or entry["result"] is None:
            continue
        disc = DISCIPLINA_MAP.get(disc_raw, disc_raw)
        try:
            resultados[(entry["name"], disc)] = parse_resultado(entry["result"])
        except (InvalidOperation, ValueError) as e:
            log(f"⚠ parse error {entry['name']} {disc} '{entry['result']}': {e}")
    return resultados


def cargar_dns_candidates() -> dict[str, set[str]]:
    """Devuelve {disciplina_plataforma: {nombre}} para atletas en schedules pero no en results."""
    schedules = json.loads(SCHEDULES_PATH.read_text())
    results = json.loads(RESULTS_PATH.read_text())

    por_schedule: dict[str, set[str]] = defaultdict(set)
    for s in schedules:
        disc = DISCIPLINA_MAP.get(s["discipline"], s["discipline"])
        por_schedule[disc].add(s["name"])

    con_resultado: dict[str, set[str]] = defaultdict(set)
    for r in results:
        if r["discipline"] == "OVERALL" or r["result"] is None:
            continue
        disc = DISCIPLINA_MAP.get(r["discipline"], r["discipline"])
        con_resultado[disc].add(r["name"])

    return {
        disc: atletas - con_resultado[disc]
        for disc, atletas in por_schedule.items()
        if atletas - con_resultado[disc]
    }


def procesar_performance(
    client: httpx.Client,
    comp_id: str,
    disciplina: str,
    entrada: dict,
    resultados: dict[tuple[str, str], Decimal],
    dns_candidates: dict[str, set[str]],
    juez_h: dict,
) -> str:
    """Procesa una performance. Retorna: 'ok' | 'dns' | 'skip' | 'err'."""
    nombre = entrada.get("nombre_atleta", "")
    participante_id = entrada.get("atleta_id")
    posicion = entrada.get("posicion", 1)
    andarivel = entrada.get("andarivel", 1)

    override = SCENARIO_OVERRIDES.get((nombre, disciplina))

    # ── DNS ────────────────────────────────────────────────────────────────────
    is_dns = (override and override["card"] == "DNS") or (
        nombre in dns_candidates.get(disciplina, set())
    )
    if is_dns:
        resp = client.post(
            f"/competencia/{comp_id}/registrar-dns",
            json={"participante_id": participante_id, "disciplina": disciplina},
            headers=juez_h,
        )
        if resp.status_code == 204:
            log(f"  ✓ {nombre} → DNS")
            return "dns"
        log(f"  ✗ {nombre} DNS error: {resp.status_code} {resp.text[:150]}")
        return "err"

    # ── Obtener valor RP ───────────────────────────────────────────────────────
    resultado = resultados.get((nombre, disciplina))
    if resultado is None:
        log(f"  ⚠ {nombre} — sin resultado en dataset, registrando DNS")
        resp = client.post(
            f"/competencia/{comp_id}/registrar-dns",
            json={"participante_id": participante_id, "disciplina": disciplina},
            headers=juez_h,
        )
        return "dns" if resp.status_code == 204 else "err"

    # ── Llamar atleta ──────────────────────────────────────────────────────────
    ot_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    resp = client.post(
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
    if resp.status_code not in (204, 409):
        log(f"  ✗ {nombre} llamar error: {resp.status_code} {resp.text[:150]}")
        return "err"

    # ── Registrar resultado ────────────────────────────────────────────────────
    unidad = DISCIPLINA_UNIDAD[disciplina]
    resp = client.post(
        f"/competencia/{comp_id}/registrar-resultado",
        json={
            "participante_id": participante_id,
            "disciplina": disciplina,
            "valor_rp": str(resultado),
            "unidad": unidad,
        },
        headers=juez_h,
    )
    if resp.status_code != 204:
        log(f"  ✗ {nombre} registrar-resultado error: {resp.status_code} {resp.text[:150]}")
        return "err"

    # ── Asignar tarjeta ────────────────────────────────────────────────────────
    if override and override["card"] == "Roja":
        tarjeta_body: dict = {
            "participante_id": participante_id,
            "disciplina": disciplina,
            "tipo": "Roja",
            "motivo_dq": override["motivo_dq"],
        }
        if "distancia_blackout" in override:
            tarjeta_body["distancia_blackout"] = override["distancia_blackout"]
        motivo_label = override["motivo_dq"]
    elif override and override.get("penalizaciones"):
        tarjeta_body = {
            "participante_id": participante_id,
            "disciplina": disciplina,
            "tipo": "Blanca",
            "penalizaciones": override["penalizaciones"],
        }
        motivo_label = f"Blanca+{len(override['penalizaciones'])}penal"
    else:
        tarjeta_body = {
            "participante_id": participante_id,
            "disciplina": disciplina,
            "tipo": "Blanca",
        }
        motivo_label = "Blanca"

    resp = client.post(
        f"/competencia/{comp_id}/asignar-tarjeta",
        json=tarjeta_body,
        headers=juez_h,
    )
    if resp.status_code != 204:
        log(f"  ✗ {nombre} asignar-tarjeta error: {resp.status_code} {resp.text[:150]}")
        return "err"

    log(f"  ✓ {nombre} — RP={resultado} {unidad} · {motivo_label}")
    return "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed-C UAT SP6 — Resultados BA2025")
    parser.add_argument("--torneo-id", required=True)
    parser.add_argument(
        "--disciplina",
        help="Procesar solo esta disciplina (ej. STA, DBF, DNF, DYN, SPE_2X50). "
        "Si se omite, procesa todas.",
    )
    args = parser.parse_args()
    torneo_id = args.torneo_id
    filtro_disciplina = args.disciplina

    print("\n=== Seed-C UAT SP6 — Resultados BA2025 ===\n")
    print(f"  torneo_id:  {torneo_id}")
    if filtro_disciplina:
        print(f"  disciplina: {filtro_disciplina}")
    print()

    resultados = cargar_resultados()
    dns_candidates = cargar_dns_candidates()
    log(f"Dataset: {len(resultados)} resultados cargados")
    for disc, nombres in dns_candidates.items():
        log(f"DNS candidates {disc}: {sorted(nombres)}")
    print()

    with httpx.Client(base_url=BASE, timeout=30) as client:

        # ── Verificar estado del torneo ────────────────────────────────────────
        print("▸ Verificando estado del torneo")
        login(client, f"organizador{EMAIL_DOMAIN}")  # warm-up
        resp = client.get(f"/torneos/{torneo_id}")
        assert_ok(resp, "obtener torneo")
        estado = resp.json().get("estado")
        if estado != "EJECUCION":
            print(f"\n✗ El torneo está en estado '{estado}' — debe estar en EJECUCION.")
            sys.exit(1)
        log(f"✓ estado: {estado}")
        print()

        # ── Autenticar jueces ──────────────────────────────────────────────────
        tokens = {
            1: login(client, f"juez1{EMAIL_DOMAIN}"),
            2: login(client, f"juez2{EMAIL_DOMAIN}"),
            3: login(client, f"juez3{EMAIL_DOMAIN}"),
        }

        # ── Obtener competencias ───────────────────────────────────────────────
        print("▸ Obteniendo competencias del torneo")
        resp = client.get("/competencia", params={"torneo_id": torneo_id})
        assert_ok(resp, "competencias por torneo")
        competencias = resp.json()

        if filtro_disciplina:
            competencias = [c for c in competencias if c["disciplina"] == filtro_disciplina]
            if not competencias:
                print(f"\n✗ No se encontró competencia para disciplina '{filtro_disciplina}'.")
                sys.exit(1)

        log(f"Competencias a procesar: {[c['disciplina'] for c in competencias]}")
        print()

        # ── Procesar disciplinas ───────────────────────────────────────────────
        totales = {"ok": 0, "dns": 0, "skip": 0, "err": 0}

        for comp in competencias:
            comp_id = comp["competencia_id"]
            disciplina = comp["disciplina"]
            print(f"▸ {disciplina}  (comp_id={comp_id[:8]}...)")

            resp = client.get(
                f"/competencia/{comp_id}/grilla",
                params={"disciplina": disciplina},
            )
            assert_ok(resp, f"grilla {disciplina}")
            grilla = resp.json()

            for entrada in grilla:
                if entrada.get("estado") != "AnunciadaAP":
                    log(
                        f"  ⏭ {entrada.get('nombre_atleta')} — ya procesado ({entrada.get('estado')})"
                    )
                    totales["skip"] += 1
                    continue

                andarivel = entrada.get("andarivel", 1)
                juez_h = {"Authorization": f"Bearer {tokens.get(andarivel, tokens[1])}"}

                resultado = procesar_performance(
                    client,
                    comp_id,
                    disciplina,
                    entrada,
                    resultados,
                    dns_candidates,
                    juez_h,
                )
                totales[resultado] = totales.get(resultado, 0) + 1

            print()

        print("=== Seed-C completo ===")
        print(f"  Registrados:  {totales['ok']}")
        print(f"  DNS:          {totales['dns']}")
        print(f"  Saltados:     {totales['skip']} (ya procesados en F-07/F-08)")
        print(f"  Errores:      {totales['err']}")
        if totales["err"] > 0:
            print("\n  ⚠ Hay errores — revisar antes de continuar F-09.")
        else:
            print("\n  ✓ Próximo paso: verificar rankings y podios en F-09.")


if __name__ == "__main__":
    main()
