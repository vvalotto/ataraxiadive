"""Step definitions BDD — US-5.5.1: Registro de APs del atleta (portal atleta)."""

from __future__ import annotations

import asyncio
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.registrar_ap import (
    APYaRegistrado,
    GrillaYaConfirmadaError,
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.application.commands.registrar_resultado import UnidadIncompatible
from competencia.domain.value_objects.ap import ValorAPInvalido
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

scenarios("../US-5.5.1-registro-aps.feature")

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

COMPETENCIA_DNF_ID = UUID("00000000-0000-0000-0000-000000005501")
ANA_ID = UUID("aaaaaaaa-0000-0000-0000-000000005501")


def _make_store(tmp_path: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_5_5_1.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


@pytest.fixture
def ctx(tmp_path):
    return {
        "event_store": _make_store(str(tmp_path)),
        "estado_port": StubCompetenciaEstadoAdapter(),
        "status_code": None,
        "excepcion": None,
        "performance_id": None,
    }


# ── Background ────────────────────────────────────────────────────────────────


@given(parsers.parse('existe el torneo "BA Open 2026" con disciplinas DNF y STA'))
def given_torneo(ctx):
    pass


@given("existen competencias creadas para DNF y STA")
def given_competencias(ctx):
    pass


@given(parsers.parse('la atleta "{email}" esta inscripta en DNF y STA'))
def given_atleta_inscripta(ctx, email):
    pass


@given("la grilla de DNF y STA no esta confirmada")
def given_grilla_no_confirmada(ctx):
    pass


# ── Givens específicos ────────────────────────────────────────────────────────


@given(parsers.parse('"{email}" esta autenticada con rol ATLETA'))
def given_autenticada(ctx, email):
    pass  # el estado_port ya es el stub (grilla no confirmada)


@given(parsers.parse('"{email}" ya registro AP {valor:d} para DNF'))
def given_ya_registro_ap(ctx, email, valor):
    handler = RegistrarAPHandler(
        ctx["event_store"], ctx["estado_port"], DisciplinaDescriptorAdapter()
    )
    cmd = RegistrarAPCommand(
        competencia_id=COMPETENCIA_DNF_ID,
        participante_id=ANA_ID,
        disciplina=Disciplina.DNF,
        valor_ap=Decimal(str(valor)),
        unidad=UnidadMedida.Metros,
    )
    asyncio.run(handler.handle(cmd))


@given("la grilla de DNF esta confirmada")
def given_grilla_confirmada(ctx):
    stub = AsyncMock(spec=StubCompetenciaEstadoAdapter)
    stub.is_plazo_vencido.return_value = False
    stub.is_grilla_confirmada.return_value = True
    ctx["estado_port"] = stub


# ── When ──────────────────────────────────────────────────────────────────────


@when(
    parsers.parse("registra AP con disciplina {disciplina}, valor_ap {valor:d} y unidad {unidad}")
)
def when_registra_ap(ctx, disciplina, valor, unidad):
    unidad_enum = UnidadMedida.Metros if unidad == "Metros" else UnidadMedida.Segundos
    disciplina_enum = Disciplina[disciplina]
    handler = RegistrarAPHandler(
        ctx["event_store"], ctx["estado_port"], DisciplinaDescriptorAdapter()
    )
    cmd = RegistrarAPCommand(
        competencia_id=COMPETENCIA_DNF_ID,
        participante_id=ANA_ID,
        disciplina=disciplina_enum,
        valor_ap=Decimal(str(valor)),
        unidad=unidad_enum,
    )
    try:
        ctx["performance_id"] = asyncio.run(handler.handle(cmd))
        ctx["status_code"] = 201
        ctx["excepcion"] = None
    except (APYaRegistrado, GrillaYaConfirmadaError) as exc:
        ctx["excepcion"] = exc
        ctx["status_code"] = 409
    except (UnidadIncompatible, ValorAPInvalido) as exc:
        ctx["excepcion"] = exc
        ctx["status_code"] = 422


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("el sistema responde {codigo:d}"))
def then_responde_codigo(ctx, codigo):
    assert (
        ctx["status_code"] == codigo
    ), f"Esperado {codigo}, obtenido {ctx['status_code']} (exc={ctx['excepcion']})"


@then(parsers.parse("existe un Performance en estado AnunciadaAP para ana y {disciplina}"))
def then_performance_anunciada(ctx, disciplina):
    from competencia.domain.aggregates.performance import Performance

    store = ctx["event_store"]
    stream_id = f"performance-{COMPETENCIA_DNF_ID}-{ANA_ID}-{disciplina}"
    events = asyncio.run(store.load(stream_id))
    assert events, f"No hay eventos en stream {stream_id}"
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.AnunciadaAP


@then(parsers.parse('el mensaje de error contiene "{texto}"'))
def then_mensaje_contiene(ctx, texto):
    assert ctx["excepcion"] is not None
    assert texto in str(ctx["excepcion"]), f"'{texto}' no en '{ctx['excepcion']}'"
