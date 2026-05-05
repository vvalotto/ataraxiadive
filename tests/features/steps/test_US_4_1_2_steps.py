"""Step definitions BDD — US-4.1.2: Tarjeta Blanca con penalizaciones."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from decimal import Decimal
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
from competencia.domain.exceptions import PenalizacionesObligatorias
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica
from competencia.domain.value_objects.tipo_penalizacion import TipoPenalizacion
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter as ResultadosDisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)

scenarios("../US-4.1.2-tarjeta-blanca-penalizaciones.feature")

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

OT = datetime(2026, 4, 8, 10, 30, 0)

_PENALIZACIONES = {
    "SIN_CONTACTO_PARED": PenalizacionTecnica(TipoPenalizacion.SIN_CONTACTO_PARED, Decimal("3")),
    "FUERA_DE_CARRIL": PenalizacionTecnica(TipoPenalizacion.FUERA_DE_CARRIL, Decimal("3")),
}


@pytest.fixture
def ctx_us_4_1_2():
    comp_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    ranking_db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    comp_path = comp_db.name
    ranking_path = ranking_db.name
    comp_db.close()
    ranking_db.close()

    async def _setup():
        for path in (comp_path, ranking_path):
            async with aiosqlite.connect(path) as db:
                await db.execute(_CREATE_TABLE)
                await db.commit()

        store = SQLiteEventStore(comp_path)
        ranking_store = SQLiteEventStore(ranking_path)
        stub = StubCompetenciaEstadoAdapter()
        cid = uuid4()
        pid = uuid4()

        return {
            "store": store,
            "ranking_store": ranking_store,
            "stub": stub,
            "cid": cid,
            "pid": pid,
            "error": None,
            "ranking": None,
        }

    return asyncio.run(_setup())


def _bootstrap_performance(ctx: dict, rp: str, pid: object | None = None) -> None:
    async def _run():
        participante_id = pid or ctx["pid"]
        await RegistrarAPHandler(ctx["store"], ctx["stub"], DisciplinaDescriptorAdapter()).handle(
            RegistrarAPCommand(
                competencia_id=ctx["cid"],
                participante_id=participante_id,
                disciplina=Disciplina.DYN,
                valor_ap=Decimal(rp),
                unidad=UnidadMedida.Metros,
            )
        )
        await LlamarAtletaHandler(ctx["store"], ctx["stub"]).handle(
            LlamarAtletaCommand(
                competencia_id=ctx["cid"],
                participante_id=participante_id,
                disciplina=Disciplina.DYN,
                ot_programado=OT,
                posicion_grilla=1,
            )
        )
        await RegistrarResultadoHandler(ctx["store"], DisciplinaDescriptorAdapter()).handle(
            RegistrarResultadoCommand(
                competencia_id=ctx["cid"],
                participante_id=participante_id,
                disciplina=Disciplina.DYN,
                valor_rp=Decimal(rp),
                unidad=UnidadMedida.Metros,
                registrado_por="juez-001",
            )
        )

    asyncio.run(_run())


@given(
    parsers.parse("una Performance en estado ResultadoRegistrado para disciplina DYN con RP {rp}"),
    target_fixture="ctx",
)
def given_performance(ctx_us_4_1_2, rp: str):
    ctx_us_4_1_2["pid"] = uuid4()
    _bootstrap_performance(ctx_us_4_1_2, rp)
    return ctx_us_4_1_2


@given("dos performances finalizadas en DYN con RP penalizado 66 y RP valido 70")
def given_dos_performances(ctx):
    atleta_a = uuid4()
    atleta_b = uuid4()
    ctx["atleta_penalizado"] = atleta_a
    ctx["atleta_valido"] = atleta_b
    _bootstrap_performance(ctx, "72", pid=atleta_a)
    _bootstrap_performance(ctx, "70", pid=atleta_b)

    async def _run():
        handler = AsignarTarjetaHandler(ctx["store"])
        await handler.handle(
            AsignarTarjetaCommand(
                competencia_id=ctx["cid"],
                participante_id=atleta_a,
                disciplina=Disciplina.DYN,
                tipo=TipoTarjeta.BlancaConPenalizaciones,
                asignada_por="juez-001",
                penalizaciones=(
                    _PENALIZACIONES["SIN_CONTACTO_PARED"],
                    _PENALIZACIONES["FUERA_DE_CARRIL"],
                ),
            )
        )
        await handler.handle(
            AsignarTarjetaCommand(
                competencia_id=ctx["cid"],
                participante_id=atleta_b,
                disciplina=Disciplina.DYN,
                tipo=TipoTarjeta.Blanca,
                asignada_por="juez-001",
            )
        )

    asyncio.run(_run())


def _asignar(ctx: dict, penalizaciones: tuple[PenalizacionTecnica, ...]) -> None:
    handler = AsignarTarjetaHandler(ctx["store"])

    async def _run():
        try:
            await handler.handle(
                AsignarTarjetaCommand(
                    competencia_id=ctx["cid"],
                    participante_id=ctx["pid"],
                    disciplina=Disciplina.DYN,
                    tipo=TipoTarjeta.BlancaConPenalizaciones,
                    asignada_por="juez-001",
                    penalizaciones=penalizaciones,
                )
            )
        except Exception as exc:
            ctx["error"] = exc

    asyncio.run(_run())


@when("el juez asigna tarjeta BlancaConPenalizaciones con penalizacion SIN_CONTACTO_PARED")
def when_una_penalizacion(ctx):
    _asignar(ctx, (_PENALIZACIONES["SIN_CONTACTO_PARED"],))


@when(
    "el juez asigna tarjeta BlancaConPenalizaciones con penalizaciones SIN_CONTACTO_PARED y FUERA_DE_CARRIL"
)
def when_dos_penalizaciones(ctx):
    _asignar(
        ctx,
        (_PENALIZACIONES["SIN_CONTACTO_PARED"], _PENALIZACIONES["FUERA_DE_CARRIL"]),
    )


@when("el juez asigna tarjeta BlancaConPenalizaciones con lista de penalizaciones vacia")
def when_lista_vacia(ctx):
    _asignar(ctx, ())


@when("se calcula el ranking de la disciplina DYN")
def when_calcula_ranking(ctx):
    async def _run():
        handler = CalcularRankingHandler(
            ranking_store=ctx["ranking_store"],
            resultados_port=ResultadosCompetenciaAdapter(ctx["store"]),
            descriptor=ResultadosDisciplinaDescriptorAdapter(),
        )
        await handler.handle(
            CalcularRankingCommand(competencia_id=ctx["cid"], disciplina=Disciplina.DYN)
        )
        ctx["ranking"] = await ObtenerRankingHandler(ctx["ranking_store"]).handle(
            ObtenerRankingQuery(competencia_id=ctx["cid"], disciplina=Disciplina.DYN)
        )

    asyncio.run(_run())


def _load_performance(ctx: dict) -> Performance:
    async def _run():
        stream_id = f"performance-{ctx['cid']}-{ctx['pid']}-{Disciplina.DYN.value}"
        events = await ctx["store"].load(stream_id)
        return Performance.reconstitute(events)

    return asyncio.run(_run())


@then("la Performance pasa a estado Ejecutada")
def then_ejecutada(ctx):
    assert ctx["error"] is None
    assert _load_performance(ctx).estado == EstadoPerformance.Ejecutada


@then(parsers.parse("rp_medido es {rp}"))
def then_rp_medido(ctx, rp: str):
    assert _load_performance(ctx).rp_medido == Decimal(rp)


@then(parsers.parse("rp_penalizado es {rp}"))
def then_rp_penalizado(ctx, rp: str):
    assert _load_performance(ctx).rp_penalizado == Decimal(rp)


@then(parsers.parse('el evento TarjetaAsignada registra tipo "{tipo}"'))
def then_tipo_evento(ctx, tipo: str):
    async def _run():
        stream_id = f"performance-{ctx['cid']}-{ctx['pid']}-{Disciplina.DYN.value}"
        return await ctx["store"].load(stream_id)

    events = asyncio.run(_run())
    payload = next(e for e in events if e["event_type"] == "TarjetaAsignada")["payload"]
    assert payload["tipo"] == tipo


@then(
    parsers.parse("el evento incluye la penalizacion SIN_CONTACTO_PARED con deduccion {deduccion}")
)
def then_evento_penalizacion(ctx, deduccion: str):
    async def _run():
        stream_id = f"performance-{ctx['cid']}-{ctx['pid']}-{Disciplina.DYN.value}"
        return await ctx["store"].load(stream_id)

    events = asyncio.run(_run())
    payload = next(e for e in events if e["event_type"] == "TarjetaAsignada")["payload"]
    assert payload["penalizaciones"][0]["tipo"] == "SIN_CONTACTO_PARED"
    assert payload["penalizaciones"][0]["deduccion"] == deduccion


@then(parsers.parse("el evento TarjetaAsignada registra {cantidad:d} penalizaciones"))
def then_evento_cantidad_penalizaciones(ctx, cantidad: int):
    async def _run():
        stream_id = f"performance-{ctx['cid']}-{ctx['pid']}-{Disciplina.DYN.value}"
        return await ctx["store"].load(stream_id)

    events = asyncio.run(_run())
    payload = next(e for e in events if e["event_type"] == "TarjetaAsignada")["payload"]
    assert len(payload["penalizaciones"]) == cantidad


@then("se lanza PenalizacionesObligatorias")
def then_penalizaciones_obligatorias(ctx):
    assert isinstance(ctx["error"], PenalizacionesObligatorias)


@then(parsers.parse('el evento TarjetaAsignada registra rp_penalizado "{rp}"'))
def then_evento_rp_penalizado(ctx, rp: str):
    async def _run():
        stream_id = f"performance-{ctx['cid']}-{ctx['pid']}-{Disciplina.DYN.value}"
        return await ctx["store"].load(stream_id)

    events = asyncio.run(_run())
    payload = next(e for e in events if e["event_type"] == "TarjetaAsignada")["payload"]
    assert payload["rp_penalizado"] == rp


@then("el atleta con RP 70 aparece antes que el atleta con RP penalizado 66")
def then_ranking_orden(ctx):
    entradas = ctx["ranking"][0].entradas
    assert entradas[0].atleta_id == str(ctx["atleta_valido"])
    assert entradas[1].atleta_id == str(ctx["atleta_penalizado"])
