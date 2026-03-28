"""Step definitions BDD — US-2.1.2: Generar Grilla de Salida."""
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
from competencia.application.commands._stream_ids import competencia_stream_id as _build_stream_id
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.exceptions import (
    GrillaYaConfirmada,
    IntervaloNoConfigurado,
    SinPerformancesParaGrilla,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
from competencia.infrastructure.repositories.performances_ap_adapter import (
    PerformancesAPAdapter,
)

scenarios("../US-2.1.2-generar-grilla.feature")

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

_C001 = UUID("00000000-0000-0000-0000-000000000001")
_C002 = UUID("00000000-0000-0000-0000-000000000002")
_C003 = UUID("00000000-0000-0000-0000-000000000003")
_ORG = "organizador-01"

_ATLETA_IDS: dict[str, UUID] = {
    "A001": UUID("00000000-0000-0000-0000-000000000011"),
    "A002": UUID("00000000-0000-0000-0000-000000000012"),
    "A003": UUID("00000000-0000-0000-0000-000000000013"),
}


def _make_store(tmp_path: str, name: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_{name}.db"
    asyncio.run(_create_db(db_path))
    return SQLiteEventStore(db_path)


async def _create_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


@pytest.fixture
def context(tmp_path: object) -> dict:
    return {
        "store_c001": _make_store(str(tmp_path), "c001"),
        "store_c002": _make_store(str(tmp_path), "c002"),
        "store_c003": _make_store(str(tmp_path), "c003"),
        "active_store": None,
        "active_competencia_id": _C001,
        "active_disciplina": Disciplina.STA,
        "active_ot_inicio": datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc),
        "raised_exception": None,
        "grilla_result": None,
    }


def _get_store(context: dict) -> SQLiteEventStore:
    return context["active_store"] or context["store_c001"]


# ── Given ─────────────────────────────────────────────────────────────────────

@given(parsers.parse('una competencia "{cid}" con disciplina "STA" en estado "Preparacion"'))
def dada_competencia_sta(context: dict, cid: str) -> None:
    context["active_competencia_id"] = _C001
    context["active_disciplina"] = Disciplina.STA
    context["active_store"] = context["store_c001"]


@given(parsers.parse('el intervalo OT está configurado en {minutos:d} minutos'))
def dado_intervalo(context: dict, minutos: int) -> None:
    store = _get_store(context)
    cid = context["active_competencia_id"]
    disciplina = context["active_disciplina"]
    cmd = ConfigurarIntervaloOTCommand(
        competencia_id=cid,
        disciplina=disciplina,
        intervalo_minutos=minutos,
        configurado_por=_ORG,
    )
    asyncio.run(ConfigurarIntervaloOTHandler(store).handle(cmd))


@given(parsers.parse('OT de inicio es "{ot_str}"'))
def dado_ot_inicio(context: dict, ot_str: str) -> None:
    h, m, s = map(int, ot_str.split(":"))
    context["active_ot_inicio"] = datetime(2026, 1, 1, h, m, s, tzinfo=timezone.utc)


@given("los siguientes APs registrados para STA:", target_fixture="aps_sta")
def dados_aps_sta(context: dict, datatable: object) -> None:
    store = _get_store(context)
    stub = StubCompetenciaEstadoAdapter()
    handler = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    rows = datatable[1:]  # skip header
    for row in rows:
        atleta_str, ap_str = row[0].strip(), row[1].strip()
        atleta_id = _ATLETA_IDS.get(atleta_str, uuid4())
        asyncio.run(
            handler.handle(
                RegistrarAPCommand(
                    competencia_id=context["active_competencia_id"],
                    participante_id=atleta_id,
                    disciplina=context["active_disciplina"],
                    valor_ap=Decimal(ap_str),
                    unidad=UnidadMedida.Segundos,
                )
            )
        )


@given("la grilla ya fue generada previamente")
def dada_grilla_generada(context: dict) -> None:
    store = _get_store(context)
    adapter = PerformancesAPAdapter(store)
    handler = GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter())
    asyncio.run(
        handler.handle(
            GenerarGrillaCommand(
                competencia_id=context["active_competencia_id"],
                disciplina=context["active_disciplina"],
                ot_inicio=context["active_ot_inicio"],
            )
        )
    )


@given('una competencia "C003" sin intervalo OT configurado')
def dada_competencia_sin_intervalo(context: dict) -> None:
    context["active_competencia_id"] = _C003
    context["active_disciplina"] = Disciplina.STA
    context["active_store"] = context["store_c003"]


@given("la grilla ya fue confirmada")
def dada_grilla_confirmada(context: dict) -> None:
    store = _get_store(context)
    cid = context["active_competencia_id"]
    asyncio.run(
        store.append(
            stream_id=_build_stream_id(cid),
            event_type="GrillaConfirmada",
            payload={"competencia_id": str(cid)},
        )
    )


@given(parsers.parse('una competencia "C002" con disciplina "DNF" e intervalo {minutos:d} minutos'))
def dada_competencia_dnf(context: dict, minutos: int) -> None:
    context["active_competencia_id"] = _C002
    context["active_disciplina"] = Disciplina.DNF
    context["active_store"] = context["store_c002"]
    store = context["store_c002"]
    asyncio.run(
        ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=_C002,
                disciplina=Disciplina.DNF,
                intervalo_minutos=minutos,
                configurado_por=_ORG,
            )
        )
    )


@given("los siguientes APs registrados para DNF:", target_fixture="aps_dnf")
def dados_aps_dnf(context: dict, datatable: object) -> None:
    store = _get_store(context)
    stub = StubCompetenciaEstadoAdapter()
    handler = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    rows = datatable[1:]
    for row in rows:
        atleta_str, ap_str = row[0].strip(), row[1].strip()
        atleta_id = _ATLETA_IDS.get(atleta_str, uuid4())
        asyncio.run(
            handler.handle(
                RegistrarAPCommand(
                    competencia_id=_C002,
                    participante_id=atleta_id,
                    disciplina=Disciplina.DNF,
                    valor_ap=Decimal(ap_str),
                    unidad=UnidadMedida.Metros,
                )
            )
        )


# ── When ──────────────────────────────────────────────────────────────────────

@when("el organizador genera la grilla")
def cuando_genera_grilla(context: dict) -> None:
    _ejecutar_generar_grilla(context)


@when("el organizador regenera la grilla")
def cuando_regenera_grilla(context: dict) -> None:
    _ejecutar_generar_grilla(context)


@when("el organizador intenta generar la grilla sin intervalo")
def cuando_intenta_sin_intervalo(context: dict) -> None:
    _ejecutar_generar_grilla(context)


@when("el organizador intenta regenerar la grilla")
def cuando_intenta_regenerar(context: dict) -> None:
    _ejecutar_generar_grilla(context)


@when(parsers.parse('se genera la grilla con OT inicio "{ot_str}"'))
def cuando_genera_grilla_dnf(context: dict, ot_str: str) -> None:
    h, m, s = map(int, ot_str.split(":"))
    context["active_ot_inicio"] = datetime(2026, 1, 1, h, m, s, tzinfo=timezone.utc)
    _ejecutar_generar_grilla(context)


def _ejecutar_generar_grilla(context: dict) -> None:
    store = _get_store(context)
    adapter = PerformancesAPAdapter(store)
    handler = GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter())
    try:
        asyncio.run(
            handler.handle(
                GenerarGrillaCommand(
                    competencia_id=context["active_competencia_id"],
                    disciplina=context["active_disciplina"],
                    ot_inicio=context["active_ot_inicio"],
                )
            )
        )
    except (IntervaloNoConfigurado, GrillaYaConfirmada, SinPerformancesParaGrilla) as exc:
        context["raised_exception"] = exc


# ── Then ──────────────────────────────────────────────────────────────────────

@then(parsers.parse("la grilla tiene {n:d} atletas"))
def entonces_grilla_tiene_n_atletas(context: dict, n: int) -> None:
    perfs = _get_grilla_perfs(context)
    assert len(perfs) == n


@then(parsers.parse('la posicion {pos:d} corresponde al atleta "{atleta}" con OT "{ot_str}"'))
def entonces_posicion_atleta_ot(context: dict, pos: int, atleta: str, ot_str: str) -> None:
    perfs = _get_grilla_perfs(context)
    entrada = next(p for p in perfs if p["posicion"] == pos)
    assert entrada["atleta_id"] == str(_ATLETA_IDS[atleta])
    h, m, s = map(int, ot_str.split(":"))
    expected_ot = datetime(2026, 1, 1, h, m, s, tzinfo=timezone.utc)
    assert datetime.fromisoformat(entrada["ot_programado"]) == expected_ot


@then("el evento GrillaDeSalidaGenerada persiste en el stream")
def entonces_evento_persiste(context: dict) -> None:
    store = _get_store(context)
    cid = context["active_competencia_id"]
    events = asyncio.run(store.load(_build_stream_id(cid)))
    assert any(e["event_type"] == "GrillaDeSalidaGenerada" for e in events)


@then(parsers.parse('"{atleta}" aparece en la grilla'))
def entonces_atleta_aparece(context: dict, atleta: str) -> None:
    perfs = _get_grilla_perfs(context)
    atleta_ids = [p["atleta_id"] for p in perfs]
    assert str(_ATLETA_IDS[atleta]) in atleta_ids


@then("se emite un nuevo GrillaDeSalidaGenerada")
def entonces_nuevo_evento(context: dict) -> None:
    entonces_evento_persiste(context)


@then("hay 2 eventos GrillaDeSalidaGenerada en el stream")
def entonces_dos_eventos_grilla(context: dict) -> None:
    store = _get_store(context)
    cid = context["active_competencia_id"]
    events = asyncio.run(store.load(_build_stream_id(cid)))
    grilla_events = [e for e in events if e["event_type"] == "GrillaDeSalidaGenerada"]
    assert len(grilla_events) == 2


@then(parsers.parse('el sistema rechaza con error "{error_type}"'))
def entonces_rechaza(context: dict, error_type: str) -> None:
    assert context["raised_exception"] is not None
    assert type(context["raised_exception"]).__name__ == error_type


@then(parsers.parse('la posicion {pos:d} corresponde al atleta "{atleta}"'))
def entonces_posicion_atleta(context: dict, pos: int, atleta: str) -> None:
    perfs = _get_grilla_perfs(context)
    entrada = next(p for p in perfs if p["posicion"] == pos)
    assert entrada["atleta_id"] == str(_ATLETA_IDS[atleta])


# ── Helpers ───────────────────────────────────────────────────────────────────

def _get_grilla_perfs(context: dict) -> list[dict]:
    store = _get_store(context)
    cid = context["active_competencia_id"]
    events = asyncio.run(store.load(_build_stream_id(cid)))
    grilla_events = [e for e in events if e["event_type"] == "GrillaDeSalidaGenerada"]
    assert grilla_events, "No se encontró evento GrillaDeSalidaGenerada"
    return grilla_events[-1]["payload"]["performances"]
