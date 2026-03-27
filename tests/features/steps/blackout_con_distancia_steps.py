"""Step definitions BDD — US-1.4.1: Black-out con Distancia."""
from __future__ import annotations

import asyncio
import tempfile
from decimal import Decimal
from datetime import datetime
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import DistanciaBlackoutObligatoria
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
scenarios("../US-1.4.1-blackout-con-distancia.feature")

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


# ── Fixture de contexto ───────────────────────────────────────────────────────


@pytest.fixture
def ctx_blackout():
    """Contexto compartido entre steps del escenario."""
    return {}


# ── Background ────────────────────────────────────────────────────────────────


@given("una Performance en estado ResultadoRegistrado", target_fixture="ctx_blackout")
def step_performance_en_resultado_registrado():
    """Crea una Performance con AP, llamada y resultado registrado."""
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    async def _setup():
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

        store = SQLiteEventStore(db_path)
        stub = StubCompetenciaEstadoAdapter()
        cid = uuid4()
        pid = uuid4()

        ap_handler = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
        llamar_handler = LlamarAtletaHandler(store, stub)
        resultado_handler = RegistrarResultadoHandler(store, DisciplinaDescriptorAdapter())

        await ap_handler.handle(
            RegistrarAPCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF, valor_ap=Decimal("50"), unidad=UnidadMedida.Metros,
            )
        )
        await llamar_handler.handle(
            LlamarAtletaCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF, ot_programado=OT, posicion_grilla=1,
            )
        )
        await resultado_handler.handle(
            RegistrarResultadoCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF,
                valor_rp=Decimal("45.5"), unidad=UnidadMedida.Metros,
                registrado_por="juez-001",
            )
        )
        return {"store": store, "cid": cid, "pid": pid, "exception": None, "events": []}

    return asyncio.run(_setup())


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('el juez asigna tarjeta roja con motivo "black-out" y distancia {distancia} metros'))
def step_asignar_blackout_con_distancia(ctx_blackout, distancia: str):
    handler = AsignarTarjetaHandler(ctx_blackout["store"])

    async def _run():
        try:
            await handler.handle(
                AsignarTarjetaCommand(
                    competencia_id=ctx_blackout["cid"],
                    participante_id=ctx_blackout["pid"],
                    disciplina=Disciplina.DNF,
                    tipo=TipoTarjeta.Roja,
                    asignada_por="juez-001",
                    motivo="black-out",
                    distancia_blackout=Decimal(distancia),
                )
            )
        except Exception as e:
            ctx_blackout["exception"] = e

    asyncio.run(_run())


@when('el juez asigna tarjeta roja con motivo "black-out" sin distancia')
def step_asignar_blackout_sin_distancia(ctx_blackout):
    handler = AsignarTarjetaHandler(ctx_blackout["store"])

    async def _run():
        try:
            await handler.handle(
                AsignarTarjetaCommand(
                    competencia_id=ctx_blackout["cid"],
                    participante_id=ctx_blackout["pid"],
                    disciplina=Disciplina.DNF,
                    tipo=TipoTarjeta.Roja,
                    asignada_por="juez-001",
                    motivo="black-out",
                )
            )
        except Exception as e:
            ctx_blackout["exception"] = e

    asyncio.run(_run())


@when('el juez asigna tarjeta roja con motivo "tiempo excedido" sin distancia')
def step_asignar_roja_sin_blackout(ctx_blackout):
    handler = AsignarTarjetaHandler(ctx_blackout["store"])

    async def _run():
        try:
            await handler.handle(
                AsignarTarjetaCommand(
                    competencia_id=ctx_blackout["cid"],
                    participante_id=ctx_blackout["pid"],
                    disciplina=Disciplina.DNF,
                    tipo=TipoTarjeta.Roja,
                    asignada_por="juez-001",
                    motivo="tiempo excedido",
                )
            )
        except Exception as e:
            ctx_blackout["exception"] = e

    asyncio.run(_run())


# ── Then ──────────────────────────────────────────────────────────────────────


@then("la Performance queda en estado Ejecutada")
def step_performance_ejecutada(ctx_blackout):
    assert ctx_blackout["exception"] is None

    async def _load():
        stream_id = f"performance-{ctx_blackout['cid']}-{ctx_blackout['pid']}-DNF"
        events = await ctx_blackout["store"].load(stream_id)
        return Performance.reconstitute(events)

    performance = asyncio.run(_load())
    assert performance.estado == EstadoPerformance.Ejecutada


@then(parsers.parse("el evento TarjetaAsignada contiene distancia_blackout {distancia}"))
def step_evento_contiene_distancia(ctx_blackout, distancia: str):
    async def _load():
        stream_id = f"performance-{ctx_blackout['cid']}-{ctx_blackout['pid']}-DNF"
        return await ctx_blackout["store"].load(stream_id)

    events = asyncio.run(_load())
    tarjeta_event = next(e for e in events if e["event_type"] == "TarjetaAsignada")
    assert tarjeta_event["payload"]["distancia_blackout"] == distancia


@then("se lanza DistanciaBlackoutObligatoria")
def step_lanza_distancia_obligatoria(ctx_blackout):
    assert isinstance(ctx_blackout["exception"], DistanciaBlackoutObligatoria)
