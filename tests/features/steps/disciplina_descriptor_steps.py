"""Step definitions BDD — US-2.2.1: DisciplinaDescriptor VO + Port."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from tests.features.steps._stubs import StubPerformancesAPPort

scenarios("../US-2.2.1-disciplina-descriptor.feature")

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

_DISCIPLINA_MAP: dict[str, Disciplina] = {d.value: d for d in Disciplina}


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path) -> dict:  # type: ignore[type-arg]
    db_path = str(tmp_path / "bdd_descriptor.db")
    asyncio.run(_create_db(db_path))
    return {
        "store": SQLiteEventStore(db_path),
        "adapter": DisciplinaDescriptorAdapter(),
    }


async def _create_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


# ── Given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('la disciplina es "{disc}"'))
def dada_disciplina(context: dict, disc: str) -> None:
    context["disciplina"] = _DISCIPLINA_MAP[disc]


@given(parsers.parse("una competencia {disc} con 3 atletas con APs {ap1}, {ap2} y {ap3}"))
def dada_competencia_con_aps(context: dict, disc: str, ap1: str, ap2: str, ap3: str) -> None:
    disciplina = _DISCIPLINA_MAP[disc]
    comp_id = uuid4()
    context["competencia_id"] = comp_id
    context["disciplina"] = disciplina

    def _parse_ap(raw: str) -> tuple[Decimal, UnidadMedida]:
        raw = raw.strip()
        if raw.endswith("s"):
            return Decimal(raw[:-1]), UnidadMedida.Segundos
        if raw.endswith("m"):
            return Decimal(raw[:-1]), UnidadMedida.Metros
        raise ValueError(f"Unidad desconocida: {raw}")

    atleta_ids = [uuid4(), uuid4(), uuid4()]
    context["atleta_ids"] = atleta_ids
    aps_raw = [ap1, ap2, ap3]
    aps = [_parse_ap(r) for r in aps_raw]

    store: SQLiteEventStore = context["store"]

    async def _seed() -> None:
        await ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=comp_id,
                disciplina=disciplina,
                intervalo_minutos=9,
                configurado_por="org",
            )
        )
        for atleta_id, (valor, unidad) in zip(atleta_ids, aps):
            await RegistrarAPHandler(
                store, StubCompetenciaEstadoAdapter(), DisciplinaDescriptorAdapter()
            ).handle(
                RegistrarAPCommand(
                    competencia_id=comp_id,
                    participante_id=atleta_id,
                    disciplina=disciplina,
                    valor_ap=valor,
                    unidad=unidad,
                )
            )
        context["aps_por_atleta"] = dict(zip(atleta_ids, [v for v, _ in aps]))

    asyncio.run(_seed())


@given(parsers.parse("el intervalo OT está configurado en {n:d} minutos"))
def dado_intervalo_configurado(context: dict, n: int) -> None:
    pass  # ya configurado en el Given anterior


# ── When ──────────────────────────────────────────────────────────────────────


@when("se consulta el DisciplinaDescriptorPort")
def cuando_consulta_descriptor(context: dict) -> None:
    adapter: DisciplinaDescriptorAdapter = context["adapter"]
    context["descriptor"] = adapter.describe(context["disciplina"])


@when("se genera la grilla usando el DisciplinaDescriptorPort")
def cuando_genera_grilla(context: dict) -> None:
    store: SQLiteEventStore = context["store"]
    ap_adapter = StubPerformancesAPPort(store)
    handler = GenerarGrillaHandler(store, ap_adapter, context["adapter"])
    ot = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
    asyncio.run(
        handler.handle(
            GenerarGrillaCommand(
                competencia_id=context["competencia_id"],
                disciplina=context["disciplina"],
                ot_inicio=ot,
            )
        )
    )
    # Reconstituir para leer la grilla
    from competencia.domain.aggregates.competencia import Competencia

    comp_id = context["competencia_id"]
    stream_id = f"competencia-{comp_id}"
    events = asyncio.run(store.load(stream_id))
    comp = Competencia.reconstitute(comp_id, context["disciplina"], events)
    context["grilla"] = comp.grilla


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('unidad_esperada es "{unidad}"'))
def entonces_unidad_es(context: dict, unidad: str) -> None:
    desc: DisciplinaDescriptor = context["descriptor"]
    assert desc.unidad_esperada.value == unidad


@then(parsers.parse("orden_ascendente es {valor}"))
def entonces_orden_ascendente_es(context: dict, valor: str) -> None:
    desc: DisciplinaDescriptor = context["descriptor"]
    expected = valor.strip() == "True"
    assert desc.orden_ascendente is expected


@then(
    parsers.parse(
        "el orden de la grilla es posición 1 con AP {ap1}, posición 2 con AP {ap2}, posición 3 con AP {ap3}"
    )
)
def entonces_orden_grilla(context: dict, ap1: str, ap2: str, ap3: str) -> None:
    def _valor(raw: str) -> Decimal:
        raw = raw.strip()
        if raw.endswith("s") or raw.endswith("m"):
            return Decimal(raw[:-1])
        return Decimal(raw)

    grilla = context["grilla"]
    aps_por_atleta: dict[UUID, Decimal] = context["aps_por_atleta"]

    expected = [_valor(ap1), _valor(ap2), _valor(ap3)]
    actual = [aps_por_atleta[e.atleta_id] for e in sorted(grilla, key=lambda e: e.posicion)]
    assert actual == expected
