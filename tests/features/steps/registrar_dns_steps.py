"""Step definitions BDD — US-1.2.5: Registrar DNS.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""
from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import EstadoInvalidoParaRegistrarDNS
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

scenarios("../US-1.2.5-registrar-dns.feature")

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

OT = datetime(2026, 3, 23, 10, 30, 0)


def _make_event_store(tmp_path: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_dns.db"

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
def step_competencia_activa_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["competencia_id"] = uuid4()


@given(parsers.parse('un atleta con id "{pid}" en disciplina "DNF"'))
def step_atleta_dnf_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["participante_id"] = uuid4()
    ctx["disciplina"] = Disciplina.DNF


@given(
    parsers.parse(
        "la performance del atleta tiene AP registrado de {valor:d} metros y fue llamada"
    )
)
def step_ap_registrado_y_llamada(ctx: dict, valor: int) -> None:  # type: ignore[type-arg]
    """Lleva la performance hasta el estado Llamada."""
    es = ctx["event_store"]
    sp = ctx["estado_port"]
    cid = ctx["competencia_id"]
    pid = ctx["participante_id"]
    disc = ctx["disciplina"]

    asyncio.run(
        RegistrarAPHandler(es, sp).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disc,
                valor_ap=Decimal(str(valor)),
                unidad=UnidadMedida.Metros,
            )
        )
    )
    asyncio.run(
        LlamarAtletaHandler(es, sp).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disc,
                ot_programado=OT,
                posicion_grilla=1,
            )
        )
    )


# ── Given (específicos de escenario) ──────────────────────────────────────────


@given('la performance del atleta está en estado "AnunciadaAP"')
def step_performance_en_anunciada(ctx: dict) -> None:  # type: ignore[type-arg]
    """Resetea con un store fresco y lleva la performance solo hasta AnunciadaAP."""
    fresh_store = _make_event_store(tempfile.mkdtemp())
    cid = uuid4()
    pid = uuid4()
    ctx["event_store"] = fresh_store
    ctx["competencia_id"] = cid
    ctx["participante_id"] = pid
    sp = ctx["estado_port"]
    disc = ctx["disciplina"]

    asyncio.run(
        RegistrarAPHandler(fresh_store, sp).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disc,
                valor_ap=Decimal("50"),
                unidad=UnidadMedida.Metros,
            )
        )
    )


@given(
    parsers.parse("la performance del atleta tiene RP registrado de {rp:f} metros")
)
def step_performance_con_resultado(ctx: dict, rp: float) -> None:  # type: ignore[type-arg]
    """Avanza la performance hasta ResultadoRegistrado desde el estado Llamada del Background."""
    es = ctx["event_store"]
    cid = ctx["competencia_id"]
    pid = ctx["participante_id"]
    disc = ctx["disciplina"]

    asyncio.run(
        RegistrarResultadoHandler(es).handle(
            RegistrarResultadoCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disc,
                valor_rp=Decimal(str(rp)),
                unidad=UnidadMedida.Metros,
                registrado_por="juez-001",
            )
        )
    )


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('el juez registra el DNS con registrado_por="{juez}"'))
def step_registrar_dns(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    handler = RegistrarDNSHandler(ctx["event_store"])
    cmd = RegistrarDNSCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        registrado_por=juez,
    )
    try:
        ctx["result"] = asyncio.run(handler.handle(cmd))
        ctx["registrado_por"] = juez
    except Exception as exc:
        ctx["error"] = exc


@when(parsers.parse('el juez intenta registrar DNS con registrado_por="{juez}"'))
def step_intentar_dns(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    step_registrar_dns(ctx, juez)


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('la performance pasa al estado "{estado}"'))
def step_estado_dns(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance(estado)


@then("el evento DNSRegistrado persiste en el event stream")
def step_evento_dns_en_stream(ctx: dict) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    assert any(e["event_type"] == "DNSRegistrado" for e in events)


@then(parsers.parse('el evento contiene registradoPor="{juez}"'))
def step_payload_dns_correcto(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    dns_ev = next(e for e in events if e["event_type"] == "DNSRegistrado")
    payload = dns_ev["payload"]
    assert payload["registrado_por"] == juez


@then(parsers.parse('el sistema rechaza la operación con error "{error_type}"'))
def step_error_esperado_dns(ctx: dict, error_type: str) -> None:  # type: ignore[type-arg]
    error_map = {
        "EstadoInvalidoParaRegistrarDNS": EstadoInvalidoParaRegistrarDNS,
    }
    assert ctx["error"] is not None, "Se esperaba un error pero no hubo ninguno"
    expected = error_map[error_type]
    assert isinstance(ctx["error"], expected), (
        f"Error esperado: {error_type}, obtenido: {type(ctx['error']).__name__}"
    )


@then(parsers.parse('la performance permanece en estado "{estado}"'))
def step_estado_permanece_dns(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    assert ctx["error"] is not None
