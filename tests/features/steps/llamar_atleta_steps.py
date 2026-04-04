"""Step definitions BDD — US-1.2.2: Llamar Atleta.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""

from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.llamar_atleta import (
    CompetenciaNoEnEjecucion,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
    PerformanceNoEncontrada,
)
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.domain.aggregates.performance import EstadoInvalidoParaLlamar
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

scenarios("../US-1.2.2-llamar-atleta.feature")

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
    db_path = f"{tmp_path}/bdd_llamar.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


# ── Fixture de contexto por escenario ─────────────────────────────────────────


@pytest.fixture
def ctx(tmp_path: pytest.TempPathFactory) -> dict:  # type: ignore[type-arg]
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


@given(parsers.parse('una competencia activa con id "{cid}" en estado "EnEjecucion"'))
def step_competencia_activa(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["competencia_id"] = uuid4()


@given(parsers.parse('un participante con id "{pid}"'))
def step_participante(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["participante_id"] = uuid4()


@given(parsers.parse('la disciplina "{disciplina}"'))
def step_disciplina(ctx: dict, disciplina: str) -> None:  # type: ignore[type-arg]
    ctx["disciplina"] = Disciplina(disciplina)


@given('la performance del participante está en estado "AnunciadaAP"')
def step_performance_anunciada_ap(ctx: dict) -> None:  # type: ignore[type-arg]
    """Registra un AP para poner la performance en AnunciadaAP."""
    handler = RegistrarAPHandler(
        ctx["event_store"], ctx["estado_port"], DisciplinaDescriptorAdapter()
    )
    cmd = RegistrarAPCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        valor_ap=Decimal("330"),
        unidad=UnidadMedida.Segundos,
    )
    asyncio.run(handler.handle(cmd))


# ── Given (específicos de escenario) ──────────────────────────────────────────


@given('la competencia está en estado "EnEjecucion"')
def step_competencia_en_ejecucion(ctx: dict) -> None:  # type: ignore[type-arg]
    pass  # stub retorna True por defecto


@given('la performance del participante está en estado "Llamada"')
def step_performance_ya_llamada(ctx: dict) -> None:  # type: ignore[type-arg]
    """Llama al atleta (AP ya registrado por el Background) para dejar estado Llamada."""
    handler_llamar = LlamarAtletaHandler(ctx["event_store"], ctx["estado_port"])
    cmd_llamar = LlamarAtletaCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        ot_programado=datetime(2026, 3, 22, 9, 0, 0),
        posicion_grilla=1,
    )
    asyncio.run(handler_llamar.handle(cmd_llamar))


@given('la competencia NO está en estado "EnEjecucion"')
def step_competencia_no_en_ejecucion(ctx: dict) -> None:  # type: ignore[type-arg]
    stub = AsyncMock(spec=StubCompetenciaEstadoAdapter)
    stub.is_en_ejecucion.return_value = False
    ctx["estado_port"] = stub


# ── When ──────────────────────────────────────────────────────────────────────


def _ejecutar_llamar(ctx: dict, ot_str: str, posicion: int) -> None:  # type: ignore[type-arg]
    handler = LlamarAtletaHandler(ctx["event_store"], ctx["estado_port"])
    cmd = LlamarAtletaCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        ot_programado=datetime.fromisoformat(ot_str),
        posicion_grilla=posicion,
    )
    try:
        ctx["result"] = asyncio.run(handler.handle(cmd))
        ctx["ot_str"] = ot_str
        ctx["posicion_grilla"] = posicion
    except Exception as exc:
        ctx["error"] = exc


@when(
    parsers.parse(
        'el sistema llama al atleta con ot_programado "{ot}" y posicion_grilla {posicion:d}'
    )
)
def step_llamar_atleta(ctx: dict, ot: str, posicion: int) -> None:  # type: ignore[type-arg]
    _ejecutar_llamar(ctx, ot, posicion)


@when(
    parsers.parse(
        'el sistema intenta llamar al atleta con ot_programado "{ot}" y posicion_grilla {posicion:d}'
    )
)
def step_intentar_llamar_atleta(ctx: dict, ot: str, posicion: int) -> None:  # type: ignore[type-arg]
    _ejecutar_llamar(ctx, ot, posicion)


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('la performance pasa al estado "{estado}"'))
def step_estado_llamada(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
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


@then(parsers.parse('el evento contiene posicion_grilla {posicion:d} y ot_programado "{ot}"'))
def step_payload_correcto(ctx: dict, posicion: int, ot: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    llamado = next(e for e in events if e["event_type"] == "AtletaLlamado")
    payload = llamado["payload"]
    assert payload["posicion_grilla"] == posicion
    assert payload["ot_programado"] == ot


@then(parsers.parse('el sistema rechaza la operación con error "{error_type}"'))
def step_error_esperado(ctx: dict, error_type: str) -> None:  # type: ignore[type-arg]
    error_map = {
        "EstadoInvalidoParaLlamar": EstadoInvalidoParaLlamar,
        "CompetenciaNoEnEjecucion": CompetenciaNoEnEjecucion,
        "PerformanceNoEncontrada": PerformanceNoEncontrada,
    }
    assert ctx["error"] is not None, "Se esperaba un error pero no hubo ninguno"
    expected = error_map[error_type]
    assert isinstance(
        ctx["error"], expected
    ), f"Error esperado: {error_type}, obtenido: {type(ctx['error']).__name__}"
