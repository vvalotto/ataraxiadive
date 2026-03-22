"""Tests de integración — RegistrarResultadoHandler con SQLiteEventStore real."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest

from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import EstadoInvalidoParaRegistrarResultado, Performance
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

OT = datetime(2026, 3, 22, 10, 30, 0)

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


@pytest.fixture
async def event_store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    """SQLiteEventStore sobre SQLite en disco temporal."""
    db_path = str(tmp_path / "competencia_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def stub() -> StubCompetenciaEstadoAdapter:
    return StubCompetenciaEstadoAdapter()


@pytest.fixture
def registrar_ap_handler(
    event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter
) -> RegistrarAPHandler:
    return RegistrarAPHandler(event_store=event_store, competencia_estado=stub)


@pytest.fixture
def llamar_handler(
    event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter
) -> LlamarAtletaHandler:
    return LlamarAtletaHandler(event_store=event_store, competencia_estado=stub)


@pytest.fixture
def resultado_handler(event_store: SQLiteEventStore) -> RegistrarResultadoHandler:
    return RegistrarResultadoHandler(event_store=event_store)


# ── Flujo completo ────────────────────────────────────────────────────────────


async def test_flujo_ap_llamar_resultado(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Flujo completo: RegistrarAP → LlamarAtleta → RegistrarResultado."""
    cid = uuid4()
    pid = uuid4()

    # 1. Registrar AP
    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal("50"),
            unidad=UnidadMedida.Metros,
        )
    )

    # 2. Llamar atleta
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )

    # 3. Registrar resultado
    await resultado_handler.handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("50.5"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-001",
        )
    )

    # 4. Verificar stream: 3 eventos, tercero = ResultadoRegistrado
    stream_id = f"performance-{cid}-{pid}-{Disciplina.DNF.value}"
    events = await event_store.load(stream_id)
    assert len(events) == 3
    assert events[2]["event_type"] == "ResultadoRegistrado"

    # 5. Reconstituir → estado ResultadoRegistrado
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.ResultadoRegistrado
    assert performance.rp == Decimal("50.5")


async def test_resultado_persiste_payload_correcto(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    event_store: SQLiteEventStore,
) -> None:
    """El payload de ResultadoRegistrado contiene valorRP, unidad y registradoPor."""
    cid = uuid4()
    pid = uuid4()

    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, valor_ap=Decimal("50"), unidad=UnidadMedida.Metros,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, ot_programado=OT, posicion_grilla=2,
        )
    )
    await resultado_handler.handle(
        RegistrarResultadoCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, valor_rp=Decimal("48.3"),
            unidad=UnidadMedida.Metros, registrado_por="juez-007",
        )
    )

    stream_id = f"performance-{cid}-{pid}-DNF"
    events = await event_store.load(stream_id)
    payload = events[2]["payload"]
    assert payload["valor_rp"] == "48.3"
    assert payload["unidad"] == "Metros"
    assert payload["registrado_por"] == "juez-007"


async def test_resultado_desde_anunciada_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    resultado_handler: RegistrarResultadoHandler,
) -> None:
    """INV-P-06: EstadoInvalidoParaRegistrarResultado si Performance en AnunciadaAP."""
    cid = uuid4()
    pid = uuid4()

    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, valor_ap=Decimal("50"), unidad=UnidadMedida.Metros,
        )
    )

    with pytest.raises(EstadoInvalidoParaRegistrarResultado):
        await resultado_handler.handle(
            RegistrarResultadoCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF, valor_rp=Decimal("50"),
                unidad=UnidadMedida.Metros, registrado_por="juez-001",
            )
        )
