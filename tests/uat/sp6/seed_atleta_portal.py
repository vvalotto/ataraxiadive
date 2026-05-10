"""
Seed UAT SP6 — validación portal atleta (INC-6.3).

Escenarios que cubre:

  A) Homepage atleta (US-6.3.1):
     - Atleta inscripto en torneo EN EJECUCION con OT asignado
     - Dos disciplinas (DNF + STA) con OTs en distinto orden → verificar sort

  B) Wizard inscripción (US-6.3.2):
     - Torneo en INSCRIPCION abierta para que el atleta pueda inscribirse
     - El wizard debe permitir declarar AP inline y subir adjuntos

Credenciales:
  Atleta:      atleta@uat-atleta.test  / atletauat2026
  Organizador: org@uat-atleta.test     / orguat2026
  Juez:        juez@uat-atleta.test    / juezuat2026

Uso:  uv run python tests/uat/sp6/seed_atleta_portal.py
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

sys.path.insert(0, "src")

BASE = "http://localhost:8000"
IDS_PATH = Path("quality/reports/uat/SP6/uat_atleta_ids.json")

ATLETA_EMAIL = "atleta@uat-atleta.test"
ATLETA_PASSWORD = "AtletaUat2026!"
ORG_EMAIL = "org@uat-atleta.test"
ORG_PASSWORD = "OrgUat2026!"
JUEZ_EMAIL = "juez@uat-atleta.test"
JUEZ_PASSWORD = "JuezUat2026!"
ADMIN_EMAIL = "admin@uat-atleta.test"
ADMIN_PASSWORD = "AdminUat2026!"

COMPETENCIA_DB = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")


async def crear_admin_directo(email: str, password: str) -> None:
    import uuid as _uuid
    from identidad.domain.aggregates.usuario import Usuario
    from identidad.domain.value_objects.rol import Rol
    from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
    from identidad.infrastructure.repositories.sqlite_usuario_repository import (
        SQLiteUsuarioRepository,
    )

    repo = SQLiteUsuarioRepository()
    existente = await repo.find_by_email(email)
    if existente is not None:
        log(f"admin existente: {email}")
        return
    hasher = BcryptPasswordHasher()
    usuario = Usuario(
        usuario_id=_uuid.uuid4(),
        nombre="Admin",
        apellido="UAT",
        email=email,
        password_hash=hasher.hash(password),
        rol=Rol.ADMIN,
    )
    await repo.save(usuario)
    log(f"admin creado: {email}")


def log(msg: str) -> None:
    print(f"  {msg}")


def assert_ok(resp: httpx.Response, context: str) -> dict:
    if resp.status_code not in (200, 201, 204):
        print(f"\n✗ ERROR en {context}: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)
    return resp.json() if resp.content else {}


def get_or_create_usuario(
    client: httpx.Client,
    email: str,
    password: str,
    rol: str,
    nombre: str = "UAT",
    apellido: str = "Test",
) -> str:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    if resp.status_code == 200:
        log(f"usuario existente: {email}")
        return resp.json()["access_token"]
    resp = client.post(
        "/auth/registro",
        json={
            "email": email,
            "password": password,
            "rol": rol,
            "nombre": nombre,
            "apellido": apellido,
        },
    )
    assert_ok(resp, f"registro {email}")
    resp = client.post("/auth/login", json={"email": email, "password": password})
    log(f"usuario creado: {email}")
    return assert_ok(resp, f"login {email}")["access_token"]


def decode_sub(token: str) -> str:
    payload = token.split(".")[1]
    payload += "==" * ((4 - len(payload) % 4) % 4)
    return json.loads(base64.b64decode(payload))["sub"]


async def preparar_grilla_disciplina(
    competencia_id: UUID,
    torneo_id: str,
    juez_id: str,
    disciplina_cod: str,
    atletas: list[tuple[str, int]],
    ot_inicio: datetime,
    intervalo_minutos: int = 7,
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
    disciplina = Disciplina(disciplina_cod)
    unidad = UnidadMedida.Metros if disciplina_cod != "STA" else UnidadMedida.Segundos
    descriptor = DisciplinaDescriptorAdapter()
    stub = StubCompetenciaEstadoAdapter()
    proyeccion = SQLiteCompetenciasPorTorneo(COMPETENCIA_DB)
    inscripcion_repo = SQLiteInscripcionRepository()

    await ConfigurarIntervaloOTHandler(store, proyeccion).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            intervalo_minutos=intervalo_minutos,
            configurado_por=juez_id,
            torneo_id=UUID(torneo_id),
        )
    )

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

    ap_adapter = PerformancesAPAdapter(store, proyeccion, inscripcion_repo)
    await GenerarGrillaHandler(store, ap_adapter, descriptor).handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            ot_inicio=ot_inicio,
        )
    )
    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(competencia_id=competencia_id, disciplina=disciplina)
    )
    log(f"Grilla {disciplina_cod} confirmada")


async def iniciar_competencia_async(
    competencia_id: UUID, disciplina_cod: str, juez_id: str
) -> None:
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
            disciplina=Disciplina(disciplina_cod),
            juez_id=juez_id,
        )
    )
    log(f"Competencia {disciplina_cod} iniciada")


def main() -> None:
    print("\n=== Seed UAT SP6 — Portal Atleta ===\n")

    IDS_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Crear admin por application layer (no permitido en auto-registro HTTP)
    print("▸ Admin (application layer)")
    asyncio.run(crear_admin_directo(ADMIN_EMAIL, ADMIN_PASSWORD))

    with httpx.Client(base_url=BASE, timeout=15) as client:

        # ── Usuarios ──────────────────────────────────────────────────────────
        print("▸ Usuarios")
        org_token = get_or_create_usuario(
            client, ORG_EMAIL, ORG_PASSWORD, "ORGANIZADOR", "Org", "UAT"
        )
        juez_token = get_or_create_usuario(client, JUEZ_EMAIL, JUEZ_PASSWORD, "JUEZ", "Juez", "UAT")
        atleta_token = get_or_create_usuario(
            client, ATLETA_EMAIL, ATLETA_PASSWORD, "ATLETA", "Valentina", "Costas"
        )
        admin_token = get_or_create_usuario(
            client, ADMIN_EMAIL, ADMIN_PASSWORD, "ADMIN", "Admin", "UAT"
        )

        org_id = decode_sub(org_token)
        juez_id = decode_sub(juez_token)
        atleta_user_id = decode_sub(atleta_token)

        log(f"org_id:    {org_id}")
        log(f"juez_id:   {juez_id}")
        log(f"atleta_user_id: {atleta_user_id}")

        org_h = {"Authorization": f"Bearer {org_token}"}
        admin_h = {"Authorization": f"Bearer {admin_token}"}
        atleta_h = {"Authorization": f"Bearer {atleta_token}"}

        # ── Atleta en registro ─────────────────────────────────────────────────
        print("▸ Atleta (registro BC)")
        me_resp = client.get("/registro/atletas/me", headers=atleta_h)
        if me_resp.status_code == 200:
            atleta_registro_id = me_resp.json()["atleta_id"]
            log(f"atleta existente: {atleta_registro_id}")
        else:
            atleta_registro_id = str(uuid.uuid4())
            assert_ok(
                client.post(
                    "/registro/atletas",
                    json={
                        "atleta_id": atleta_registro_id,
                        "nombre": "Valentina",
                        "apellido": "Costas",
                        "email": ATLETA_EMAIL,
                        "fecha_nacimiento": "1995-03-15",
                        "categoria": "SENIOR_FEMENINO",
                        "club": "Club Apnea BsAs",
                        "brevet": "FAAS-2024-001",
                    },
                    headers=admin_h,
                ),
                "registrar atleta",
            )
            log(f"atleta_registro_id: {atleta_registro_id}")

        # ── Torneo A: EN EJECUCION (homepage + disciplinas ordenadas) ─────────
        print("▸ Torneo A — EJECUCION (escenario homepage US-6.3.1)")
        torneo_a_id = assert_ok(
            client.post(
                "/torneos",
                json={
                    "nombre": "Copa Apnea Indoor BsAs 2026",
                    "descripcion": "Validación portal atleta — torneo en ejecución",
                    "fecha_inicio": "2026-06-15",
                    "fecha_fin": "2026-06-15",
                    "sede": {
                        "nombre": "Natatorio Municipal",
                        "ciudad": "Buenos Aires",
                        "pais": "Argentina",
                    },
                    "entidad_organizadora": {"nombre": "FAAS", "tipo": "Federación"},
                    "grupos_etarios": ["SENIOR"],
                },
                headers=org_h,
            ),
            "crear torneo A",
        )["torneo_id"]
        log(f"torneo_a_id: {torneo_a_id}")

        # Disciplinas: DNF + STA en una sola llamada (PUT reemplaza el set completo)
        assert_ok(
            client.put(
                f"/torneos/{torneo_a_id}/disciplinas",
                json={"disciplinas": ["DNF", "STA"]},
                headers=org_h,
            ),
            "agregar disciplinas torneo A",
        )
        for disc in ["DNF", "STA"]:
            assert_ok(
                client.put(
                    f"/torneos/{torneo_a_id}/disciplinas/{disc}/juez",
                    json={"juez_id": juez_id},
                    headers=org_h,
                ),
                f"asignar juez {disc}",
            )
        log("DNF + STA con juez asignado")

        assert_ok(
            client.put(f"/torneos/{torneo_a_id}/abrir-inscripcion", headers=org_h),
            "abrir inscripcion A",
        )

        # Atleta + 3 competidores más para tener grilla
        otros_atletas = []
        for i, (nombre, apellido, cat, ap_dnf, ap_sta) in enumerate(
            [
                ("Lucía", "Fondos", "SENIOR_FEMENINO", 60, 240),
                ("Marco", "Pelágico", "SENIOR_MASCULINO", 75, 300),
                ("Daniela", "Abismo", "SENIOR_FEMENINO", 55, 210),
            ]
        ):
            aid = str(uuid.uuid4())
            email = f"comp{i+1}@uat-atleta.test"
            assert_ok(
                client.post(
                    "/registro/atletas",
                    json={
                        "atleta_id": aid,
                        "nombre": nombre,
                        "apellido": apellido,
                        "email": email,
                        "fecha_nacimiento": "1992-05-01",
                        "categoria": cat,
                        "club": "Club UAT",
                    },
                    headers=admin_h,
                ),
                f"registrar comp{i+1}",
            )
            otros_atletas.append({"id": aid, "ap_dnf": ap_dnf, "ap_sta": ap_sta})
            log(f"comp{i+1}: {nombre} {apellido} ({aid})")

        # Inscribir a todos (atleta principal + 3 competidores) en DNF + STA
        inscripcion_a_id = None
        todos = [(atleta_registro_id, 65, 260)] + [
            (a["id"], a["ap_dnf"], a["ap_sta"]) for a in otros_atletas
        ]
        for aid, ap_dnf, ap_sta in todos:
            insc = assert_ok(
                client.post(
                    "/registro/inscripciones",
                    json={
                        "atleta_id": aid,
                        "torneo_id": torneo_a_id,
                        "disciplinas": ["DNF", "STA"],
                    },
                    headers=admin_h,
                ),
                f"inscribir {aid}",
            )
            if aid == atleta_registro_id:
                inscripcion_a_id = insc["inscripcion_id"]
            # Declarar APs
            for disc, ap in [("DNF", ap_dnf), ("STA", ap_sta)]:
                assert_ok(
                    client.put(
                        f"/registro/inscripciones/{insc['inscripcion_id']}/ap",
                        json={"disciplina": disc, "valor_ap": ap},
                        headers=admin_h,
                    ),
                    f"AP {disc} {aid}",
                )
        log(f"4 atletas inscriptos en DNF + STA, APs declarados")
        log(f"inscripcion atleta principal: {inscripcion_a_id}")

        assert_ok(
            client.put(f"/torneos/{torneo_a_id}/cerrar-inscripcion", headers=org_h),
            "cerrar inscripcion A",
        )
        log("estado torneo A: PREPARACION")

    # ── Grillas DNF + STA ──────────────────────────────────────────────────────
    cid_dnf = uuid.uuid4()
    cid_sta = uuid.uuid4()

    print("▸ Preparar grillas (application layer)")
    atleta_ap_dnf = [(a[0], a[1]) for a in todos]
    atleta_ap_sta = [(a[0], a[2]) for a in todos]
    dnf_rps = {todos[0][0]: 62, todos[1][0]: 58, todos[2][0]: 72, todos[3][0]: 50}

    # DNF: OT empieza a las 09:00
    asyncio.run(
        preparar_grilla_disciplina(
            cid_dnf,
            torneo_a_id,
            juez_id,
            "DNF",
            atleta_ap_dnf,
            ot_inicio=datetime(2026, 6, 15, 9, 0, 0, tzinfo=timezone.utc),
        )
    )
    # STA: OT empieza a las 14:00 (POSTERIOR a DNF → verificar sort en homepage)
    asyncio.run(
        preparar_grilla_disciplina(
            cid_sta,
            torneo_a_id,
            juez_id,
            "STA",
            atleta_ap_sta,
            ot_inicio=datetime(2026, 6, 15, 14, 0, 0, tzinfo=timezone.utc),
            intervalo_minutos=10,
        )
    )

    print("▸ DNF — iniciar competencia (application layer)")
    asyncio.run(iniciar_competencia_async(cid_dnf, "DNF", juez_id))

    with httpx.Client(base_url=BASE, timeout=15) as client:
        org_token = get_or_create_usuario(client, ORG_EMAIL, ORG_PASSWORD, "ORGANIZADOR")
        juez_token = get_or_create_usuario(client, JUEZ_EMAIL, JUEZ_PASSWORD, "JUEZ")
        org_h = {"Authorization": f"Bearer {org_token}"}
        juez_h = {"Authorization": f"Bearer {juez_token}"}

        print("▸ Asignar juez a performances")
        for cid, disc in [(cid_dnf, "DNF"), (cid_sta, "STA")]:
            resp = client.get(f"/competencia/{cid}/grilla", params={"disciplina": disc})
            assert_ok(resp, f"grilla {disc}")
            for entrada in resp.json():
                assert_ok(
                    client.put(
                        f"/competencia/{cid}/grilla/{entrada['performance_id']}/juez",
                        json={"disciplina": disc, "juez_id": juez_id},
                        headers=org_h,
                    ),
                    f"juez performance {disc}",
                )
        log("jueces asignados")

        print("▸ Torneo A → EJECUCION")
        assert_ok(
            client.put(f"/torneos/{torneo_a_id}/iniciar-ejecucion", headers=org_h),
            "iniciar ejecucion A",
        )
        log("estado: EJECUCION")

        # ── DNF: registrar resultados (todos tarjeta blanca) ──────────────────
        print("▸ DNF — registrar resultados y finalizar")
        grilla_dnf = assert_ok(
            client.get(f"/competencia/{cid_dnf}/grilla", params={"disciplina": "DNF"}),
            "grilla DNF",
        )
        for entrada in grilla_dnf:
            aid = entrada["atleta_id"]
            assert_ok(
                client.post(
                    f"/competencia/{cid_dnf}/llamar",
                    json={
                        "participante_id": aid,
                        "disciplina": "DNF",
                        "ot_programado": entrada["ot_programado"],
                        "posicion_grilla": entrada["posicion"],
                        "andarivel": entrada["andarivel"],
                    },
                    headers=juez_h,
                ),
                f"llamar DNF {aid}",
            )
            rp = dnf_rps.get(aid, 50)
            assert_ok(
                client.post(
                    f"/competencia/{cid_dnf}/registrar-resultado",
                    json={
                        "participante_id": aid,
                        "disciplina": "DNF",
                        "valor_rp": rp,
                        "unidad": "Metros",
                    },
                    headers=juez_h,
                ),
                f"resultado DNF {aid}",
            )
            assert_ok(
                client.post(
                    f"/competencia/{cid_dnf}/asignar-tarjeta",
                    json={"participante_id": aid, "disciplina": "DNF", "tipo": "Blanca"},
                    headers=juez_h,
                ),
                f"tarjeta DNF {aid}",
            )
        assert_ok(
            client.post(
                f"/competencia/{cid_dnf}/finalizar", json={"disciplina": "DNF"}, headers=org_h
            ),
            "finalizar DNF",
        )
        log("DNF finalizado — STA sin resultados (pendiente)")

        # ── Torneo B: INSCRIPCION ABIERTA (wizard US-6.3.2) ───────────────────
        print("▸ Torneo B — INSCRIPCION (escenario wizard US-6.3.2)")
        torneo_b_id = assert_ok(
            client.post(
                "/torneos",
                json={
                    "nombre": "Open Nacional Apnea 2026",
                    "descripcion": "Validación portal atleta — torneo con inscripción abierta",
                    "fecha_inicio": "2026-09-20",
                    "fecha_fin": "2026-09-21",
                    "sede": {
                        "nombre": "Pileta Olímpica Nacional",
                        "ciudad": "Córdoba",
                        "pais": "Argentina",
                    },
                    "entidad_organizadora": {"nombre": "FAAS", "tipo": "Federación"},
                    "grupos_etarios": ["JUNIOR", "SENIOR", "MASTER"],
                },
                headers=org_h,
            ),
            "crear torneo B",
        )["torneo_id"]
        log(f"torneo_b_id: {torneo_b_id}")

        assert_ok(
            client.put(
                f"/torneos/{torneo_b_id}/disciplinas",
                json={"disciplinas": ["DNF", "DYN", "STA"]},
                headers=org_h,
            ),
            "agregar disciplinas torneo B",
        )
        assert_ok(
            client.put(f"/torneos/{torneo_b_id}/abrir-inscripcion", headers=org_h),
            "abrir inscripcion B",
        )
        log("DNF + DYN + STA disponibles — inscripción abierta")

    # ── Guardar IDs ───────────────────────────────────────────────────────────
    ids = {
        "atleta_email": ATLETA_EMAIL,
        "atleta_password": ATLETA_PASSWORD,
        "org_email": ORG_EMAIL,
        "org_password": ORG_PASSWORD,
        "juez_email": JUEZ_EMAIL,
        "juez_password": JUEZ_PASSWORD,
        "atleta_registro_id": atleta_registro_id,
        "torneo_a_id": torneo_a_id,
        "torneo_a_nombre": "Copa Apnea Indoor BsAs 2026",
        "torneo_a_estado": "EJECUCION",
        "competencia_dnf_id": str(cid_dnf),
        "competencia_sta_id": str(cid_sta),
        "inscripcion_a_id": inscripcion_a_id,
        "torneo_b_id": torneo_b_id,
        "torneo_b_nombre": "Open Nacional Apnea 2026",
        "torneo_b_estado": "INSCRIPCION",
    }
    IDS_PATH.write_text(json.dumps(ids, indent=2))

    print(f"\n✓ IDs guardados en {IDS_PATH}")
    print("\n" + "=" * 50)
    print("🔑 CREDENCIALES")
    print(f"   Atleta:      {ATLETA_EMAIL} / {ATLETA_PASSWORD}")
    print(f"   Organizador: {ORG_EMAIL} / {ORG_PASSWORD}")
    print(f"   Juez:        {JUEZ_EMAIL} / {JUEZ_PASSWORD}")
    print("\n📋 ESCENARIOS DE PRUEBA")
    print("\n  A) Homepage — inicio atleta (US-6.3.1)")
    print(f"     Torneo: {ids['torneo_a_nombre']} [{ids['torneo_a_estado']}]")
    print("     → Verificar: indicador 'En línea' en header")
    print("     → Verificar: NO aparece 'Hola' antes del nombre")
    print("     → Verificar: DNF (09:00) aparece ANTES que STA (14:00) en la sección")
    print("\n  B) Wizard inscripción (US-6.3.2)")
    print(f"     Torneo: {ids['torneo_b_nombre']} [{ids['torneo_b_estado']}]")
    print("     → Verificar: al seleccionar DNF aparece input AP inline")
    print("     → Verificar: AP inválido ('abc') bloquea avance al paso 3")
    print("     → Verificar: certificado médico + comprobante se suben al backend")
    print("     → Verificar: AP queda guardado post-inscripción")
    print("\n=== Seed completado ===\n")


if __name__ == "__main__":
    main()
