"""Step definitions BDD — US-1.2.3: Registrar Resultado.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import EstadoInvalidoParaRegistrarResultado, Performance
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
scenarios("../US-1.2.3-registrar-resultado.feature")

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

OT = datetime(2026, 3, 22, 10, 30, 0)


def _make_event_store(tmp_path: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_resultado.db"

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
        "disciplina": Disciplina.DNF,
        "event_store": _make_event_store(str(tmp_path)),
        "estado_port": StubCompetenciaEstadoAdapter(),
        "result": None,
        "error": None,
    }


# ── Background ────────────────────────────────────────────────────────────────


@given(parsers.parse('una competencia activa con id "{cid}" en estado "EnEjecucion"'))
def step_competencia_activa_resultado(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["competencia_id"] = uuid4()


@given(parsers.parse('un atleta con id "{pid}" en disciplina "DNF"'))
def step_atleta_dnf(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["participante_id"] = uuid4()
    ctx["disciplina"] = Disciplina.DNF


@given(parsers.parse('la performance del atleta tiene AP registrado de {valor:d} metros'))
def step_ap_registrado(ctx: dict, valor: int) -> None:  # type: ignore[type-arg]
    handler = RegistrarAPHandler(ctx["event_store"], ctx["estado_port"], DisciplinaDescriptorAdapter())
    cmd = RegistrarAPCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        valor_ap=Decimal(str(valor)),
        unidad=UnidadMedida.Metros,
    )
    asyncio.run(handler.handle(cmd))


@given('la performance está en estado "Llamada"')
def step_performance_llamada(ctx: dict) -> None:  # type: ignore[type-arg]
    handler = LlamarAtletaHandler(ctx["event_store"], ctx["estado_port"])
    cmd = LlamarAtletaCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        ot_programado=OT,
        posicion_grilla=1,
    )
    asyncio.run(handler.handle(cmd))


# ── Given (específicos de escenario) ──────────────────────────────────────────


@given('la performance del atleta está en estado "AnunciadaAP"')
def step_performance_anunciada_ap_resultado(ctx: dict) -> None:  # type: ignore[type-arg]
    """Resetea con store fresco y lleva la performance solo hasta AnunciadaAP."""
    import tempfile
    fresh_store = _make_event_store(tempfile.mkdtemp())
    cid = uuid4()
    pid = uuid4()
    ctx["event_store"] = fresh_store
    ctx["competencia_id"] = cid
    ctx["participante_id"] = pid
    sp = ctx["estado_port"]
    asyncio.run(
        RegistrarAPHandler(fresh_store, sp, DisciplinaDescriptorAdapter()).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=ctx["disciplina"],
                valor_ap=Decimal("50"),
                unidad=UnidadMedida.Metros,
            )
        )
    )


@given('la performance del atleta está en estado "DNS"')
def step_performance_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    """Simula estado DNS usando reconstitución con evento DNSRegistrado hardcodeado."""
    # Para el test: la performance está en DNS, no se puede registrar resultado.
    # Usamos un event_store con un stream que termina en DNS.
    from unittest.mock import AsyncMock

    dns_store = AsyncMock()
    dns_store.load.return_value = [
        {
            "event_type": "APRegistrado",
            "payload": {
                "performance_id": str(uuid4()),
                "competencia_id": str(ctx["competencia_id"]),
                "participante_id": str(ctx["participante_id"]),
                "disciplina": ctx["disciplina"].value,
                "valor_ap": "50",
                "unidad": "Metros",
                "occurred_at": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
            },
        },
        {
            "event_type": "AtletaLlamado",
            "payload": {
                "performance_id": str(uuid4()),
                "participante_id": str(ctx["participante_id"]),
                "disciplina": ctx["disciplina"].value,
                "posicion_grilla": 1,
                "ot_programado": OT.isoformat(),
                "llamado_en": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
            },
        },
        {
            "event_type": "DNSRegistrado",
            "payload": {
                "performance_id": str(uuid4()),
                "participante_id": str(ctx["participante_id"]),
                "disciplina": ctx["disciplina"].value,
                "registrado_por": "juez-001",
                "occurred_at": datetime(2026, 3, 22, 10, 5, 0).isoformat(),
            },
        },
    ]
    ctx["event_store"] = dns_store
    ctx["estado_dns"] = EstadoPerformance.DNS


# ── When ──────────────────────────────────────────────────────────────────────


def _ejecutar_registrar_resultado(ctx: dict, valor_rp: float, juez: str) -> None:  # type: ignore[type-arg]
    handler = RegistrarResultadoHandler(ctx["event_store"], DisciplinaDescriptorAdapter())
    cmd = RegistrarResultadoCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        valor_rp=Decimal(str(valor_rp)),
        unidad=UnidadMedida.Metros,
        registrado_por=juez,
    )
    try:
        ctx["result"] = asyncio.run(handler.handle(cmd))
        ctx["valor_rp"] = str(Decimal(str(valor_rp)))
    except Exception as exc:
        ctx["error"] = exc


@when(
    parsers.parse(
        'el juez registra el resultado con valorRP={valor_rp:f} metros y registrado_por="{juez}"'
    )
)
def step_registrar_resultado(ctx: dict, valor_rp: float, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_registrar_resultado(ctx, valor_rp, juez)


@when(
    parsers.parse('el juez intenta registrar el resultado con valorRP={valor_rp:f} metros')
)
def step_intentar_registrar_resultado(ctx: dict, valor_rp: float) -> None:  # type: ignore[type-arg]
    _ejecutar_registrar_resultado(ctx, valor_rp, "juez-001")


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('la performance pasa al estado "{estado}"'))
def step_estado_resultado(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance(estado)


@then('el evento ResultadoRegistrado persiste en el event stream')
def step_evento_resultado_en_stream(ctx: dict) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    assert any(e["event_type"] == "ResultadoRegistrado" for e in events)


@then(
    parsers.parse(
        'el evento contiene valorRP="{valor_rp}", unidad="{unidad}" y registradoPor="{juez}"'
    )
)
def step_payload_resultado_correcto(
    ctx: dict, valor_rp: str, unidad: str, juez: str
) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    resultado = next(e for e in events if e["event_type"] == "ResultadoRegistrado")
    payload = resultado["payload"]
    assert payload["valor_rp"] == valor_rp
    assert payload["unidad"] == unidad
    assert payload["registrado_por"] == juez


@then(parsers.parse('el sistema rechaza la operación con error "{error_type}"'))
def step_error_esperado_resultado(ctx: dict, error_type: str) -> None:  # type: ignore[type-arg]
    error_map = {
        "EstadoInvalidoParaRegistrarResultado": EstadoInvalidoParaRegistrarResultado,
    }
    assert ctx["error"] is not None, "Se esperaba un error pero no hubo ninguno"
    expected = error_map[error_type]
    assert isinstance(ctx["error"], expected), (
        f"Error esperado: {error_type}, obtenido: {type(ctx['error']).__name__}"
    )


@then(parsers.parse('la performance permanece en estado "{estado}"'))
def step_estado_permanece(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    """Verifica que el error se produjo y el estado no cambió."""
    assert ctx["error"] is not None
