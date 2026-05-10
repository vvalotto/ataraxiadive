"""
Seed UAT SP6 — datos de prueba para validación funcional manual (rol Juez).

Flujo corregido (precondiciones SP5+):
  1. Usuarios, torneo, disciplinas, inscripciones, APs via HTTP
  2. Cerrar inscripción (requiere APs completas)
  3. Preparar competencia: OT + APs en competencia + grilla confirmada (application layer)
  4. Iniciar ejecución del torneo via HTTP (requiere grilla confirmada)
  5. Iniciar competencia (application layer)

Crea:
  - 1 torneo "UAT SP6" en estado EJECUCION
  - 5 atletas DNF con AP declarada
  - 1 juez (juez@uat-sp4.test) asignado a DNF
  - 1 competencia DNF en EJECUCION con grilla confirmada
  - Guarda IDs en quality/reports/uat/SP6/uat_ids.json

Uso:  uv run python tests/uat/sp6/seed_sp6.py
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import sqlite3
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from uuid import UUID

import httpx

BASE = "http://localhost:8000"
IDS_PATH = Path("quality/reports/uat/SP6/uat_ids.json")

JUEZ_EMAIL = "juez@uat-sp4.test"
JUEZ_PASSWORD = "juezsp4uat2025"
ORG_EMAIL = "organizador@uat-sp4.test"
ORG_PASSWORD = "orgsp4uat2025"
ADMIN_EMAIL = "admin@uat-sp4.test"
ADMIN_PASSWORD = "adminsp4uat2025"

COMPETENCIA_DB = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")

ATLETAS_DEF = [
    ("a01", "Elena", "Marino", "SENIOR_FEMENINO", "a01@uat-sp6.test", 72),
    ("a02", "Tomás", "Buceo", "SENIOR_MASCULINO", "a02@uat-sp6.test", 68),
    ("a03", "Sofía", "Oceano", "SENIOR_FEMENINO", "a03@uat-sp6.test", 65),
    ("a04", "Rodrigo", "Profundo", "MASTER_MASCULINO", "a04@uat-sp6.test", 60),
    ("a05", "Camila", "Abismo", "SENIOR_FEMENINO", "a05@uat-sp6.test", 55),
]


REGISTRO_DB = os.getenv("REGISTRO_DB_PATH", "data/registro.db")
TORNEO_DB = os.getenv("TORNEO_DB_PATH", "data/torneo.db")
RESULTADOS_DB = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")

UAT_NOMBRE_PREFIX = "UAT SP6"
UAT_EMAIL_SUFFIX = "@uat-sp6.test"


def limpiar_datos_uat() -> None:
    """Elimina datos de corridas anteriores del seed para evitar duplicados."""

    with sqlite3.connect(TORNEO_DB) as con:
        torneo_ids = [
            row[0]
            for row in con.execute(
                "SELECT torneo_id FROM torneos WHERE nombre LIKE ?",
                (f"{UAT_NOMBRE_PREFIX}%",),
            )
        ]
        if torneo_ids:
            placeholders = ",".join("?" * len(torneo_ids))
            con.execute(f"DELETE FROM torneos WHERE torneo_id IN ({placeholders})", torneo_ids)
    log(f"torneos UAT eliminados: {len(torneo_ids)}")

    with sqlite3.connect(COMPETENCIA_DB) as con:
        if torneo_ids:
            placeholders = ",".join("?" * len(torneo_ids))
            comp_ids = [
                row[0]
                for row in con.execute(
                    f"SELECT competencia_id FROM competencias_por_torneo WHERE torneo_id IN ({placeholders})",
                    torneo_ids,
                )
            ]
            if comp_ids:
                p2 = ",".join("?" * len(comp_ids))
                con.execute(f"DELETE FROM events WHERE stream_id IN ({p2})", comp_ids)
                con.execute(
                    f"DELETE FROM competencias_por_torneo WHERE competencia_id IN ({p2})",
                    comp_ids,
                )
            log(f"competencias UAT eliminadas: {len(comp_ids) if torneo_ids else 0}")

    with sqlite3.connect(RESULTADOS_DB) as con:
        if torneo_ids:
            placeholders = ",".join("?" * len(torneo_ids))
            con.execute(f"DELETE FROM events WHERE stream_id IN ({placeholders})", torneo_ids)

    with sqlite3.connect(REGISTRO_DB) as con:
        atleta_ids = [
            row[0]
            for row in con.execute(
                "SELECT atleta_id FROM atletas WHERE email LIKE ?",
                (f"%{UAT_EMAIL_SUFFIX}",),
            )
        ]
        if atleta_ids:
            p3 = ",".join("?" * len(atleta_ids))
            con.execute(f"DELETE FROM inscripciones WHERE atleta_id IN ({p3})", atleta_ids)
            con.execute(f"DELETE FROM atletas WHERE atleta_id IN ({p3})", atleta_ids)
    log(f"atletas UAT eliminados: {len(atleta_ids)}")


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


async def preparar_grilla(
    competencia_id: UUID,
    torneo_id: str,
    juez_id: str,
    atletas: list[tuple[str, int]],
) -> None:
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
    from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
        SQLiteInscripcionRepository,
    )

    store = SQLiteEventStore(COMPETENCIA_DB)
    disciplina = Disciplina("DNF")
    unidad = UnidadMedida.Metros
    descriptor = DisciplinaDescriptorAdapter()
    stub = StubCompetenciaEstadoAdapter()
    proyeccion = SQLiteCompetenciasPorTorneo(COMPETENCIA_DB)
    inscripcion_repo = SQLiteInscripcionRepository()

    await ConfigurarIntervaloOTHandler(store, proyeccion).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            intervalo_minutos=7,
            configurado_por=juez_id,
            torneo_id=UUID(torneo_id),
        )
    )
    log("OT configurado (7 min)")

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
    log(f"{len(atletas)} APs registradas en competencia")

    ot_inicio = datetime(2026, 6, 1, 9, 0, 0, tzinfo=timezone.utc)
    ap_adapter = PerformancesAPAdapter(store, proyeccion, inscripcion_repo)
    await GenerarGrillaHandler(store, ap_adapter, descriptor).handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            ot_inicio=ot_inicio,
        )
    )
    log("Grilla generada")

    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(competencia_id=competencia_id, disciplina=disciplina)
    )
    log("Grilla confirmada")


async def iniciar_competencia_async(competencia_id: UUID, juez_id: str) -> None:
    from competencia.application.commands.iniciar_competencia import (
        IniciarCompetenciaCommand,
        IniciarCompetenciaHandler,
    )
    from competencia.domain.value_objects.disciplina import Disciplina
    from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

    store = SQLiteEventStore(COMPETENCIA_DB)
    await IniciarCompetenciaHandler(store).handle(
        IniciarCompetenciaCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina("DNF"),
            juez_id=juez_id,
        )
    )
    log("Competencia iniciada")


def main() -> None:
    print("\n=== Seed UAT SP6 ===\n")

    print("▸ Limpieza de datos anteriores")
    limpiar_datos_uat()

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
        juez_h = {"Authorization": f"Bearer {juez_token}"}

        # ── Torneo ────────────────────────────────────────────────────────────
        print("▸ Torneo")
        torneo_id = assert_ok(
            client.post(
                "/torneos",
                json={
                    "nombre": "UAT SP6 — Validación Funcional Juez",
                    "descripcion": "Torneo de prueba para validación manual SP6",
                    "fecha_inicio": "2026-06-01",
                    "fecha_fin": "2026-06-01",
                    "sede": {
                        "nombre": "Pileta UAT SP6",
                        "ciudad": "Buenos Aires",
                        "pais": "Argentina",
                    },
                    "entidad_organizadora": {"nombre": "AIDA Argentina", "tipo": "Federación"},
                    "grupos_etarios": ["SENIOR"],
                },
                headers=org_h,
            ),
            "crear torneo",
        )["torneo_id"]
        log(f"torneo_id: {torneo_id}")

        # ── Disciplinas y juez ────────────────────────────────────────────────
        print("▸ Disciplinas")
        assert_ok(
            client.put(
                f"/torneos/{torneo_id}/disciplinas",
                json={"disciplinas": ["DNF"]},
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
        log("DNF asignada al juez")

        assert_ok(
            client.put(f"/torneos/{torneo_id}/abrir-inscripcion", headers=org_h),
            "abrir inscripcion",
        )

        # ── Atletas ───────────────────────────────────────────────────────────
        print("▸ Atletas DNF (5 atletas)")
        atleta_ids: dict[str, str] = {}
        inscripcion_ids: dict[str, str] = {}
        atleta_ap_list: list[tuple[str, int]] = []

        for codigo, nombre, apellido, cat, email, ap in ATLETAS_DEF:
            aid = str(uuid.uuid4())
            data = assert_ok(
                client.post(
                    "/registro/atletas",
                    json={
                        "atleta_id": aid,
                        "nombre": nombre,
                        "apellido": apellido,
                        "email": email,
                        "fecha_nacimiento": "1990-01-01",
                        "categoria": cat,
                        "club": "Club UAT SP6",
                    },
                    headers=admin_h,
                ),
                f"registrar atleta {codigo}",
            )
            atleta_ids[codigo] = data.get("atleta_id", aid)
            atleta_ap_list.append((atleta_ids[codigo], ap))
            log(f"{codigo} ({nombre} {apellido}): {atleta_ids[codigo]}")

        # ── Inscripciones ─────────────────────────────────────────────────────
        print("▸ Inscripciones")
        for codigo in [d[0] for d in ATLETAS_DEF]:
            data = assert_ok(
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
            inscripcion_ids[codigo] = data["inscripcion_id"]
            log(f"{codigo} → DNF (inscripcion: {inscripcion_ids[codigo]})")

        # ── Declarar AP via HTTP (precondición para cerrar inscripción) ───────
        print("▸ Declarar AP (HTTP)")
        for codigo, _, _, _, _, ap in ATLETAS_DEF:
            assert_ok(
                client.put(
                    f"/registro/inscripciones/{inscripcion_ids[codigo]}/ap",
                    json={"disciplina": "DNF", "valor_ap": ap},
                    headers=juez_h,
                ),
                f"declarar AP {codigo}",
            )
            log(f"{codigo} → AP DNF = {ap}m")

        # ── Cerrar inscripción ────────────────────────────────────────────────
        print("▸ Cerrar inscripción")
        assert_ok(
            client.put(f"/torneos/{torneo_id}/cerrar-inscripcion", headers=org_h),
            "cerrar inscripcion",
        )
        log("estado: PREPARACION")

    # ── Preparar competencia: OT + APs + grilla confirmada ───────────────────
    cid_dnf = uuid.uuid4()
    print("▸ Preparar competencia DNF (application layer)")
    asyncio.run(preparar_grilla(cid_dnf, torneo_id, juez_id, atleta_ap_list))

    with httpx.Client(base_url=BASE, timeout=15) as client:
        org_token = get_or_create_usuario(client, ORG_EMAIL, ORG_PASSWORD, "ORGANIZADOR")
        org_h = {"Authorization": f"Bearer {org_token}"}

        # ── Asignar juez a cada entrada de la grilla ──────────────────────────
        print("▸ Asignar juez a performances de la grilla")
        resp = client.get(
            f"/competencia/{cid_dnf}/grilla",
            params={"disciplina": "DNF"},
        )
        assert_ok(resp, "obtener grilla")
        entradas = resp.json()
        for entrada in entradas:
            assert_ok(
                client.put(
                    f"/competencia/{cid_dnf}/grilla/{entrada['performance_id']}/juez",
                    json={"disciplina": "DNF", "juez_id": juez_id},
                    headers=org_h,
                ),
                f"asignar juez a performance {entrada['performance_id']}",
            )
        log(f"{len(entradas)} performances con juez asignado")

        # ── Iniciar ejecución del torneo (grilla ya confirmada + jueces) ──────
        print("▸ Torneo → EJECUCION")
        assert_ok(
            client.put(f"/torneos/{torneo_id}/iniciar-ejecucion", headers=org_h),
            "iniciar ejecucion",
        )
        log("estado: EJECUCION")

    # ── Guardar IDs ───────────────────────────────────────────────────────────
    ids = {
        "torneo_id": torneo_id,
        "competencia_dnf_id": str(cid_dnf),
        "juez_id": juez_id,
        "juez_email": JUEZ_EMAIL,
        "juez_password": JUEZ_PASSWORD,
        **{f"atleta_{k}": v for k, v in atleta_ids.items()},
        **{f"inscripcion_{k}": v for k, v in inscripcion_ids.items()},
    }
    IDS_PATH.write_text(json.dumps(ids, indent=2))

    print(f"\n✓ IDs guardados en {IDS_PATH}")
    print(json.dumps(ids, indent=2))
    print("\n=== Seed completado ===")
    print(f"\n🔑 Juez: {JUEZ_EMAIL} / {JUEZ_PASSWORD}")
    print("\n📋 Grilla DNF:")
    for _, nombre, apellido, _, _, ap in ATLETAS_DEF:
        print(f"   {nombre} {apellido}: AP={ap}m")
    print()


if __name__ == "__main__":
    main()
