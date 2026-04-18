"""Step definitions BDD — US-4.1.4: Orden de grilla reglamentario."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, scenarios, then, when

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.domain.aggregates.competencia import Competencia
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from shared.domain.value_objects.unidad_medida import UnidadMedida

scenarios("../US-4.1.4-orden-grilla-reglamentario.feature")

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
def ctx_us_4_1_4(tmp_path) -> dict:  # type: ignore[type-arg]
    db_path = str(tmp_path / "bdd_grilla_us_4_1_4.db")

    async def _setup() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_setup())
    return {
        "store": SQLiteEventStore(db_path),
        "competencia_id": uuid4(),
        "ot_inicio": datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "descriptor": None,
        "grilla": None,
    }


def _seed_competencia(ctx: dict, disciplina: Disciplina, aps: list[str], unidad: UnidadMedida) -> None:
    async def _run() -> None:
        ctx["disciplina"] = disciplina
        await ConfigurarIntervaloOTHandler(ctx["store"]).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=ctx["competencia_id"],
                disciplina=disciplina,
                intervalo_minutos=9,
                configurado_por="org",
            )
        )
        handler = RegistrarAPHandler(
            ctx["store"], StubCompetenciaEstadoAdapter(), DisciplinaDescriptorAdapter()
        )
        for valor in aps:
            await handler.handle(
                RegistrarAPCommand(
                    competencia_id=ctx["competencia_id"],
                    participante_id=uuid4(),
                    disciplina=disciplina,
                    valor_ap=Decimal(valor[:-1]),
                    unidad=unidad,
                )
            )

    asyncio.run(_run())


@given("una competencia DYN con APs 80m, 60m y 75m", target_fixture="ctx")
def given_dyn(ctx_us_4_1_4):
    _seed_competencia(ctx_us_4_1_4, Disciplina.DYN, ["80m", "60m", "75m"], UnidadMedida.Metros)
    return ctx_us_4_1_4


@given("una competencia STA con APs 300s, 180s y 240s", target_fixture="ctx")
def given_sta(ctx_us_4_1_4):
    _seed_competencia(
        ctx_us_4_1_4, Disciplina.STA, ["300s", "180s", "240s"], UnidadMedida.Segundos
    )
    return ctx_us_4_1_4


@given("una competencia SPE_4X50 con APs 180s, 210s y 195s", target_fixture="ctx")
def given_spe_4(ctx_us_4_1_4):
    _seed_competencia(
        ctx_us_4_1_4,
        Disciplina.SPE_4X50,
        ["180s", "210s", "195s"],
        UnidadMedida.Segundos,
    )
    return ctx_us_4_1_4


@given("una competencia SPE_2X50 con APs 70s, 90s y 80s", target_fixture="ctx")
def given_spe_2(ctx_us_4_1_4):
    _seed_competencia(
        ctx_us_4_1_4,
        Disciplina.SPE_2X50,
        ["70s", "90s", "80s"],
        UnidadMedida.Segundos,
    )
    return ctx_us_4_1_4


@given("el DisciplinaDescriptor para SPE_4X50 en US-4.1.4", target_fixture="ctx")
def given_descriptor_spe(ctx_us_4_1_4):
    ctx_us_4_1_4["descriptor"] = DisciplinaDescriptor.para(Disciplina.SPE_4X50)
    return ctx_us_4_1_4


@given("el DisciplinaDescriptor para DNF en US-4.1.4", target_fixture="ctx")
def given_descriptor_dnf(ctx_us_4_1_4):
    ctx_us_4_1_4["descriptor"] = DisciplinaDescriptor.para(Disciplina.DNF)
    return ctx_us_4_1_4


@when("se genera la grilla reglamentaria")
def when_genera_grilla(ctx):
    async def _run() -> None:
        handler = GenerarGrillaHandler(
            ctx["store"], PerformancesAPAdapter(ctx["store"]), DisciplinaDescriptorAdapter()
        )
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=ctx["competencia_id"],
                disciplina=ctx["disciplina"],
                ot_inicio=ctx["ot_inicio"],
            )
        )
        events = await ctx["store"].load(f"competencia-{ctx['competencia_id']}")
        competencia = Competencia.reconstitute(ctx["competencia_id"], ctx["disciplina"], events)
        ctx["grilla"] = competencia.grilla

    asyncio.run(_run())


def _aps_ordenados(ctx: dict) -> list[str]:
    async def _load() -> list[str]:
        prefix = f"performance-{ctx['competencia_id']}-"
        streams = await ctx["store"].load_all_streams_with_prefix(prefix)
        valor_por_atleta: dict[str, str] = {}
        for stream in streams:
            payload = stream[0]["payload"]
            raw = payload["valor_ap"]
            suffix = "s" if payload["unidad"] == "Segundos" else "m"
            valor_por_atleta[payload["participante_id"]] = f"{raw}{suffix}"
        return [valor_por_atleta[str(entrada.atleta_id)] for entrada in ctx["grilla"]]

    return asyncio.run(_load())


@then("el orden de salida es AP 60m, 75m y 80m")
def then_dyn(ctx):
    assert _aps_ordenados(ctx) == ["60m", "75m", "80m"]


@then("el orden de salida es AP 180s, 240s y 300s")
def then_sta(ctx):
    assert _aps_ordenados(ctx) == ["180s", "240s", "300s"]


@then("el orden de salida es AP 210s, 195s y 180s")
def then_spe_4(ctx):
    assert _aps_ordenados(ctx) == ["210s", "195s", "180s"]


@then("el orden de salida es AP 90s, 80s y 70s")
def then_spe_2(ctx):
    assert _aps_ordenados(ctx) == ["90s", "80s", "70s"]


@then("orden_ascendente es False en US-4.1.4")
def then_desc_false(ctx):
    assert ctx["descriptor"].orden_ascendente is False


@then("unidad_esperada es Segundos en US-4.1.4")
def then_segundos(ctx):
    assert ctx["descriptor"].unidad_esperada == UnidadMedida.Segundos


@then("orden_ascendente es True en US-4.1.4")
def then_asc_true(ctx):
    assert ctx["descriptor"].orden_ascendente is True


@then("unidad_esperada es Metros en US-4.1.4")
def then_metros(ctx):
    assert ctx["descriptor"].unidad_esperada == UnidadMedida.Metros
