"""Tests de integración — LlamarAtletaHandler con SQLiteEventStore real."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest

from competencia.application.commands.llamar_atleta import (
    CompetenciaNoEnEjecucion,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
    PerformanceNoEncontrada,
)
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import EstadoInvalidoParaLlamar
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
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
def registrar_handler(event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter) -> RegistrarAPHandler:
    return RegistrarAPHandler(event_store=event_store, competencia_estado=stub, disciplina_descriptor=DisciplinaDescriptorAdapter())


@pytest.fixture
def llamar_handler(event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter) -> LlamarAtletaHandler:
    return LlamarAtletaHandler(event_store=event_store, competencia_estado=stub)


# ── Flujo completo ────────────────────────────────────────────────────────────


async def test_flujo_registrar_ap_luego_llamar(
    registrar_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Flujo completo: RegistrarAP → LlamarAtleta → estado Llamada en el stream."""
    cid = uuid4()
    pid = uuid4()

    # 1. Registrar AP
    await registrar_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_ap=Decimal("330"),
            unidad=UnidadMedida.Segundos,
        )
    )

    # 2. Llamar atleta
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )

    # 3. Verificar stream: 2 eventos, segundo = AtletaLlamado
    stream_id = f"performance-{cid}-{pid}-{Disciplina.STA.value}"
    events = await event_store.load(stream_id)
    assert len(events) == 2
    assert events[1]["event_type"] == "AtletaLlamado"

    # 4. Reconstituir → estado Llamada
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.Llamada


async def test_llamar_persiste_payload_correcto(
    registrar_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    event_store: SQLiteEventStore,
) -> None:
    """El payload de AtletaLlamado contiene posicion_grilla y ot_programado."""
    cid = uuid4()
    pid = uuid4()

    await registrar_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, valor_ap=Decimal("80"), unidad=UnidadMedida.Metros,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, ot_programado=OT, posicion_grilla=4,
        )
    )

    stream_id = f"performance-{cid}-{pid}-DNF"
    events = await event_store.load(stream_id)
    payload = events[1]["payload"]
    assert payload["posicion_grilla"] == 4
    assert payload["ot_programado"] == OT.isoformat()


async def test_llamar_sin_ap_previo_lanza_error(
    llamar_handler: LlamarAtletaHandler,
) -> None:
    """PerformanceNoEncontrada si se intenta llamar sin AP registrado."""
    with pytest.raises(PerformanceNoEncontrada):
        await llamar_handler.handle(
            LlamarAtletaCommand(
                competencia_id=uuid4(), participante_id=uuid4(),
                disciplina=Disciplina.STA, ot_programado=OT, posicion_grilla=1,
            )
        )


async def test_llamar_dos_veces_lanza_error(
    registrar_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
) -> None:
    """EstadoInvalidoParaLlamar si se llama al mismo atleta dos veces."""
    cid = uuid4()
    pid = uuid4()
    cmd_ap = RegistrarAPCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, valor_ap=Decimal("330"), unidad=UnidadMedida.Segundos,
    )
    cmd_llamar = LlamarAtletaCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, ot_programado=OT, posicion_grilla=2,
    )

    await registrar_handler.handle(cmd_ap)
    await llamar_handler.handle(cmd_llamar)

    with pytest.raises(EstadoInvalidoParaLlamar):
        await llamar_handler.handle(cmd_llamar)
