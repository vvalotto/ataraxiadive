"""Step definitions BDD — US-2.1.1: Configurar Intervalo OT.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""
from __future__ import annotations

import asyncio
from uuid import UUID

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
    _build_stream_id,
)
from competencia.domain.exceptions import GrillaYaConfirmada
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.intervalo_disciplina import IntervaloInvalido
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

scenarios("../US-2.1.1-configurar-intervalo-ot.feature")

_CREATE_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""

_COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
_CONFIGURADO_POR = "organizador-01"


def _make_event_store(tmp_path: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_test_us211.db"
    asyncio.run(_create_db(db_path))
    return SQLiteEventStore(db_path)


async def _create_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


# ── Context ───────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: object) -> dict:
    return {
        "event_store": _make_event_store(str(tmp_path)),
        "competencia_id": _COMPETENCIA_ID,
        "disciplina": Disciplina.STA,
        "raised_exception": None,
        "intervalo_configurado": None,
    }


# ── Given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('una competencia con id "{competencia_id}" en estado "Preparacion"'))
def dada_competencia_en_preparacion(context: dict, competencia_id: str) -> None:
    # El estado Preparacion es el inicial — no requiere persistir eventos previos.
    pass


@given(parsers.parse('la disciplina es "{disciplina}"'))
def dada_disciplina(context: dict, disciplina: str) -> None:
    context["disciplina"] = Disciplina(disciplina)


@given("no existe un intervalo previo configurado")
def sin_intervalo_previo(context: dict) -> None:
    # El stream está vacío por defecto — no requiere acción.
    pass


@given(parsers.parse("ya existe un IntervaloOTConfigurado de {minutos:d} minutos"))
def dado_intervalo_previo(context: dict, minutos: int) -> None:
    cmd = ConfigurarIntervaloOTCommand(
        competencia_id=context["competencia_id"],
        disciplina=context["disciplina"],
        intervalo_minutos=minutos,
        configurado_por=_CONFIGURADO_POR,
    )
    handler = ConfigurarIntervaloOTHandler(context["event_store"])
    asyncio.run(handler.handle(cmd))


@given("la grilla ya fue confirmada para esta competencia")
def dada_grilla_confirmada(context: dict) -> None:
    stream_id = _build_stream_id(context["competencia_id"])

    async def _seed() -> None:
        await context["event_store"].append(
            stream_id=stream_id,
            event_type="GrillaConfirmada",
            payload={"competencia_id": str(context["competencia_id"])},
        )

    asyncio.run(_seed())


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse("el organizador configura el intervalo en {minutos:d} minutos"))
def cuando_configura_intervalo(context: dict, minutos: int) -> None:
    cmd = ConfigurarIntervaloOTCommand(
        competencia_id=context["competencia_id"],
        disciplina=context["disciplina"],
        intervalo_minutos=minutos,
        configurado_por=_CONFIGURADO_POR,
    )
    handler = ConfigurarIntervaloOTHandler(context["event_store"])
    try:
        asyncio.run(handler.handle(cmd))
        context["intervalo_configurado"] = minutos
    except (IntervaloInvalido, GrillaYaConfirmada) as exc:
        context["raised_exception"] = exc


@when(parsers.parse("el organizador reconfigura el intervalo a {minutos:d} minutos"))
def cuando_reconfigura_intervalo(context: dict, minutos: int) -> None:
    cuando_configura_intervalo(context, minutos)


@when(parsers.parse("el organizador intenta configurar el intervalo en {minutos:d} minutos"))
def cuando_intenta_configurar(context: dict, minutos: int) -> None:
    cuando_configura_intervalo(context, minutos)


@when("el organizador intenta reconfigurar el intervalo")
def cuando_intenta_reconfigurar(context: dict) -> None:
    cuando_configura_intervalo(context, 9)


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("el intervalo queda registrado en {minutos:d} minutos"))
def entonces_intervalo_registrado(context: dict, minutos: int) -> None:
    stream_id = _build_stream_id(context["competencia_id"])
    events = asyncio.run(context["event_store"].load(stream_id))
    last = events[-1]
    assert last["event_type"] == "IntervaloOTConfigurado"
    assert last["payload"]["intervalo_minutos"] == minutos


@then("el evento IntervaloOTConfigurado persiste en el stream")
def entonces_evento_persiste(context: dict) -> None:
    stream_id = _build_stream_id(context["competencia_id"])
    events = asyncio.run(context["event_store"].load(stream_id))
    assert any(e["event_type"] == "IntervaloOTConfigurado" for e in events)


@then(parsers.parse('la competencia sigue en estado "Preparacion"'))
def entonces_estado_preparacion(context: dict) -> None:
    # El estado se deriva del stream — sin eventos de transición, sigue Preparacion.
    stream_id = _build_stream_id(context["competencia_id"])
    events = asyncio.run(context["event_store"].load(stream_id))
    from competencia.domain.aggregates.competencia import Competencia
    c = Competencia.reconstitute(context["competencia_id"], context["disciplina"], events)
    assert c.estado == EstadoCompetencia.Preparacion


@then(parsers.parse("el nuevo IntervaloOTConfigurado persiste con valor {minutos:d}"))
def entonces_nuevo_evento_persiste(context: dict, minutos: int) -> None:
    entonces_intervalo_registrado(context, minutos)


@then(parsers.parse("el intervalo activo de la competencia es {minutos:d} minutos"))
def entonces_intervalo_activo(context: dict, minutos: int) -> None:
    stream_id = _build_stream_id(context["competencia_id"])
    events = asyncio.run(context["event_store"].load(stream_id))
    from competencia.domain.aggregates.competencia import Competencia
    c = Competencia.reconstitute(context["competencia_id"], context["disciplina"], events)
    assert c.intervalo is not None
    assert c.intervalo.minutos == minutos


@then(parsers.parse('el sistema rechaza la operación con error "{error_type}"'))
def entonces_rechaza_con_error(context: dict, error_type: str) -> None:
    assert context["raised_exception"] is not None, "Se esperaba una excepción pero no se lanzó"
    exc_name = type(context["raised_exception"]).__name__
    assert exc_name == error_type, f"Esperado {error_type}, recibido {exc_name}"
