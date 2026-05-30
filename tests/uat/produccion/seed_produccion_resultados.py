"""
Seed producción — Resultados progresivos por disciplina

Alimenta la app en https://ataraxiadive.fly.dev con resultados del dataset BA2025.
Procesa solo los atletas en estado AnunciadaAP (los ya Ejecutados/DNS se saltean).

Uso:
  uv run python tests/uat/produccion/seed_produccion_resultados.py --disciplina STA
  uv run python tests/uat/produccion/seed_produccion_resultados.py --disciplina DNF --limite 6
  uv run python tests/uat/produccion/seed_produccion_resultados.py --disciplina DNF --desde 7
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

import httpx

BASE = "https://ataraxiadive.fly.dev"
TORNEO_ID = "996e9f82-6a3f-4a6a-bd53-2d6414c10a13"

ORG_EMAIL = "org1faas@prueba.uat"
PASSWORD = "Ataraxia2026?"

JUECES = {
    1: "juez1apnea@prueba.uat",
    2: "raul@urquiza.uat",
}

DISCIPLINA_UNIDAD = {
    "DBF": "Metros",
    "DNF": "Metros",
    "DYN": "Metros",
    "SPE_2X50": "Segundos",
    "STA": "Segundos",
}

RESULTS_PATH = Path("data/datasets/buenos_aires_2025/results.json")

# Overrides por (nombre_normalizado, disciplina) → tarjeta especial
# card: "Roja" | "DNS"
# Para Roja: motivo_dq obligatorio, distancia_blackout opcional (solo disciplinas de distancia)
SCENARIO_OVERRIDES: dict[tuple[str, str], dict] = {
    # DNF
    ("NICOLAS STAFFORINI", "DNF"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUBACUATICO",
        "distancia_blackout": "30",
    },
    ("MATIAS GONZALEZ COURTOIS", "DNF"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUPERFICIE",
        "distancia_blackout": "40",
    },
    # DYN — Tanda 1
    ("MATIAS GONZALEZ COURTOIS", "DYN"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUPERFICIE",
        "distancia_blackout": "45",
    },
    ("MAURO ALMADA", "DYN"): {
        "card": "BlancaConPenalizaciones",
        "penalizaciones": [{"tipo": "SIN_CONTACTO_PARED", "deduccion": "3"}],
    },
    ("EZEQUIEL CUCHIARELLI", "DYN"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUBACUATICO",
        "distancia_blackout": "10",
    },
    # DYN — Tanda 2
    ("GUADALUPE FARDI", "DYN"): {
        "card": "BlancaConPenalizaciones",
        "penalizaciones": [{"tipo": "SIN_CONTACTO_PARED", "deduccion": "3"}],
    },
    ("THIAGO STALLDECKER", "DYN"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUPERFICIE",
        "distancia_blackout": "55",
    },
    # DYN — Tanda 3
    ("PABLO SALE", "DYN"): {
        "card": "BlancaConPenalizaciones",
        "penalizaciones": [{"tipo": "SIN_CONTACTO_PARED", "deduccion": "3"}],
    },
    ("NICOLAS BURGELL", "DYN"): {
        "card": "Roja",
        "motivo_dq": "BKO_SUBACUATICO",
        "distancia_blackout": "70",
    },
}


def normalize(s: str) -> str:
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode().upper()


def parse_resultado(valor_str: str) -> Decimal:
    valor_str = valor_str.strip()
    if ":" in valor_str:
        partes = valor_str.replace(",", ".").split(":")
        return Decimal(int(partes[0]) * 60) + Decimal(partes[1])
    return Decimal(valor_str.replace(",", "."))


def cargar_resultados(disciplina: str) -> dict[str, Decimal]:
    data = json.loads(RESULTS_PATH.read_text())
    return {
        normalize(r["name"]): parse_resultado(r["result"])
        for r in data
        if r["discipline"] == disciplina and r["result"] is not None
    }


def assert_ok(resp: httpx.Response, context: str) -> dict:
    if resp.status_code not in (200, 201, 204):
        print(f"\n✗ ERROR en {context}: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)
    return resp.json() if resp.content else {}


def login(client: httpx.Client, email: str, rol: str | None = None) -> str:
    body: dict = {"email": email, "password": PASSWORD}
    if rol:
        body["rol_elegido"] = rol
    resp = client.post("/auth/login", json=body)
    data = resp.json()
    if "requires_role_selection" in data:
        rol_elegido = rol or data["roles"][0]
        body["rol_elegido"] = rol_elegido
        resp = client.post("/auth/login", json=body)
        assert_ok(resp, f"login {email} (rol={rol_elegido})")
        return resp.json()["access_token"]
    assert_ok(resp, f"login {email}")
    return data["access_token"]


def procesar_atleta(
    client: httpx.Client,
    comp_id: str,
    disciplina: str,
    entrada: dict,
    resultados: dict[str, Decimal],
    juez_token: str,
    posicion: int,
) -> str:
    """Procesa un atleta en AnunciadaAP. Retorna 'ok' | 'dns' | 'err'."""
    nombre_prod = entrada.get("nombre_atleta", "")
    participante_id = entrada.get("atleta_id")
    andarivel = entrada.get("andarivel", 1)
    juez_h = {"Authorization": f"Bearer {juez_token}"}
    unidad = DISCIPLINA_UNIDAD[disciplina]
    ot_now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    override = SCENARIO_OVERRIDES.get((normalize(nombre_prod), disciplina))

    # Llamar al atleta
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
    if resp.status_code != 204:
        print(f"  ✗ {nombre_prod} — llamar error: {resp.status_code} {resp.text[:200]}")
        return "err"

    # DNS forzado por override o por ausencia en dataset
    resultado = resultados.get(normalize(nombre_prod))
    if (override and override["card"] == "DNS") or resultado is None:
        resp = client.post(
            f"/competencia/{comp_id}/registrar-dns",
            json={"participante_id": participante_id, "disciplina": disciplina},
            headers=juez_h,
        )
        if resp.status_code == 204:
            print(f"  ✓ {nombre_prod:35s} → DNS")
            return "dns"
        print(f"  ✗ {nombre_prod} — DNS error: {resp.status_code} {resp.text[:200]}")
        return "err"

    # Registrar resultado
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
        print(f"  ✗ {nombre_prod} — registrar-resultado error: {resp.status_code} {resp.text[:200]}")
        return "err"

    # Tarjeta
    if override and override["card"] == "Roja":
        tarjeta_body: dict = {
            "participante_id": participante_id,
            "disciplina": disciplina,
            "tipo": "Roja",
            "motivo_dq": override["motivo_dq"],
        }
        if "distancia_blackout" in override:
            tarjeta_body["distancia_blackout"] = override["distancia_blackout"]
        label = f"Roja ({override['motivo_dq']})"
    elif override and override["card"] == "BlancaConPenalizaciones":
        tarjeta_body = {
            "participante_id": participante_id,
            "disciplina": disciplina,
            "tipo": "BlancaConPenalizaciones",
            "penalizaciones": override["penalizaciones"],
        }
        deduccion = sum(float(p["deduccion"]) for p in override["penalizaciones"])
        label = f"BlancaConPenalizaciones (−{deduccion:.0f}m)"
    else:
        tarjeta_body = {
            "participante_id": participante_id,
            "disciplina": disciplina,
            "tipo": "Blanca",
        }
        label = "Blanca"

    resp = client.post(
        f"/competencia/{comp_id}/asignar-tarjeta",
        json=tarjeta_body,
        headers=juez_h,
    )
    if resp.status_code != 204:
        print(f"  ✗ {nombre_prod} — asignar-tarjeta error: {resp.status_code} {resp.text[:200]}")
        return "err"

    print(f"  ✓ {nombre_prod:35s} RP={resultado} {unidad} · {label}")
    return "ok"


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed producción — resultados por disciplina")
    parser.add_argument("--disciplina", required=True, choices=["STA", "DNF", "DYN", "DBF", "SPE_2X50"])
    parser.add_argument("--limite", type=int, help="Procesar solo los primeros N pendientes")
    parser.add_argument("--desde", type=int, default=1, help="Empezar desde el N-ésimo pendiente (1-based)")
    parser.add_argument("--dry-run", action="store_true", help="Muestra el plan sin llamar a la API")
    args = parser.parse_args()
    disciplina = args.disciplina

    print(f"\n=== Seed producción — {disciplina} ===\n")
    print(f"  Base:   {BASE}")
    print(f"  Torneo: {TORNEO_ID}\n")

    resultados = cargar_resultados(disciplina)

    with httpx.Client(base_url=BASE, timeout=30) as client:
        org_token = login(client, ORG_EMAIL)
        org_h = {"Authorization": f"Bearer {org_token}"}

        resp = client.get("/competencia", params={"torneo_id": TORNEO_ID}, headers=org_h)
        assert_ok(resp, "competencias")
        comp = next((c for c in resp.json() if c["disciplina"] == disciplina), None)
        if not comp:
            print(f"✗ No se encontró competencia para {disciplina}")
            sys.exit(1)
        comp_id = comp["competencia_id"]

        resp = client.get(f"/competencia/{comp_id}/grilla", params={"disciplina": disciplina}, headers=org_h)
        assert_ok(resp, "grilla")
        grilla = resp.json()

        pendientes = [e for e in grilla if e.get("estado") == "AnunciadaAP"]
        ya_procesados = len(grilla) - len(pendientes)

        # Aplicar rango --desde / --limite
        inicio = args.desde - 1
        fin = inicio + args.limite if args.limite else len(pendientes)
        tanda = pendientes[inicio:fin]

        print(f"  Ya procesados:  {ya_procesados}")
        print(f"  Total pendientes: {len(pendientes)}")
        print(f"  Esta tanda:     {len(tanda)} (posiciones {inicio+1}–{inicio+len(tanda)})\n")

        if not tanda:
            print("  Nada que procesar en este rango.")
            return

        # Mostrar plan
        print("  Plan:")
        for i, entrada in enumerate(tanda, start=inicio+1):
            nombre = entrada.get("nombre_atleta", "")
            override = SCENARIO_OVERRIDES.get((normalize(nombre), disciplina))
            resultado = resultados.get(normalize(nombre))
            if override and override["card"] == "DNS":
                tarjeta = "DNS (override)"
            elif resultado is None:
                tarjeta = "DNS (sin dato)"
            elif override and override["card"] == "Roja":
                tarjeta = f"Roja ({override['motivo_dq']})"
            elif override and override["card"] == "BlancaConPenalizaciones":
                deduccion = sum(Decimal(p["deduccion"]) for p in override["penalizaciones"])
                tarjeta = f"BlancaConPenalizaciones −{deduccion}m → {resultado - deduccion} {DISCIPLINA_UNIDAD[disciplina]}"
            else:
                tarjeta = f"Blanca — {resultado} {DISCIPLINA_UNIDAD[disciplina]}"
            print(f"    {i:2d}. {nombre:35s} → {tarjeta}")

        if args.dry_run:
            print("\n  [DRY RUN — sin llamadas de escritura]")
            return

        print()
        juez_tokens = {andarivel: login(client, email, rol="JUEZ") for andarivel, email in JUECES.items()}
        print(f"  Jueces autenticados: {list(JUECES.values())}\n")
        print(f"▸ Ejecutando tanda...\n")

        totales: dict[str, int] = {"ok": 0, "dns": 0, "err": 0}
        for pos, entrada in enumerate(tanda, start=inicio+1):
            andarivel = entrada.get("andarivel", 1)
            juez_token = juez_tokens.get(andarivel, juez_tokens[1])
            r = procesar_atleta(client, comp_id, disciplina, entrada, resultados, juez_token, pos)
            totales[r] = totales.get(r, 0) + 1

        print(f"\n=== Tanda completada ===")
        print(f"  Registrados: {totales['ok']}")
        print(f"  DNS:         {totales['dns']}")
        print(f"  Errores:     {totales['err']}")
        if totales["err"] == 0:
            print(f"\n  ✓ Verificar: {BASE}/portalapnea")


if __name__ == "__main__":
    main()
