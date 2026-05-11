"""
Seed-B UAT SP6 — Inscripciones y APs Buenos Aires 2025

Pre-requisito: Seed-A ejecutado (usuarios existen) · torneo_id de F-02.

Acciones:
  1. Abre inscripciones del torneo (como organizador)
  2. Inscribe 31 atletas con sus disciplinas
  3. Declara el AP de cada atleta en cada disciplina

Uso:  uv run python tests/uat/sp6/seed_ba2025_inscripciones.py --torneo-id <uuid>
"""

from __future__ import annotations

import argparse
import base64
import json
import re
import sys
import unicodedata
from collections import defaultdict
from decimal import Decimal
from pathlib import Path

import httpx

BASE = "http://localhost:8000"
PASSWORD = "Ba2025uat!"
EMAIL_DOMAIN = "@ba2025.uat"

# El dataset BA2025 usa "SPE" (legacy) que en la plataforma corresponde a SPE_2X50
DISCIPLINA_MAP = {"SPE": "SPE_2X50"}

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


def normalizar_email(nombre_completo: str) -> str:
    nfkd = unicodedata.normalize("NFKD", nombre_completo.lower())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", ".", sin_tildes).strip(".")


def decode_sub(token: str) -> str:
    payload = token.split(".")[1]
    payload += "==" * ((4 - len(payload) % 4) % 4)
    return json.loads(base64.b64decode(payload))["sub"]


def ap_a_decimal(valor_str: str) -> Decimal:
    """Convierte AP del dataset a Decimal.

    Si el valor tiene formato mm:ss lo convierte a segundos (para STA/SPE).
    Si es un número directo lo usa tal cual (metros para DBF/DNF/DYN).
    """
    if ":" in valor_str:
        partes = valor_str.split(":")
        minutos = int(partes[0])
        segundos = Decimal(partes[1])
        return Decimal(minutos * 60) + segundos
    return Decimal(valor_str)


def cargar_schedules() -> dict[str, list[dict]]:
    """Devuelve {nombre_atleta: [{disc, ap_decimal}, ...]}."""
    data = json.loads(SCHEDULES_PATH.read_text())
    por_atleta: dict[str, list[dict]] = defaultdict(list)
    for entry in data:
        disciplina = DISCIPLINA_MAP.get(entry["discipline"], entry["discipline"])
        por_atleta[entry["name"]].append(
            {
                "disciplina": disciplina,
                "ap": ap_a_decimal(entry["announced_performance"]),
            }
        )
    return dict(por_atleta)


def login(client: httpx.Client, email: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    assert_ok(resp, f"login {email}")
    return resp.json()["access_token"]


def main() -> None:
    parser = argparse.ArgumentParser(description="Seed-B UAT SP6 — Inscripciones BA2025")
    parser.add_argument("--torneo-id", required=True, help="UUID del torneo creado en F-02")
    args = parser.parse_args()
    torneo_id = args.torneo_id

    print(f"\n=== Seed-B UAT SP6 — Inscripciones BA2025 ===\n")
    print(f"  torneo_id: {torneo_id}\n")

    schedules = cargar_schedules()
    log(f"Dataset cargado: {len(schedules)} atletas")

    ids_data = json.loads(IDS_PATH.read_text())
    atleta_ids: dict[str, str] = {
        nombre: info["atleta_id"] for nombre, info in ids_data["atletas"].items()
    }

    with httpx.Client(base_url=BASE, timeout=30) as client:

        # ── 1. Abrir inscripciones ─────────────────────────────────────────────
        print("▸ Abriendo inscripciones del torneo")
        org_token = login(client, f"organizador{EMAIL_DOMAIN}")
        org_h = {"Authorization": f"Bearer {org_token}"}
        resp = client.put(f"/torneos/{torneo_id}/abrir-inscripcion", headers=org_h)
        if resp.status_code == 409:
            log("inscripciones ya abiertas (OK)")
        else:
            assert_ok(resp, "abrir-inscripcion")
            log("✓ inscripciones abiertas")
        print()

        # ── 2. Inscribir atletas y declarar APs ───────────────────────────────
        print(f"▸ Inscribiendo {len(schedules)} atletas con APs")
        ok = 0
        err = 0

        for nombre, disciplinas_ap in schedules.items():
            atleta_id = atleta_ids.get(nombre)
            if not atleta_id:
                log(f"✗ atleta_id no encontrado para: {nombre}")
                err += 1
                continue

            email = f"{normalizar_email(nombre)}{EMAIL_DOMAIN}"
            token = login(client, email)
            headers = {"Authorization": f"Bearer {token}"}

            disciplinas_lista = [d["disciplina"] for d in disciplinas_ap]

            resp = client.post(
                "/registro/inscripciones",
                json={
                    "atleta_id": atleta_id,
                    "torneo_id": torneo_id,
                    "disciplinas": disciplinas_lista,
                },
                headers=headers,
            )
            if resp.status_code == 409 and "ya está inscripto" in resp.text:
                # Obtener inscripcion existente
                resp2 = client.get(
                    f"/registro/atletas/{atleta_id}/inscripciones", headers=headers
                )
                if resp2.status_code != 200:
                    log(f"✗ no se pudo recuperar inscripcion para {nombre}")
                    err += 1
                    continue
                inscripciones = resp2.json()
                match = next((i for i in inscripciones if i["torneo_id"] == torneo_id), None)
                if not match:
                    log(f"✗ inscripcion no encontrada para {nombre} en torneo {torneo_id}")
                    err += 1
                    continue
                inscripcion_id = match["inscripcion_id"]
                log(f"  {nombre}: inscripcion existente → {inscripcion_id}")
            else:
                assert_ok(resp, f"inscripcion {nombre}")
                inscripcion_id = resp.json()["inscripcion_id"]

            # Declarar AP por disciplina
            for entry in disciplinas_ap:
                disc = entry["disciplina"]
                ap_valor = float(entry["ap"])
                resp_ap = client.put(
                    f"/registro/inscripciones/{inscripcion_id}/ap",
                    json={"disciplina": disc, "valor_ap": str(ap_valor)},
                    headers=headers,
                )
                if resp_ap.status_code not in (200, 201):
                    log(f"  ✗ AP {disc} para {nombre}: {resp_ap.status_code} {resp_ap.text[:200]}")

            log(f"✓ {nombre} — {len(disciplinas_ap)} disciplinas")
            ok += 1

        print()
        print(f"  Completado: {ok} atletas OK · {err} errores")

        # ── 3. Verificar total inscriptos ──────────────────────────────────────
        print()
        print("▸ Verificando inscriptos")
        resp = client.get(
            f"/registro/torneos/{torneo_id}/inscriptos",
            headers=org_h,
        )
        if resp.status_code == 200:
            total = len(resp.json())
            log(f"Total inscriptos en torneo: {total}")
        else:
            log(f"✗ no se pudo verificar inscriptos: {resp.status_code}")

    print()
    print("=== Seed-B completo ===")
    print(f"  torneo_id: {torneo_id}")
    print(f"  Estado torneo: INSCRIPCION_ABIERTA")
    print(f"  Próximo paso: F-03 verificación → F-04 inscripción manual atleta")


if __name__ == "__main__":
    main()
