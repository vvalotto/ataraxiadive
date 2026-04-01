"""Step definitions BDD — US-2.1.3: Ajustar Grilla Manualmente."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.ajustar_grilla import (
    AjustarGrillaCommand,
    AjustarGrillaHandler,
    _build_stream_id,
)
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
from competencia.domain.exceptions import GrillaNoGenerada, GrillaYaConfirmada
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter

scenarios("../US-2.1.3-ajustar-grilla.feature")

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
_ORG = "organizador-01"
_OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

_ATLETA_IDS: dict[str, UUID] = {
    "A001": UUID("00000000-0000-0000-0000-000000000011"),
    "A002": UUID("00000000-0000-0000-0000-000000000012"),
    "A003": UUID("00000000-0000-0000-0000-000000000013"),
}

_CID_MAP: dict[str, UUID] = {"C001": _C001, "C002": _C002}


def _make_store(tmp_path: str, name: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_ajustar_{name}.db"
    asyncio.run(_create_db(db_path))
    return SQLiteEventStore(db_path)


async def _create_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()


@pytest.fixture
def ctx_ajustar(tmp_path: object) -> dict:
    return {
        "store_c001": _make_store(str(tmp_path), "c001"),
        "store_c002": _make_store(str(tmp_path), "c002"),
        "perf_ids": {},  # atleta_id → performance_id (para C001)
        "raised": {},  # cid_str → exception
    }


def _store(ctx: dict, cid_str: str) -> SQLiteEventStore:
    key = f"store_{cid_str.lower()}"
    return ctx[key]


# ── Helpers async ─────────────────────────────────────────────────────────────


async def _seed_grilla_c001(store: SQLiteEventStore, ctx: dict) -> None:
    """Seed C001: intervalo 9min + APs (A002=360, A001=330, A003=285) + grilla generada."""
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=_C001,
            disciplina=Disciplina.STA,
            intervalo_minutos=9,
            configurado_por=_ORG,
        )
    )
    stub = StubCompetenciaEstadoAdapter()
    handler_ap = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    for atleta_str, valor in [("A002", "360"), ("A001", "330"), ("A003", "285")]:
        await handler_ap.handle(
            RegistrarAPCommand(
                competencia_id=_C001,
                participante_id=_ATLETA_IDS[atleta_str],
                disciplina=Disciplina.STA,
                valor_ap=Decimal(valor),
                unidad=UnidadMedida.Segundos,
            )
        )

    adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter()).handle(
        GenerarGrillaCommand(
            competencia_id=_C001,
            disciplina=Disciplina.STA,
            ot_inicio=_OT_INICIO,
        )
    )

    events = await store.load(_build_stream_id(_C001))
    grilla_event = next(e for e in events if e["event_type"] == "GrillaDeSalidaGenerada")
    ctx["perf_ids"] = {
        UUID(p["atleta_id"]): UUID(p["performance_id"])
        for p in grilla_event["payload"]["performances"]
    }


# ── Given ─────────────────────────────────────────────────────────────────────


@given(
    parsers.parse(
        'la competencia "{cid}" tiene grilla generada con 3 atletas STA e intervalo 9 min'
    )
)
def dada_competencia_con_grilla(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    asyncio.run(_seed_grilla_c001(store, ctx_ajustar))


@given(parsers.parse('la competencia "{cid}" tiene solo el intervalo configurado (sin grilla)'))
def dada_competencia_sin_grilla(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    asyncio.run(
        ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=_CID_MAP[cid],
                disciplina=Disciplina.STA,
                intervalo_minutos=9,
                configurado_por=_ORG,
            )
        )
    )


@given(parsers.parse('ya se aplicó un ajuste previo en "{cid}" (A001 a posicion 1)'))
def dado_ajuste_previo(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    p_a001 = ctx_ajustar["perf_ids"][_ATLETA_IDS["A001"]]
    asyncio.run(
        AjustarGrillaHandler(store).handle(
            AjustarGrillaCommand(
                competencia_id=_CID_MAP[cid],
                disciplina=Disciplina.STA,
                cambios=[CambioGrilla(performance_id=p_a001, campo="posicion", valor_nuevo=1)],
            )
        )
    )


@given(parsers.parse('la grilla de "{cid}" está confirmada'))
def dada_grilla_confirmada_ajuste(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    cid_uuid = _CID_MAP[cid]
    asyncio.run(
        store.append(
            stream_id=_build_stream_id(cid_uuid),
            event_type="GrillaConfirmada",
            payload={"competencia_id": str(cid_uuid)},
        )
    )


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('el organizador ajusta la posicion del atleta "{atleta}" a {pos:d} en "{cid}"'))
def cuando_ajusta_posicion(ctx_ajustar: dict, atleta: str, pos: int, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    p_id = ctx_ajustar["perf_ids"][_ATLETA_IDS[atleta]]
    _ejecutar_ajuste(
        ctx_ajustar,
        cid,
        store,
        [CambioGrilla(performance_id=p_id, campo="posicion", valor_nuevo=pos)],
    )


@when(
    parsers.parse('el organizador asigna andarivel {andarivel:d} al atleta "{atleta}" en "{cid}"')
)
def cuando_ajusta_andarivel(ctx_ajustar: dict, atleta: str, andarivel: int, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    p_id = ctx_ajustar["perf_ids"][_ATLETA_IDS[atleta]]
    _ejecutar_ajuste(
        ctx_ajustar,
        cid,
        store,
        [CambioGrilla(performance_id=p_id, campo="andarivel", valor_nuevo=andarivel)],
    )


@when(parsers.parse('el organizador intenta ajustar la grilla de "{cid}"'))
def cuando_intenta_ajustar(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    pid = ctx_ajustar["perf_ids"].get(_ATLETA_IDS.get("A001", uuid4()), uuid4())
    _ejecutar_ajuste(
        ctx_ajustar,
        cid,
        store,
        [CambioGrilla(performance_id=pid, campo="posicion", valor_nuevo=1)],
    )


def _ejecutar_ajuste(
    ctx: dict, cid: str, store: SQLiteEventStore, cambios: list[CambioGrilla]
) -> None:
    try:
        asyncio.run(
            AjustarGrillaHandler(store).handle(
                AjustarGrillaCommand(
                    competencia_id=_CID_MAP[cid],
                    disciplina=Disciplina.STA,
                    cambios=cambios,
                )
            )
        )
    except (GrillaNoGenerada, GrillaYaConfirmada) as exc:
        ctx["raised"][cid] = exc


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('la grilla de "{cid}" queda: "{a1}" en posicion 1, "{a2}" en posicion 2'))
def entonces_posiciones(ctx_ajustar: dict, cid: str, a1: str, a2: str) -> None:
    perfs = _get_grilla_state(ctx_ajustar, cid)
    pos1 = next(p for p in perfs if p["posicion"] == 1)
    pos2 = next(p for p in perfs if p["posicion"] == 2)
    assert pos1["atleta_id"] == str(_ATLETA_IDS[a1])
    assert pos2["atleta_id"] == str(_ATLETA_IDS[a2])


@then(parsers.parse('los OTs de "{cid}" son: posicion 1 = "{ot1}", posicion 2 = "{ot2}"'))
def entonces_ots(ctx_ajustar: dict, cid: str, ot1: str, ot2: str) -> None:
    perfs = _get_grilla_state(ctx_ajustar, cid)
    p1 = next(p for p in perfs if p["posicion"] == 1)
    p2 = next(p for p in perfs if p["posicion"] == 2)
    _assert_ot(p1["ot_programado"], ot1)
    _assert_ot(p2["ot_programado"], ot2)


@then(parsers.parse('el evento GrillaDeSalidaAjustada persiste en el stream de "{cid}"'))
def entonces_evento_ajustada_persiste(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    events = asyncio.run(store.load(_build_stream_id(_CID_MAP[cid])))
    assert any(e["event_type"] == "GrillaDeSalidaAjustada" for e in events)


@then(parsers.parse('el atleta "{atleta}" en "{cid}" queda con andarivel {andarivel:d}'))
def entonces_andarivel(ctx_ajustar: dict, atleta: str, cid: str, andarivel: int) -> None:
    perfs = _get_grilla_state(ctx_ajustar, cid)
    p = next(e for e in perfs if e["atleta_id"] == str(_ATLETA_IDS[atleta]))
    assert p["andarivel"] == andarivel


@then(parsers.parse('los atletas "{a1}" y "{a2}" de "{cid}" mantienen andarivel {andarivel:d}'))
def entonces_andarivel_sin_cambio(
    ctx_ajustar: dict, a1: str, a2: str, cid: str, andarivel: int
) -> None:
    perfs = _get_grilla_state(ctx_ajustar, cid)
    for atleta in (a1, a2):
        p = next(e for e in perfs if e["atleta_id"] == str(_ATLETA_IDS[atleta]))
        assert p["andarivel"] == andarivel


@then(parsers.parse('hay 2 eventos GrillaDeSalidaAjustada en el stream de "{cid}"'))
def entonces_dos_eventos_ajustada(ctx_ajustar: dict, cid: str) -> None:
    store = _store(ctx_ajustar, cid)
    events = asyncio.run(store.load(_build_stream_id(_CID_MAP[cid])))
    ajuste_events = [e for e in events if e["event_type"] == "GrillaDeSalidaAjustada"]
    assert len(ajuste_events) == 2


@then(parsers.parse('el ajuste de "{cid}" es rechazado con "{error_type}"'))
def entonces_rechazado(ctx_ajustar: dict, cid: str, error_type: str) -> None:
    exc = ctx_ajustar["raised"].get(cid)
    assert exc is not None, f"Se esperaba excepción {error_type} pero no se lanzó"
    assert type(exc).__name__ == error_type


# ── Helpers ───────────────────────────────────────────────────────────────────


def _get_grilla_state(ctx: dict, cid: str) -> list[dict]:
    """Reconstruye la grilla final desde el event store (último estado)."""
    store = _store(ctx, cid)
    cid_uuid = _CID_MAP[cid]
    from competencia.domain.aggregates.competencia import Competencia

    events = asyncio.run(store.load(_build_stream_id(cid_uuid)))
    c = Competencia.reconstitute(cid_uuid, Disciplina.STA, events)
    return [
        {
            "atleta_id": str(e.atleta_id),
            "posicion": e.posicion,
            "andarivel": e.andarivel,
            "ot_programado": e.ot_programado.isoformat(),
        }
        for e in c.grilla
    ]


def _assert_ot(ot_iso: str, expected_str: str) -> None:
    h, m, s = map(int, expected_str.split(":"))
    expected = datetime(2026, 1, 1, h, m, s, tzinfo=timezone.utc)
    assert datetime.fromisoformat(ot_iso) == expected
