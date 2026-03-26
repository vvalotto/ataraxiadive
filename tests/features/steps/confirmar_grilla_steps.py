"""Step definitions BDD — US-2.1.4: Confirmar Grilla + Iniciar Competencia."""
from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import (
    CompetenciaNoConfirmada,
    GrillaNoGenerada,
    GrillaYaConfirmada,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
from competencia.infrastructure.repositories.competencia_estado_adapter import (
    CompetenciaEstadoAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter

scenarios("../US-2.1.4-confirmar-grilla.feature")

_CREATE_TABLE = """
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

_OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
_DISCIPLINA = Disciplina.STA
_A001 = UUID("00000000-0000-0000-0000-000000000011")
_A002 = UUID("00000000-0000-0000-0000-000000000012")

_CID_MAP: dict[str, UUID] = {
    "C001": UUID("00000000-0000-0000-0000-200000000001"),
    "C002": UUID("00000000-0000-0000-0000-200000000002"),
}


def _make_store(tmp_path: str, name: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_214_{name}.db"
    asyncio.run(_create_db(db_path))
    return SQLiteEventStore(db_path)


async def _create_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


@pytest.fixture
def ctx_214(tmp_path: object) -> dict:
    """Contexto compartido entre steps — US-2.1.4."""
    return {
        "store_c001": _make_store(str(tmp_path), "c001"),
        "store_c002": _make_store(str(tmp_path), "c002"),
        "last_exception": None,
        "adapter_result": None,
    }


def _store(ctx: dict, comp: str) -> SQLiteEventStore:
    return ctx[f"store_{comp.lower()}"]


def _cid(comp: str) -> UUID:
    return _CID_MAP[comp]


async def _seed_grilla(store: SQLiteEventStore, comp_id: UUID) -> None:
    """Seed: intervalo + 2 APs + grilla generada."""
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=comp_id,
            disciplina=_DISCIPLINA,
            intervalo_minutos=9,
            configurado_por="org",
        )
    )
    stub = StubCompetenciaEstadoAdapter()
    handler_ap = RegistrarAPHandler(store, stub)
    for atleta_id, valor in [(_A001, "300"), (_A002, "240")]:
        await handler_ap.handle(
            RegistrarAPCommand(
                competencia_id=comp_id,
                participante_id=atleta_id,
                disciplina=_DISCIPLINA,
                valor_ap=Decimal(valor),
                unidad=UnidadMedida.Segundos,
            )
        )
    adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter()).handle(
        GenerarGrillaCommand(
            competencia_id=comp_id,
            disciplina=_DISCIPLINA,
            ot_inicio=_OT_INICIO,
        )
    )


# ── Given ──────────────────────────────────────────────────────────────────────


@given(parsers.parse('la competencia "{comp}" tiene grilla generada y lista para confirmar'))
def given_con_grilla(ctx_214: dict, comp: str) -> None:
    asyncio.run(_seed_grilla(_store(ctx_214, comp), _cid(comp)))


@given(parsers.parse('la competencia "{comp}" no tiene grilla generada'))
def given_sin_grilla(ctx_214: dict, comp: str) -> None:  # noqa: ARG001
    pass  # C002 store vacío — no seed necesario


@given(parsers.parse('la grilla de "{comp}" ya fue confirmada previamente'))
def given_grilla_confirmada(ctx_214: dict, comp: str) -> None:
    store = _store(ctx_214, comp)
    comp_id = _cid(comp)

    async def _run() -> None:
        events = await store.load(f"competencia-{comp_id}")
        if not any(e["event_type"] == "GrillaDeSalidaGenerada" for e in events):
            await _seed_grilla(store, comp_id)
        # Re-cargar tras seed (si aplica) para no confirmar dos veces
        events2 = await store.load(f"competencia-{comp_id}")
        if not any(e["event_type"] == "GrillaConfirmada" for e in events2):
            await ConfirmarGrillaHandler(store).handle(
                ConfirmarGrillaCommand(comp_id, _DISCIPLINA)
            )

    asyncio.run(_run())


@given(parsers.parse('la competencia "{comp}" fue iniciada'))
def given_competencia_iniciada(ctx_214: dict, comp: str) -> None:
    store = _store(ctx_214, comp)
    comp_id = _cid(comp)

    async def _run() -> None:
        events = await store.load(f"competencia-{comp_id}")
        if not any(e["event_type"] == "GrillaDeSalidaGenerada" for e in events):
            await _seed_grilla(store, comp_id)
        events2 = await store.load(f"competencia-{comp_id}")
        if not any(e["event_type"] == "GrillaConfirmada" for e in events2):
            await ConfirmarGrillaHandler(store).handle(
                ConfirmarGrillaCommand(comp_id, _DISCIPLINA)
            )
        events3 = await store.load(f"competencia-{comp_id}")
        if not any(e["event_type"] == "CompetenciaIniciada" for e in events3):
            await IniciarCompetenciaHandler(store).handle(
                IniciarCompetenciaCommand(comp_id, _DISCIPLINA, "juez-bdd")
            )

    asyncio.run(_run())


# ── When ───────────────────────────────────────────────────────────────────────


@when(parsers.parse('el organizador confirma la grilla de "{comp}"'))
def when_confirmar(ctx_214: dict, comp: str) -> None:
    asyncio.run(
        ConfirmarGrillaHandler(_store(ctx_214, comp)).handle(
            ConfirmarGrillaCommand(_cid(comp), _DISCIPLINA)
        )
    )


@when(parsers.parse('el organizador intenta confirmar la grilla de "{comp}"'))
def when_intentar_confirmar(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        try:
            await ConfirmarGrillaHandler(_store(ctx_214, comp)).handle(
                ConfirmarGrillaCommand(_cid(comp), _DISCIPLINA)
            )
        except (GrillaNoGenerada, GrillaYaConfirmada) as exc:
            ctx_214["last_exception"] = exc

    asyncio.run(_run())


@when(parsers.parse('el organizador intenta confirmar la grilla de "{comp}" de nuevo'))
def when_confirmar_de_nuevo(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        try:
            await ConfirmarGrillaHandler(_store(ctx_214, comp)).handle(
                ConfirmarGrillaCommand(_cid(comp), _DISCIPLINA)
            )
        except GrillaYaConfirmada as exc:
            ctx_214["last_exception"] = exc

    asyncio.run(_run())


@when(parsers.parse('el juez inicia la competencia "{comp}"'))
def when_iniciar(ctx_214: dict, comp: str) -> None:
    asyncio.run(
        IniciarCompetenciaHandler(_store(ctx_214, comp)).handle(
            IniciarCompetenciaCommand(_cid(comp), _DISCIPLINA, "juez-bdd")
        )
    )


@when(parsers.parse('el juez intenta iniciar la competencia "{comp}" sin confirmar'))
def when_intentar_iniciar(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        try:
            await IniciarCompetenciaHandler(_store(ctx_214, comp)).handle(
                IniciarCompetenciaCommand(_cid(comp), _DISCIPLINA, "juez-bdd")
            )
        except CompetenciaNoConfirmada as exc:
            ctx_214["last_exception"] = exc

    asyncio.run(_run())


@when(parsers.parse('se consulta is_grilla_confirmada para "{comp}"'))
def when_is_grilla_confirmada(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        adapter = CompetenciaEstadoAdapter(_store(ctx_214, comp))
        ctx_214["adapter_result"] = await adapter.is_grilla_confirmada(_cid(comp), _DISCIPLINA)

    asyncio.run(_run())


@when(parsers.parse('se consulta is_en_ejecucion para "{comp}"'))
def when_is_en_ejecucion(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        adapter = CompetenciaEstadoAdapter(_store(ctx_214, comp))
        ctx_214["adapter_result"] = await adapter.is_en_ejecucion(_cid(comp))

    asyncio.run(_run())


# ── Then ───────────────────────────────────────────────────────────────────────


@then(parsers.parse('el evento GrillaConfirmada persiste en el stream de "{comp}"'))
def then_grilla_confirmada_persiste(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        events = await _store(ctx_214, comp).load(f"competencia-{_cid(comp)}")
        assert any(e["event_type"] == "GrillaConfirmada" for e in events)

    asyncio.run(_run())


@then(parsers.parse('la competencia "{comp}" está en estado "{estado}"'))
def then_estado(ctx_214: dict, comp: str, estado: str) -> None:
    async def _run() -> None:
        events = await _store(ctx_214, comp).load(f"competencia-{_cid(comp)}")
        c = Competencia.reconstitute(_cid(comp), _DISCIPLINA, events)
        assert c.estado == EstadoCompetencia(estado)

    asyncio.run(_run())


@then(parsers.parse('GenerarGrilla queda bloqueado para "{comp}"'))
def then_generar_grilla_bloqueado(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        events = await _store(ctx_214, comp).load(f"competencia-{_cid(comp)}")
        c = Competencia.reconstitute(_cid(comp), _DISCIPLINA, events)
        assert c.grilla_confirmada is True

    asyncio.run(_run())


@then(parsers.parse('la confirmación de "{comp}" es rechazada con "{exc_name}"'))
def then_confirmacion_rechazada(ctx_214: dict, comp: str, exc_name: str) -> None:  # noqa: ARG001
    exc = ctx_214["last_exception"]
    assert exc is not None, f"Se esperaba {exc_name} pero no se lanzó ninguna excepción"
    assert type(exc).__name__ == exc_name


@then(parsers.parse('el evento CompetenciaIniciada persiste en el stream de "{comp}"'))
def then_competencia_iniciada_persiste(ctx_214: dict, comp: str) -> None:
    async def _run() -> None:
        events = await _store(ctx_214, comp).load(f"competencia-{_cid(comp)}")
        assert any(e["event_type"] == "CompetenciaIniciada" for e in events)

    asyncio.run(_run())


@then(parsers.parse('el inicio de "{comp}" es rechazado con "{exc_name}"'))
def then_inicio_rechazado(ctx_214: dict, comp: str, exc_name: str) -> None:  # noqa: ARG001
    exc = ctx_214["last_exception"]
    assert exc is not None, f"Se esperaba {exc_name} pero no se lanzó ninguna excepción"
    assert type(exc).__name__ == exc_name


@then("el adaptador retorna True")
def then_adaptador_true(ctx_214: dict) -> None:
    assert ctx_214["adapter_result"] is True
