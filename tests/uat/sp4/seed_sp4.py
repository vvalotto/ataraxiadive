"""
Seed UAT SP4 — datos de prueba para el UAT de cierre de BL-004.

Estrategia:
  - HTTP para: usuarios, torneo, atletas, inscripciones (ciclo de vida torneo)
  - Python application layer para: competencia (RegistrarAP + GenerarGrilla +
    ConfirmarGrilla + IniciarCompetencia) — no tienen endpoints HTTP.

Crea:
  - 1 torneo en estado EJECUCION
  - 5 atletas DNF (e02-e06) + 3 atletas STA (t01-t03)
  - 1 juez asignado a ambas disciplinas
  - 2 competencias DNF y STA en estado EJECUCION con grilla confirmada
  - Guarda IDs en quality/reports/uat/SP4/uat_ids.json

Uso:  uv run python tests/uat/sp4/seed_sp4.py
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import httpx

BASE = "http://localhost:8000"
IDS_PATH = Path("quality/reports/uat/SP4/uat_ids.json")

JUEZ_EMAIL = "juez@uat-sp4.test"
JUEZ_PASSWORD = "juezsp4uat2025"
ORG_EMAIL = "organizador@uat-sp4.test"
ORG_PASSWORD = "orgsp4uat2025"
ADMIN_EMAIL = "admin@uat-sp4.test"
ADMIN_PASSWORD = "adminsp4uat2025"

COMPETENCIA_DB = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")


def log(msg: str) -> None:
    print(f"  {msg}")


def assert_ok(resp: httpx.Response, context: str) -> dict:
    if resp.status_code not in (200, 201):
        print(f"\n✗ ERROR en {context}: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)
    return resp.json()


def get_or_create_usuario(client: httpx.Client, email: str, password: str, rol: str) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        log(f"usuario existente: {email}")
        return resp.json()["access_token"]
    resp = client.post("/auth/registro", json={"email": email, "password": password, "rol": rol})
    assert_ok(resp, f"registro {email}")
    resp = client.post("/auth/login", json={"email": email, "password": password})
    log(f"usuario creado: {email}")
    return assert_ok(resp, f"login {email}")["access_token"]


def decode_sub(token: str) -> str:
    payload = token.split(".")[1]
    payload += "==" * ((4 - len(payload) % 4) % 4)
    return json.loads(base64.b64decode(payload))["sub"]


async def setup_competencia(
    competencia_id: UUID,
    disciplina_str: str,
    intervalo_minutos: int,
    juez_id: str,
    torneo_id: str,
    atletas: list[tuple[str, int]],  # (atleta_id, ap_valor)
    unidad_str: str,  # "metros" | "segundos"
) -> None:
    """Configura una competencia completa via application layer."""
    from competencia.application.commands.configurar_intervalo_ot import (
        ConfigurarIntervaloOTCommand,
        ConfigurarIntervaloOTHandler,
    )
    from competencia.application.commands.confirmar_grilla import (
        ConfirmarGrillaCommand,
        ConfirmarGrillaHandler,
    )
    from competencia.application.commands.generar_grilla import (
        GenerarGrillaCommand,
        GenerarGrillaHandler,
    )
    from competencia.application.commands.iniciar_competencia import (
        IniciarCompetenciaCommand,
        IniciarCompetenciaHandler,
    )
    from competencia.application.commands.registrar_ap import (
        RegistrarAPCommand,
        RegistrarAPHandler,
    )
    from competencia.domain.value_objects.disciplina import Disciplina
    from competencia.domain.value_objects.unidad_medida import UnidadMedida
    from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
    from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
    from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
        DisciplinaDescriptorAdapter,
    )
    from competencia.infrastructure.repositories.performances_ap_adapter import (
        PerformancesAPAdapter,
    )
    from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
        SQLiteCompetenciasPorTorneo,
    )

    store = SQLiteEventStore(COMPETENCIA_DB)
    disciplina = Disciplina(disciplina_str)
    unidad = UnidadMedida.Metros if unidad_str == "metros" else UnidadMedida.Segundos
    descriptor = DisciplinaDescriptorAdapter()
    stub = StubCompetenciaEstadoAdapter()
    proyeccion = SQLiteCompetenciasPorTorneo(COMPETENCIA_DB)

    await ConfigurarIntervaloOTHandler(store, proyeccion).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            intervalo_minutos=intervalo_minutos,
            configurado_por=juez_id,
            torneo_id=UUID(torneo_id),
        )
    )
    log("  OT configurado")

    for atleta_id_str, ap_valor in atletas:
        await RegistrarAPHandler(store, stub, descriptor).handle(
            RegistrarAPCommand(
                competencia_id=competencia_id,
                participante_id=UUID(atleta_id_str),
                disciplina=disciplina,
                valor_ap=Decimal(ap_valor),
                unidad=unidad,
            )
        )
    log(f"  {len(atletas)} APs registradas")

    ot_inicio = datetime(2025, 12, 1, 9, 0, 0, tzinfo=timezone.utc)
    ap_adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, ap_adapter, descriptor).handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            ot_inicio=ot_inicio,
        )
    )
    log("  Grilla generada")

    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
        )
    )
    log("  Grilla confirmada")

    await IniciarCompetenciaHandler(store).handle(
        IniciarCompetenciaCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            juez_id=juez_id,
        )
    )
    log("  Competencia iniciada")


def main() -> None:
    print("\n=== Seed UAT SP4 ===\n")

    with httpx.Client(base_url=BASE, timeout=15) as client:

        # ── Usuarios ──────────────────────────────────────────────────────────
        print("▸ Usuarios")
        juez_token = get_or_create_usuario(client, JUEZ_EMAIL, JUEZ_PASSWORD, "JUEZ")
        juez_id = decode_sub(juez_token)
        log(f"juez_id: {juez_id}")

        org_token = get_or_create_usuario(client, ORG_EMAIL, ORG_PASSWORD, "ORGANIZADOR")
        log(f"org_id:  {decode_sub(org_token)}")

        admin_token = get_or_create_usuario(client, ADMIN_EMAIL, ADMIN_PASSWORD, "ADMIN")
        log(f"admin_id: {decode_sub(admin_token)}")

        org_h = {"Authorization": f"Bearer {org_token}"}
        admin_h = {"Authorization": f"Bearer {admin_token}"}

        # ── Torneo ────────────────────────────────────────────────────────────
        print("▸ Torneo")
        resp = client.post(
            "/torneos",
            json={
                "nombre": "UAT SP4 — Flujo de Performance",
                "descripcion": "Torneo de prueba para UAT SP4",
                "fecha_inicio": "2025-12-01",
                "fecha_fin": "2025-12-01",
                "sede": {"nombre": "Pileta UAT", "ciudad": "Buenos Aires", "pais": "Argentina"},
                "entidad_organizadora": {"nombre": "AIDA Argentina", "tipo": "Federación"},
            },
            headers=org_h,
        )
        torneo_id = assert_ok(resp, "crear torneo")["torneo_id"]
        log(f"torneo_id: {torneo_id}")

        # ── Disciplinas y juez ────────────────────────────────────────────────
        print("▸ Disciplinas")
        assert_ok(
            client.put(
                f"/torneos/{torneo_id}/disciplinas",
                json={"disciplinas": ["DNF", "STA"]},
                headers=org_h,
            ),
            "agregar disciplinas",
        )
        assert_ok(
            client.put(
                f"/torneos/{torneo_id}/disciplinas/DNF/juez",
                json={"juez_id": juez_id},
                headers=org_h,
            ),
            "asignar juez DNF",
        )
        assert_ok(
            client.put(
                f"/torneos/{torneo_id}/disciplinas/STA/juez",
                json={"juez_id": juez_id},
                headers=org_h,
            ),
            "asignar juez STA",
        )
        log("DNF + STA asignadas al juez")

        assert_ok(
            client.put(f"/torneos/{torneo_id}/abrir-inscripcion", headers=org_h),
            "abrir inscripcion",
        )

        # ── Atletas DNF ───────────────────────────────────────────────────────
        print("▸ Atletas DNF (e02-e06)")
        atletas_dnf_def = [
            ("e02", "Elena", "Marino", "SENIOR_FEMENINO", "e02@uat.test", 72),
            ("e03", "Tomás", "Buceo", "SENIOR_MASCULINO", "e03@uat.test", 68),
            ("e04", "Sofía", "Oceano", "SENIOR_FEMENINO", "e04@uat.test", 65),
            ("e05", "Rodrigo", "Profundo", "MASTER_MASCULINO", "e05@uat.test", 60),
            ("e06", "Camila", "Abismo", "SENIOR_FEMENINO", "e06@uat.test", 55),
        ]
        atleta_ids: dict[str, str] = {}
        atleta_ap_dnf: list[tuple[str, int]] = []
        for codigo, nombre, apellido, cat, email, ap in atletas_dnf_def:
            aid = str(uuid.uuid4())
            resp = client.post(
                "/registro/atletas",
                json={
                    "atleta_id": aid,
                    "nombre": nombre,
                    "apellido": apellido,
                    "email": email,
                    "fecha_nacimiento": "1990-01-01",
                    "categoria": cat,
                    "club": "Club UAT",
                },
                headers=admin_h,
            )
            data = assert_ok(resp, f"registrar atleta {codigo}")
            atleta_ids[codigo] = data.get("atleta_id", aid)
            atleta_ap_dnf.append((atleta_ids[codigo], ap))
            log(f"  {codigo}: {atleta_ids[codigo]}")

        print("▸ Atletas STA (t01-t03)")
        atletas_sta_def = [
            ("t01", "Lucía", "Apnea", "SENIOR_FEMENINO", "t01@uat.test", 300),
            ("t02", "Marcos", "Silencio", "SENIOR_MASCULINO", "t02@uat.test", 270),
            ("t03", "Valentina", "Fondo", "SENIOR_FEMENINO", "t03@uat.test", 240),
        ]
        atleta_ap_sta: list[tuple[str, int]] = []
        for codigo, nombre, apellido, cat, email, ap in atletas_sta_def:
            aid = str(uuid.uuid4())
            resp = client.post(
                "/registro/atletas",
                json={
                    "atleta_id": aid,
                    "nombre": nombre,
                    "apellido": apellido,
                    "email": email,
                    "fecha_nacimiento": "1992-01-01",
                    "categoria": cat,
                    "club": "Club UAT",
                },
                headers=admin_h,
            )
            data = assert_ok(resp, f"registrar atleta {codigo}")
            atleta_ids[codigo] = data.get("atleta_id", aid)
            atleta_ap_sta.append((atleta_ids[codigo], ap))
            log(f"  {codigo}: {atleta_ids[codigo]}")

        # ── Inscripciones ─────────────────────────────────────────────────────
        print("▸ Inscripciones")
        for codigo in ["e02", "e03", "e04", "e05", "e06"]:
            assert_ok(
                client.post(
                    "/registro/inscripciones",
                    json={
                        "atleta_id": atleta_ids[codigo],
                        "torneo_id": torneo_id,
                        "disciplinas": ["DNF"],
                    },
                    headers=admin_h,
                ),
                f"inscribir {codigo}",
            )
            log(f"  {codigo} → DNF")
        for codigo in ["t01", "t02", "t03"]:
            assert_ok(
                client.post(
                    "/registro/inscripciones",
                    json={
                        "atleta_id": atleta_ids[codigo],
                        "torneo_id": torneo_id,
                        "disciplinas": ["STA"],
                    },
                    headers=admin_h,
                ),
                f"inscribir {codigo}",
            )
            log(f"  {codigo} → STA")

        # ── Ciclo torneo → EJECUCION ──────────────────────────────────────────
        print("▸ Torneo → EJECUCION")
        assert_ok(
            client.put(f"/torneos/{torneo_id}/cerrar-inscripcion", headers=org_h),
            "cerrar inscripcion",
        )
        assert_ok(
            client.put(f"/torneos/{torneo_id}/iniciar-ejecucion", headers=org_h),
            "iniciar ejecucion",
        )
        log("estado: EJECUCION")

    # ── Competencias (application layer) ─────────────────────────────────────
    cid_dnf = uuid.uuid4()
    cid_sta = uuid.uuid4()

    print("▸ Competencia DNF (application layer)")
    asyncio.run(
        setup_competencia(
            competencia_id=cid_dnf,
            disciplina_str="DNF",
            intervalo_minutos=7,
            juez_id=juez_id,
            torneo_id=torneo_id,
            atletas=atleta_ap_dnf,
            unidad_str="metros",
        )
    )

    print("▸ Competencia STA (application layer)")
    asyncio.run(
        setup_competencia(
            competencia_id=cid_sta,
            disciplina_str="STA",
            intervalo_minutos=20,
            juez_id=juez_id,
            torneo_id=torneo_id,
            atletas=atleta_ap_sta,
            unidad_str="segundos",
        )
    )

    # ── Guardar IDs ───────────────────────────────────────────────────────────
    ids = {
        "torneo_id": torneo_id,
        "competencia_dnf_id": str(cid_dnf),
        "competencia_sta_id": str(cid_sta),
        "juez_id": juez_id,
        **{f"atleta_{k}": v for k, v in atleta_ids.items()},
    }
    IDS_PATH.write_text(json.dumps(ids, indent=2))

    print(f"\n✓ IDs guardados en {IDS_PATH}")
    print(json.dumps(ids, indent=2))
    print("\n=== Seed completado ===\n")


if __name__ == "__main__":
    main()
