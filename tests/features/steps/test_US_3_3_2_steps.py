"""Step definitions BDD — US-3.3.2: Flujo E2E Torneo-Registro-Competencia.

Patrón: handlers directos + asyncio.run() en steps síncronos.
Consistent con flujo_e2e_steps.py (US-1.4.2).
"""

from __future__ import annotations

import asyncio
import sqlite3
from datetime import date, datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest
from pytest_bdd import given, scenario, then, when

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
from competencia.application.queries.obtener_estado_competencia import (
    ObtenerEstadoCompetenciaHandler,
    ObtenerEstadoCompetenciaQuery,
)
from competencia.application.queries.obtener_grilla import (
    ObtenerGrillaHandler,
    ObtenerGrillaQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.competencia_estado_adapter import (
    CompetenciaEstadoAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import (
    PerformancesAPAdapter,
)
from registro.application.commands.inscribir_atleta import (
    InscribirAtletaCommand,
    InscribirAtletaHandler,
)
from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.acl.sqlite_torneo_consulta import SQLiteTorneoConsulta
from registro.infrastructure.repositories.sqlite_atleta_repository import (
    SQLiteAtletaRepository,
)
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina as SharedDisciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida
from torneo.application.commands.crear_torneo import CrearTorneoCommand, CrearTorneoHandler
from torneo.application.commands.transicionar_torneo import (
    AbrirInscripcionHandler,
    TransicionarTorneoCommand,
)
from torneo.infrastructure.repositories.sqlite_torneo_repository import (
    SQLiteTorneoRepository,
)

FEATURE = "../US-3.3.2-flujo-e2e-torneo-competencia.feature"

_CREATE_EVENTS_TABLE = """
    CREATE TABLE IF NOT EXISTS events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""

_OT_INICIO = datetime(2026, 9, 10, 9, 0, 0, tzinfo=timezone.utc)


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx(tmp_path: Any) -> dict[str, Any]:
    """Inicializa los 3 BCs con paths SQLite coordinados y estado compartido."""
    torneo_db = str(tmp_path / "torneo.db")
    registro_db = str(tmp_path / "registro.db")
    competencia_db = str(tmp_path / "competencia.db")

    # Event Store necesita DDL explícito
    conn = sqlite3.connect(competencia_db)
    conn.execute(_CREATE_EVENTS_TABLE)
    conn.commit()
    conn.close()

    return {
        "torneo_repo": SQLiteTorneoRepository(db_path=torneo_db),
        "atleta_repo": SQLiteAtletaRepository(db_path=registro_db),
        "inscripcion_repo": SQLiteInscripcionRepository(db_path=registro_db),
        "torneo_consulta": SQLiteTorneoConsulta(db_path=torneo_db),
        "event_store": SQLiteEventStore(db_path=competencia_db),
        "torneo_id": None,
        "atleta_id": None,
        "atleta_con_ap": None,
        "competencia_id": None,
        "grilla": None,
        "atletas_y_aps": [],
    }


# ── Scenarios ─────────────────────────────────────────────────────────────────


@scenario(FEATURE, "flujo completo inscripcion AP grilla")
def test_flujo_completo():
    pass


@scenario(FEATURE, "atleta sin AP no aparece en grilla")
def test_atleta_sin_ap():
    pass


@scenario(FEATURE, "multiples atletas ordenados por AP ascendente")
def test_orden_ap():
    pass


# ── Helpers async ─────────────────────────────────────────────────────────────


async def _crear_torneo_abierto(torneo_repo) -> UUID:
    cmd = CrearTorneoCommand(
        nombre="Copa E2E BDD 2026",
        descripcion="Torneo BDD E2E",
        fecha_inicio=date(2026, 9, 10),
        fecha_fin=date(2026, 9, 12),
        sede_nombre="Pileta Test",
        sede_ciudad="Buenos Aires",
        sede_pais="Argentina",
        entidad_nombre="FADA",
        entidad_tipo="FEDERACION",
    )
    torneo_id = await CrearTorneoHandler(torneo_repo).handle(cmd)
    await AbrirInscripcionHandler(torneo_repo).handle(TransicionarTorneoCommand(torneo_id))
    return torneo_id


async def _registrar_e_inscribir(
    atleta_repo,
    inscripcion_repo,
    torneo_consulta,
    torneo_id: UUID,
    nombre: str = "Juan",
    apellido: str = "Perez",
    email: str = "juan@test.com",
    atleta_id: UUID | None = None,
) -> UUID:
    if atleta_id is None:
        atleta_id = uuid4()
    await RegistrarAtletaHandler(atleta_repo).handle(
        RegistrarAtletaCommand(
            atleta_id=atleta_id,
            nombre=nombre,
            apellido=apellido,
            email=email,
            fecha_nacimiento=date(1990, 1, 15),
            categoria=Categoria.SENIOR_MASCULINO,
            club="Club Test",
        )
    )
    await InscribirAtletaHandler(inscripcion_repo, torneo_consulta).handle(
        InscribirAtletaCommand(
            atleta_id=atleta_id,
            torneo_id=torneo_id,
            disciplinas=frozenset({SharedDisciplina.STA}),
        )
    )
    return atleta_id


async def _ap(event_store, competencia_id: UUID, atleta_id: UUID, valor: int) -> None:
    estado_adapter = CompetenciaEstadoAdapter(event_store)
    descriptor_adapter = DisciplinaDescriptorAdapter()
    await RegistrarAPHandler(event_store, estado_adapter, descriptor_adapter).handle(
        RegistrarAPCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            participante_id=atleta_id,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Segundos,
        )
    )


async def _generar_y_confirmar(event_store, competencia_id: UUID) -> list:
    ap_adapter = PerformancesAPAdapter(event_store)
    descriptor_adapter = DisciplinaDescriptorAdapter()
    await GenerarGrillaHandler(event_store, ap_adapter, descriptor_adapter).handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            ot_inicio=_OT_INICIO,
        )
    )
    await ConfirmarGrillaHandler(event_store).handle(
        ConfirmarGrillaCommand(competencia_id=competencia_id, disciplina=Disciplina.STA)
    )
    return await ObtenerGrillaHandler(event_store).handle(
        ObtenerGrillaQuery(competencia_id=competencia_id, disciplina=Disciplina.STA)
    )


# ── Given steps ───────────────────────────────────────────────────────────────


@given("torneo abierto para inscripcion")
def torneo_abierto(ctx: dict[str, Any]) -> None:
    torneo_id = _run(_crear_torneo_abierto(ctx["torneo_repo"]))
    ctx["torneo_id"] = torneo_id


@given("atleta registrado e inscripto en disciplina STA")
def atleta_inscripto(ctx: dict[str, Any]) -> None:
    atleta_id = _run(
        _registrar_e_inscribir(
            ctx["atleta_repo"],
            ctx["inscripcion_repo"],
            ctx["torneo_consulta"],
            ctx["torneo_id"],
        )
    )
    ctx["atleta_id"] = atleta_id


@given("competencia STA configurada con torneo_id")
def competencia_configurada(ctx: dict[str, Any]) -> None:
    competencia_id = uuid4()

    async def _cfg():
        await ConfigurarIntervaloOTHandler(ctx["event_store"]).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=competencia_id,
                disciplina=Disciplina.STA,
                intervalo_minutos=5,
                configurado_por="organizador",
                torneo_id=ctx["torneo_id"],
            )
        )

    _run(_cfg())
    ctx["competencia_id"] = competencia_id


@given("dos atletas inscriptos solo uno registra AP")
def dos_atletas_uno_con_ap(ctx: dict[str, Any]) -> None:
    atleta_con_ap = _run(
        _registrar_e_inscribir(
            ctx["atleta_repo"],
            ctx["inscripcion_repo"],
            ctx["torneo_consulta"],
            ctx["torneo_id"],
            nombre="Con",
            apellido="AP",
            email="conap@test.com",
        )
    )
    _run(
        _registrar_e_inscribir(
            ctx["atleta_repo"],
            ctx["inscripcion_repo"],
            ctx["torneo_consulta"],
            ctx["torneo_id"],
            nombre="Sin",
            apellido="AP2",
            email="sinap@test.com",
        )
    )
    ctx["atleta_con_ap"] = atleta_con_ap


@given("tres atletas con APs de 360 300 y 240 segundos en STA")
def tres_atletas_con_aps(ctx: dict[str, Any]) -> None:
    atletas_y_aps = [(uuid4(), ap) for ap in [360, 300, 240]]
    for atleta_id, ap in atletas_y_aps:
        _run(
            _registrar_e_inscribir(
                ctx["atleta_repo"],
                ctx["inscripcion_repo"],
                ctx["torneo_consulta"],
                ctx["torneo_id"],
                nombre="Atleta",
                apellido=f"AP{ap}",
                email=f"atleta{ap}@test.com",
                atleta_id=atleta_id,
            )
        )
    ctx["atletas_y_aps"] = atletas_y_aps


# ── When steps ────────────────────────────────────────────────────────────────


@when("el atleta registra su AP en la competencia")
def atleta_registra_ap(ctx: dict[str, Any]) -> None:
    _run(_ap(ctx["event_store"], ctx["competencia_id"], ctx["atleta_id"], 360))


@when("se genera y confirma la grilla")
def generar_confirmar_grilla(ctx: dict[str, Any]) -> None:
    # Registrar AP del atleta_con_ap si aplica (escenario 2)
    if ctx.get("atleta_con_ap"):
        _run(_ap(ctx["event_store"], ctx["competencia_id"], ctx["atleta_con_ap"], 300))
    # Registrar APs de atletas_y_aps si aplica (escenario 3)
    for atleta_id, ap in ctx.get("atletas_y_aps", []):
        _run(_ap(ctx["event_store"], ctx["competencia_id"], atleta_id, ap))
    grilla = _run(_generar_y_confirmar(ctx["event_store"], ctx["competencia_id"]))
    ctx["grilla"] = grilla


# ── Then steps ────────────────────────────────────────────────────────────────


@then("la grilla contiene al atleta")
def grilla_contiene_atleta(ctx: dict[str, Any]) -> None:
    assert len(ctx["grilla"]) == 1
    assert ctx["grilla"][0].atleta_id == str(ctx["atleta_id"])


@then("la competencia referencia el torneo_id correcto")
def competencia_referencia_torneo(ctx: dict[str, Any]) -> None:
    async def _check():
        return await ObtenerEstadoCompetenciaHandler(ctx["event_store"]).handle(
            ObtenerEstadoCompetenciaQuery(
                competencia_id=ctx["competencia_id"], disciplina=Disciplina.STA
            )
        )

    estado = _run(_check())
    assert estado.torneo_id == ctx["torneo_id"]


@then("la grilla contiene solo el atleta con AP")
def grilla_contiene_solo_atleta_con_ap(ctx: dict[str, Any]) -> None:
    assert len(ctx["grilla"]) == 1
    assert ctx["grilla"][0].atleta_id == str(ctx["atleta_con_ap"])


@then("el orden de la grilla es 240 300 360 segundos")
def orden_grilla_ascendente(ctx: dict[str, Any]) -> None:
    grilla = ctx["grilla"]
    atletas_y_aps = ctx["atletas_y_aps"]
    assert len(grilla) == 3
    assert grilla[0].atleta_id == str(atletas_y_aps[2][0])  # 240s — posición 1
    assert grilla[1].atleta_id == str(atletas_y_aps[1][0])  # 300s — posición 2
    assert grilla[2].atleta_id == str(atletas_y_aps[0][0])  # 360s — posición 3
