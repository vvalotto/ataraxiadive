"""Step definitions BDD — US-4.1.3: Subdisciplinas SPE."""

from __future__ import annotations

import asyncio
from datetime import date, datetime
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
    UnidadIncompatible,
)
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.application.queries.obtener_ranking import ObtenerRankingHandler, ObtenerRankingQuery
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter as ResultadosDisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from shared.domain.value_objects.unidad_medida import UnidadMedida
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import DisciplinaObsoleta
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede

scenarios("../US-4.1.3-subdisciplinas-spe.feature")

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


@pytest.fixture
def ctx_us_4_1_3(tmp_path) -> dict:  # type: ignore[type-arg]
    comp_path = str(tmp_path / "competencia.db")
    ranking_path = str(tmp_path / "resultados.db")

    async def _setup() -> None:
        for path in (comp_path, ranking_path):
            async with aiosqlite.connect(path) as db:
                await db.execute(_CREATE_TABLE)
                await db.commit()

    asyncio.run(_setup())

    return {
        "comp_store": SQLiteEventStore(comp_path),
        "ranking_store": SQLiteEventStore(ranking_path),
        "stub": StubCompetenciaEstadoAdapter(),
        "descriptor": DisciplinaDescriptorAdapter(),
        "error": None,
        "ranking": None,
    }


def _torneo_base() -> Torneo:
    return Torneo(
        nombre="Copa SPE",
        descripcion="Test",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina", "CABA", "Argentina"),
        entidad_organizadora=EntidadOrganizadora("FAADS", "federacion"),
    )


async def _registrar_performance_finalizada(
    ctx: dict,
    participante_id,
    disciplina: Disciplina,
    valor: str,
    ot: datetime,
) -> None:
    await RegistrarAPHandler(ctx["comp_store"], ctx["stub"], ctx["descriptor"]).handle(
        RegistrarAPCommand(
            competencia_id=ctx.setdefault("cid", uuid4()),
            participante_id=participante_id,
            disciplina=disciplina,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Segundos,
        )
    )
    await LlamarAtletaHandler(ctx["comp_store"], ctx["stub"]).handle(
        LlamarAtletaCommand(
            competencia_id=ctx["cid"],
            participante_id=participante_id,
            disciplina=disciplina,
            posicion_grilla=1,
            ot_programado=ot,
        )
    )
    await RegistrarResultadoHandler(ctx["comp_store"], ctx["descriptor"]).handle(
        RegistrarResultadoCommand(
            competencia_id=ctx["cid"],
            participante_id=participante_id,
            disciplina=disciplina,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Segundos,
            registrado_por="juez-001",
        )
    )
    await AsignarTarjetaHandler(ctx["comp_store"]).handle(
        AsignarTarjetaCommand(
            competencia_id=ctx["cid"],
            participante_id=participante_id,
            disciplina=disciplina,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-001",
        )
    )


@given("el DisciplinaDescriptor para SPE_2X50", target_fixture="ctx")
def given_descriptor_spe(ctx_us_4_1_3):
    ctx_us_4_1_3["descriptor_actual"] = DisciplinaDescriptor.para(Disciplina.SPE_2X50)
    return ctx_us_4_1_3


@given("un torneo con SPE_4X50 y SPE_8X50 configuradas", target_fixture="ctx")
def given_torneo_con_variantes(ctx_us_4_1_3):
    torneo = _torneo_base()
    torneo.asignar_disciplinas(frozenset({Disciplina.SPE_4X50, Disciplina.SPE_8X50}))
    ctx_us_4_1_3["torneo"] = torneo
    return ctx_us_4_1_3


@given("un torneo con performances en SPE_2X50 y SPE_8X50", target_fixture="ctx")
def given_torneo_con_performances(ctx_us_4_1_3):
    atleta_spe_2 = uuid4()
    atleta_spe_8 = uuid4()
    ctx_us_4_1_3["atleta_spe_2"] = atleta_spe_2
    ctx_us_4_1_3["atleta_spe_8"] = atleta_spe_8

    async def _run() -> None:
        await _registrar_performance_finalizada(
            ctx_us_4_1_3,
            atleta_spe_2,
            Disciplina.SPE_2X50,
            "180",
            datetime(2026, 4, 8, 10, 0, 0),
        )
        await _registrar_performance_finalizada(
            ctx_us_4_1_3,
            atleta_spe_8,
            Disciplina.SPE_8X50,
            "420",
            datetime(2026, 4, 8, 10, 5, 0),
        )

    asyncio.run(_run())
    return ctx_us_4_1_3


@given("una Performance para disciplina SPE_4X50", target_fixture="ctx")
def given_performance_spe_4(ctx_us_4_1_3):
    ctx_us_4_1_3["disciplina_actual"] = Disciplina.SPE_4X50
    ctx_us_4_1_3["cid"] = uuid4()
    ctx_us_4_1_3["pid"] = uuid4()
    return ctx_us_4_1_3


@given("una Performance para disciplina SPE_2X50", target_fixture="ctx")
def given_performance_spe_2(ctx_us_4_1_3):
    ctx_us_4_1_3["disciplina_actual"] = Disciplina.SPE_2X50
    ctx_us_4_1_3["cid"] = uuid4()
    ctx_us_4_1_3["pid"] = uuid4()
    return ctx_us_4_1_3


@given("un Torneo recién creado", target_fixture="ctx")
def given_torneo_recien_creado(ctx_us_4_1_3):
    ctx_us_4_1_3["torneo"] = _torneo_base()
    return ctx_us_4_1_3


@when("se consultan las disciplinas configuradas del torneo")
def when_consultan_disciplinas(ctx):
    ctx["disciplinas_torneo"] = {dt.disciplina for dt in ctx["torneo"].disciplinas_torneo}


@when("se consulta el ranking de SPE_2X50")
def when_consulta_ranking(ctx):
    async def _run() -> None:
        await CalcularRankingHandler(
            ranking_store=ctx["ranking_store"],
            resultados_port=ResultadosCompetenciaAdapter(ctx["comp_store"]),
            descriptor=ResultadosDisciplinaDescriptorAdapter(),
        ).handle(CalcularRankingCommand(competencia_id=ctx["cid"], disciplina=Disciplina.SPE_2X50))
        ctx["ranking"] = await ObtenerRankingHandler(ctx["ranking_store"]).handle(
            ObtenerRankingQuery(competencia_id=ctx["cid"], disciplina=Disciplina.SPE_2X50)
        )

    asyncio.run(_run())


@when(parsers.parse("se registra AP con valor {valor} y unidad {unidad}"))
def when_registra_ap(ctx, valor: str, unidad: str):
    try:
        asyncio.run(
            RegistrarAPHandler(ctx["comp_store"], ctx["stub"], ctx["descriptor"]).handle(
                RegistrarAPCommand(
                    competencia_id=ctx["cid"],
                    participante_id=ctx["pid"],
                    disciplina=ctx["disciplina_actual"],
                    valor_ap=Decimal(valor),
                    unidad=getattr(UnidadMedida, unidad),
                )
            )
        )
    except Exception as exc:
        ctx["error"] = exc


@when("se intenta agregar disciplina SPE genérica al torneo")
def when_intenta_agregar_spe(ctx):
    try:
        ctx["torneo"].asignar_disciplinas(frozenset({Disciplina.SPE}))
    except Exception as exc:
        ctx["error"] = exc


@then("unidad_esperada es Segundos")
def then_unidad_segundos(ctx):
    assert ctx["descriptor_actual"].unidad_esperada == UnidadMedida.Segundos


@then("orden_ascendente es False")
def then_orden_descendente(ctx):
    assert ctx["descriptor_actual"].orden_ascendente is False


@then("es_tiempo() retorna True")
def then_es_tiempo(ctx):
    assert Disciplina.SPE_2X50.es_tiempo() is True


@then("es_spe() retorna True")
def then_es_spe(ctx):
    assert Disciplina.SPE_2X50.es_spe() is True


@then("SPE_4X50 queda configurada en el torneo")
def then_torneo_tiene_spe_4(ctx):
    assert Disciplina.SPE_4X50 in ctx["disciplinas_torneo"]


@then("SPE_8X50 queda configurada en el torneo")
def then_torneo_tiene_spe_8(ctx):
    assert Disciplina.SPE_8X50 in ctx["disciplinas_torneo"]


@then("ambas disciplinas son independientes")
def then_ambas_independientes(ctx):
    assert len(ctx["disciplinas_torneo"]) == 2


@then("el ranking de SPE_2X50 no incluye atletas de SPE_8X50")
def then_ranking_independiente(ctx):
    entradas = ctx["ranking"][0].entradas
    atleta_ids = {entry.atleta_id for entry in entradas}
    assert str(ctx["atleta_spe_2"]) in atleta_ids
    assert str(ctx["atleta_spe_8"]) not in atleta_ids


@then("el AP queda registrado correctamente")
def then_ap_registrado(ctx):
    assert ctx["error"] is None

    async def _run() -> None:
        stream_id = f"performance-{ctx['cid']}-{ctx['pid']}-{ctx['disciplina_actual'].value}"
        events = await ctx["comp_store"].load(stream_id)
        assert len(events) == 1
        assert events[0]["payload"]["unidad"] == "Segundos"

    asyncio.run(_run())


@then("se lanza UnidadIncompatible")
def then_unidad_incompatible(ctx):
    assert isinstance(ctx["error"], UnidadIncompatible)


@then("se lanza DisciplinaObsoleta")
def then_disciplina_obsoleta(ctx):
    assert isinstance(ctx["error"], DisciplinaObsoleta)
