"""Step definitions BDD — US-2.4.1: Competencia Finalizada (automático).

Verifica INV-C-04 y la política P-08: disparo automático de CompetenciaFinalizada
cuando todas las performances de la disciplina finalizan.

pytest-bdd no soporta async steps nativamente — se usa asyncio.run() como wrapper.
"""
from __future__ import annotations

import asyncio
import json
import tempfile
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.asignar_tarjeta import AsignarTarjetaCommand, AsignarTarjetaHandler
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import CompetenciaNoFinalizable
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
from competencia.infrastructure.repositories.performances_estado_adapter import PerformancesEstadoAdapter

scenarios("../US-2.4.1-competencia-finalizada.feature")

CREATE_EVENTS_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL
            DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""

OT_A = datetime(2026, 3, 22, 10, 30, 0)
OT_B = datetime(2026, 3, 22, 10, 33, 0)
OT_C = datetime(2026, 3, 22, 10, 36, 0)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _make_store(tmp_path: str) -> SQLiteEventStore:
    return SQLiteEventStore(tmp_path)


async def _init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _registrar_ap_async(store, stub, descriptor, cid, pid) -> None:
    h = RegistrarAPHandler(event_store=store, competencia_estado=stub, disciplina_descriptor=descriptor)
    await h.handle(RegistrarAPCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, valor_ap=Decimal("300"), unidad=UnidadMedida.Segundos,
    ))


async def _llamar_async(store, stub, cid, pid, ot, posicion) -> None:
    h = LlamarAtletaHandler(event_store=store, competencia_estado=stub)
    await h.handle(LlamarAtletaCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, ot_programado=ot, posicion_grilla=posicion, andarivel=posicion,
    ))


async def _registrar_resultado_async(store, descriptor, cid, pid) -> None:
    h = RegistrarResultadoHandler(event_store=store, disciplina_descriptor=descriptor)
    await h.handle(RegistrarResultadoCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, valor_rp=Decimal("295"), unidad=UnidadMedida.Segundos,
        registrado_por="juez",
    ))


async def _asignar_tarjeta_async(store, cid, pid, pe_adapter=None) -> None:
    h = AsignarTarjetaHandler(store, pe_adapter)
    await h.handle(AsignarTarjetaCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, tipo=TipoTarjeta.Blanca, asignada_por="juez",
    ))


async def _registrar_dns_async(store, cid, pid, pe_adapter=None) -> None:
    h = RegistrarDNSHandler(store, pe_adapter)
    await h.handle(RegistrarDNSCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, registrado_por="juez",
    ))


async def _tiene_evento(store, stream_id, event_type) -> bool:
    events = await store.load(stream_id)
    return any(e["event_type"] == event_type for e in events)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def ctx():
    """Contexto compartido entre steps del mismo escenario."""
    return {}


# ── Background ────────────────────────────────────────────────────────────────


@given("una competencia STA en estado EnEjecucion con 3 performances")
def given_competencia_3_performances(ctx):
    tmp = tempfile.mktemp(suffix=".db")
    asyncio.run(_init_db(tmp))
    ctx["store"] = _make_store(tmp)
    ctx["stub"] = StubCompetenciaEstadoAdapter()
    ctx["descriptor"] = DisciplinaDescriptorAdapter()
    ctx["pe_adapter"] = PerformancesEstadoAdapter(ctx["store"])
    ctx["cid"] = uuid4()
    ctx["pid_a"] = uuid4()
    ctx["pid_b"] = uuid4()
    ctx["pid_c"] = uuid4()

    async def _setup():
        for pid in [ctx["pid_a"], ctx["pid_b"], ctx["pid_c"]]:
            await _registrar_ap_async(ctx["store"], ctx["stub"], ctx["descriptor"], ctx["cid"], pid)

    asyncio.run(_setup())


@given("las performances A y B están en estado Ejecutada")
def given_a_b_ejecutadas(ctx):
    async def _setup():
        await _llamar_async(ctx["store"], ctx["stub"], ctx["cid"], ctx["pid_a"], OT_A, 1)
        await _registrar_resultado_async(ctx["store"], ctx["descriptor"], ctx["cid"], ctx["pid_a"])
        await _asignar_tarjeta_async(ctx["store"], ctx["cid"], ctx["pid_a"])

        await _llamar_async(ctx["store"], ctx["stub"], ctx["cid"], ctx["pid_b"], OT_B, 2)
        await _registrar_resultado_async(ctx["store"], ctx["descriptor"], ctx["cid"], ctx["pid_b"])
        await _asignar_tarjeta_async(ctx["store"], ctx["cid"], ctx["pid_b"])

    asyncio.run(_setup())


@given("la performance C está en estado Llamada")
def given_c_en_llamada(ctx):
    asyncio.run(_llamar_async(ctx["store"], ctx["stub"], ctx["cid"], ctx["pid_c"], OT_C, 3))


# ── Scenario: tarjeta dispara finalización ─────────────────────────────────────


@when("el juez asigna tarjeta blanca a la performance C")
def when_asigna_tarjeta_c(ctx):
    async def _act():
        await _registrar_resultado_async(ctx["store"], ctx["descriptor"], ctx["cid"], ctx["pid_c"])
        await _asignar_tarjeta_async(ctx["store"], ctx["cid"], ctx["pid_c"], ctx["pe_adapter"])

    asyncio.run(_act())


@then("el evento TarjetaAsignada persiste en el stream de C")
def then_tarjeta_asignada_persiste(ctx):
    stream_id = f"performance-{ctx['cid']}-{ctx['pid_c']}-STA"
    assert asyncio.run(_tiene_evento(ctx["store"], stream_id, "TarjetaAsignada"))


@then("el sistema dispara CompetenciaFinalizada automáticamente")
def then_competencia_finalizada(ctx):
    stream_id = f"competencia-{ctx['cid']}"
    assert asyncio.run(_tiene_evento(ctx["store"], stream_id, "CompetenciaFinalizada"))


@then("la competencia pasa al estado Finalizada")
def then_estado_finalizada(ctx):
    async def _check():
        events = await ctx["store"].load(f"competencia-{ctx['cid']}")
        comp = Competencia.reconstitute(
            competencia_id=ctx["cid"], disciplina=Disciplina.STA, events=events
        )
        return comp.estado

    estado = asyncio.run(_check())
    assert estado == EstadoCompetencia.Finalizada


# ── Scenario: DNS dispara finalización ────────────────────────────────────────


@when("el juez registra DNS para la performance C")
def when_registra_dns_c(ctx):
    asyncio.run(_registrar_dns_async(ctx["store"], ctx["cid"], ctx["pid_c"], ctx["pe_adapter"]))


@then("el evento DNSRegistrado persiste en el stream de C")
def then_dns_registrado_persiste(ctx):
    stream_id = f"performance-{ctx['cid']}-{ctx['pid_c']}-STA"
    assert asyncio.run(_tiene_evento(ctx["store"], stream_id, "DNSRegistrado"))


# ── Scenario: no finaliza si quedan pendientes ────────────────────────────────


@given("una competencia STA con solo performance A en Ejecutada y B y C en Llamada")
def given_competencia_a_ejecutada_bc_llamada(ctx):
    tmp = tempfile.mktemp(suffix=".db")
    asyncio.run(_init_db(tmp))
    ctx["store"] = _make_store(tmp)
    ctx["stub"] = StubCompetenciaEstadoAdapter()
    ctx["descriptor"] = DisciplinaDescriptorAdapter()
    ctx["pe_adapter"] = PerformancesEstadoAdapter(ctx["store"])
    ctx["cid"] = uuid4()
    ctx["pid_a"] = uuid4()
    ctx["pid_b"] = uuid4()
    ctx["pid_c"] = uuid4()

    async def _setup():
        for pid in [ctx["pid_a"], ctx["pid_b"], ctx["pid_c"]]:
            await _registrar_ap_async(ctx["store"], ctx["stub"], ctx["descriptor"], ctx["cid"], pid)

        await _llamar_async(ctx["store"], ctx["stub"], ctx["cid"], ctx["pid_a"], OT_A, 1)
        await _registrar_resultado_async(ctx["store"], ctx["descriptor"], ctx["cid"], ctx["pid_a"])
        await _asignar_tarjeta_async(ctx["store"], ctx["cid"], ctx["pid_a"])

        await _llamar_async(ctx["store"], ctx["stub"], ctx["cid"], ctx["pid_b"], OT_B, 2)
        await _llamar_async(ctx["store"], ctx["stub"], ctx["cid"], ctx["pid_c"], OT_C, 3)

    asyncio.run(_setup())


@when("el juez asigna tarjeta blanca a performance B")
def when_asigna_tarjeta_b(ctx):
    async def _act():
        await _registrar_resultado_async(ctx["store"], ctx["descriptor"], ctx["cid"], ctx["pid_b"])
        await _asignar_tarjeta_async(ctx["store"], ctx["cid"], ctx["pid_b"], ctx["pe_adapter"])

    asyncio.run(_act())


@then("TarjetaAsignada persiste en el stream de B")
def then_tarjeta_asignada_b(ctx):
    stream_id = f"performance-{ctx['cid']}-{ctx['pid_b']}-STA"
    assert asyncio.run(_tiene_evento(ctx["store"], stream_id, "TarjetaAsignada"))


@then("CompetenciaFinalizada NO es emitido")
def then_competencia_finalizada_no_emitido(ctx):
    stream_id = f"competencia-{ctx['cid']}"
    assert not asyncio.run(_tiene_evento(ctx["store"], stream_id, "CompetenciaFinalizada"))


# ── Scenario: rechazo directo CompetenciaNoFinalizable ───────────────────────


@given("una competencia STA con performance C en estado AnunciadaAP")
def given_competencia_c_anunciada(ctx):
    tmp = tempfile.mktemp(suffix=".db")
    asyncio.run(_init_db(tmp))
    ctx["store"] = _make_store(tmp)
    ctx["cid"] = uuid4()
    ctx["exception"] = None

    # Competencia "vacía" — no hay performances ejecutadas
    ctx["competencia"] = Competencia(competencia_id=ctx["cid"], disciplina=Disciplina.STA)


@when("el sistema intenta finalizar la competencia directamente")
def when_intenta_finalizar(ctx):
    try:
        ctx["competencia"].finalizar(total_performances=3, ejecutadas=1, dns_count=0)
    except CompetenciaNoFinalizable as exc:
        ctx["exception"] = exc


@then("la operación es rechazada con CompetenciaNoFinalizable")
def then_rechazada_no_finalizable(ctx):
    assert isinstance(ctx["exception"], CompetenciaNoFinalizable)


# ── Scenario: payload en stream de Competencia ───────────────────────────────


@when("el sistema dispara CompetenciaFinalizada automáticamente")
def when_ya_fue_disparado(ctx):
    # La finalización ya fue disparada en el When anterior del mismo escenario.
    pass


@then("el stream de la Competencia contiene el evento CompetenciaFinalizada")
def then_stream_contiene_cf(ctx):
    stream_id = f"competencia-{ctx['cid']}"
    assert asyncio.run(_tiene_evento(ctx["store"], stream_id, "CompetenciaFinalizada"))


@then("el evento incluye competencia_id, disciplina y total_performances")
def then_payload_contiene_campos(ctx):
    async def _check():
        events = await ctx["store"].load(f"competencia-{ctx['cid']}")
        cf = next(e for e in events if e["event_type"] == "CompetenciaFinalizada")
        payload = json.loads(cf["payload"]) if isinstance(cf["payload"], str) else cf["payload"]
        return payload

    payload = asyncio.run(_check())
    assert "competencia_id" in payload
    assert "disciplina" in payload
    assert "total_performances" in payload
