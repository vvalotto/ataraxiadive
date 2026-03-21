"""Step definitions BDD — US-1.2.1: Registrar AP.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""
from __future__ import annotations

import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.registrar_ap import (
    APYaRegistrado,
    GrillaYaConfirmadaError,
    PlazoAPVencidoError,
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.value_objects.ap import ValorAPInvalido
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

# Enlaza todos los escenarios del feature file a este módulo
scenarios("../US-1.2.1-registrar-ap.feature")

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


def _make_event_store(tmp_path: str) -> SQLiteEventStore:
    """Crea un SQLiteEventStore síncrono para tests BDD."""
    db_path = f"{tmp_path}/bdd_test.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


# ── Fixture de contexto por escenario ─────────────────────────────────────────


@pytest.fixture
def ctx(tmp_path: pytest.TempPathFactory) -> dict:  # type: ignore[type-arg]
    """Contexto compartido entre steps del mismo escenario."""
    return {
        "competencia_id": uuid4(),
        "participante_id": uuid4(),
        "disciplina": Disciplina.STA,
        "event_store": _make_event_store(str(tmp_path)),
        "estado_port": StubCompetenciaEstadoAdapter(),
        "result": None,
        "error": None,
    }


# ── Background ────────────────────────────────────────────────────────────────


@given(parsers.parse('una competencia activa con id "{cid}"'))
def step_competencia(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["competencia_id"] = uuid4()


@given(parsers.parse('un participante con id "{pid}"'))
def step_participante(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["participante_id"] = uuid4()


@given(parsers.parse('la disciplina "{disciplina}"'))
def step_disciplina(ctx: dict, disciplina: str) -> None:  # type: ignore[type-arg]
    ctx["disciplina"] = Disciplina(disciplina)


# ── Given ─────────────────────────────────────────────────────────────────────


@given("no existe un AP previo del atleta para esta disciplina y competencia")
def step_sin_ap_previo(ctx: dict) -> None:  # type: ignore[type-arg]
    pass  # stream vacío por defecto


@given("el plazo de AP no ha vencido")
def step_plazo_activo(ctx: dict) -> None:  # type: ignore[type-arg]
    pass  # stub retorna False


@given("la grilla no está confirmada")
def step_grilla_no_confirmada(ctx: dict) -> None:  # type: ignore[type-arg]
    pass  # stub retorna False


@given("ya existe un AP del participante para esta disciplina y competencia")
def step_ap_existente(ctx: dict) -> None:  # type: ignore[type-arg]
    handler = RegistrarAPHandler(ctx["event_store"], ctx["estado_port"])
    cmd = RegistrarAPCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        valor_ap=Decimal("300"),
        unidad=UnidadMedida.Segundos,
    )
    asyncio.run(handler.handle(cmd))


@given("el plazo de AP ya venció para esta disciplina y competencia")
def step_plazo_vencido(ctx: dict) -> None:  # type: ignore[type-arg]
    stub = AsyncMock(spec=StubCompetenciaEstadoAdapter)
    stub.is_plazo_vencido.return_value = True
    stub.is_grilla_confirmada.return_value = False
    ctx["estado_port"] = stub


@given("la grilla ya fue confirmada para esta competencia")
def step_grilla_confirmada(ctx: dict) -> None:  # type: ignore[type-arg]
    stub = AsyncMock(spec=StubCompetenciaEstadoAdapter)
    stub.is_plazo_vencido.return_value = False
    stub.is_grilla_confirmada.return_value = True
    ctx["estado_port"] = stub


# ── When ──────────────────────────────────────────────────────────────────────


def _ejecutar_registrar_ap(ctx: dict, valor: str, unidad: str) -> None:  # type: ignore[type-arg]
    handler = RegistrarAPHandler(ctx["event_store"], ctx["estado_port"])
    cmd = RegistrarAPCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        valor_ap=Decimal(valor),
        unidad=UnidadMedida(unidad),
    )
    try:
        ctx["result"] = asyncio.run(handler.handle(cmd))
    except Exception as exc:
        ctx["error"] = exc


@when(parsers.parse('el atleta registra un AP de valor "{valor}" unidad "{unidad}"'))
def step_registrar_ap(ctx: dict, valor: str, unidad: str) -> None:  # type: ignore[type-arg]
    _ejecutar_registrar_ap(ctx, valor, unidad)


@when(parsers.parse('el atleta intenta registrar otro AP de valor "{valor}" unidad "{unidad}"'))
def step_intentar_registrar_ap(ctx: dict, valor: str, unidad: str) -> None:  # type: ignore[type-arg]
    _ejecutar_registrar_ap(ctx, valor, unidad)


@when(parsers.parse('el atleta intenta registrar un AP de valor "{valor}" unidad "{unidad}"'))
def step_intentar_registrar_ap_nuevo(ctx: dict, valor: str, unidad: str) -> None:  # type: ignore[type-arg]
    _ejecutar_registrar_ap(ctx, valor, unidad)


# ── Then ──────────────────────────────────────────────────────────────────────


@then("el AP queda registrado exitosamente")
def step_ap_registrado(ctx: dict) -> None:  # type: ignore[type-arg]
    assert ctx["error"] is None, f"Error inesperado: {ctx['error']}"
    assert ctx["result"] is not None


@then(parsers.parse('la performance queda en estado "{estado}"'))
def step_estado_performance(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    from competencia.domain.aggregates.performance import Performance

    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance(estado)


@then(parsers.parse('el evento "{event_type}" persiste en el event stream'))
def step_evento_en_stream(ctx: dict, event_type: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    assert any(e["event_type"] == event_type for e in events)


@then(parsers.parse('el sistema rechaza la operación con error "{error_type}"'))
def step_error_esperado(ctx: dict, error_type: str) -> None:  # type: ignore[type-arg]
    error_map = {
        "APYaRegistrado": APYaRegistrado,
        "ValorAPInvalido": ValorAPInvalido,
        "PlazoAPVencido": PlazoAPVencidoError,
        "GrillaYaConfirmada": GrillaYaConfirmadaError,
    }
    assert ctx["error"] is not None, "Se esperaba un error pero no hubo ninguno"
    expected = error_map[error_type]
    assert isinstance(ctx["error"], expected), (
        f"Error esperado: {error_type}, obtenido: {type(ctx['error']).__name__}"
    )
