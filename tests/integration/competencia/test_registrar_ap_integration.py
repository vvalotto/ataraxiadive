"""Tests de integración — RegistrarAPHandler con SQLiteEventStore real."""
from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest

from competencia.application.commands.registrar_ap import (
    APYaRegistrado,
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

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
def handler(event_store: SQLiteEventStore) -> RegistrarAPHandler:
    return RegistrarAPHandler(
        event_store=event_store,
        competencia_estado=StubCompetenciaEstadoAdapter(),
    )


# ── Flujo completo ────────────────────────────────────────────────────────────


async def test_registrar_ap_persiste_y_recarga(
    handler: RegistrarAPHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Flujo completo: handler → event store → reconstitute."""
    cid = uuid4()
    pid = uuid4()
    cmd = RegistrarAPCommand(
        competencia_id=cid,
        participante_id=pid,
        disciplina=Disciplina.STA,
        valor_ap=Decimal("330"),
        unidad=UnidadMedida.Segundos,
    )

    performance_id = await handler.handle(cmd)
    assert performance_id is not None

    # Cargar stream y reconstituir aggregate
    stream_id = f"performance-{cid}-{pid}-{Disciplina.STA.value}"
    events = await event_store.load(stream_id)
    assert len(events) == 1
    assert events[0]["event_type"] == "APRegistrado"

    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.AnunciadaAP
    assert performance.ap is not None
    assert performance.ap.valor == Decimal("330")


async def test_registrar_ap_payload_contiene_ids_correctos(
    handler: RegistrarAPHandler,
    event_store: SQLiteEventStore,
) -> None:
    """El payload del evento persiste los IDs del comando."""
    cid = uuid4()
    pid = uuid4()
    cmd = RegistrarAPCommand(
        competencia_id=cid,
        participante_id=pid,
        disciplina=Disciplina.DNF,
        valor_ap=Decimal("80"),
        unidad=UnidadMedida.Metros,
    )
    await handler.handle(cmd)

    stream_id = f"performance-{cid}-{pid}-DNF"
    events = await event_store.load(stream_id)
    payload = events[0]["payload"]
    assert payload["competencia_id"] == str(cid)
    assert payload["participante_id"] == str(pid)
    assert payload["disciplina"] == "DNF"
    assert payload["valor_ap"] == "80"
    assert payload["unidad"] == "Metros"


async def test_segunda_llamada_misma_combinacion_lanza_error(
    handler: RegistrarAPHandler,
) -> None:
    """INV-P-02: segunda llamada con misma (competencia, participante, disciplina)."""
    cid = uuid4()
    pid = uuid4()
    cmd = RegistrarAPCommand(
        competencia_id=cid,
        participante_id=pid,
        disciplina=Disciplina.CWT,
        valor_ap=Decimal("40"),
        unidad=UnidadMedida.Metros,
    )

    await handler.handle(cmd)

    with pytest.raises(APYaRegistrado):
        await handler.handle(cmd)


async def test_distinta_disciplina_mismo_atleta_es_independiente(
    handler: RegistrarAPHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Mismo atleta puede tener AP en distintas disciplinas."""
    cid = uuid4()
    pid = uuid4()

    cmd_sta = RegistrarAPCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.STA, valor_ap=Decimal("330"), unidad=UnidadMedida.Segundos,
    )
    cmd_dnf = RegistrarAPCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=Disciplina.DNF, valor_ap=Decimal("100"), unidad=UnidadMedida.Metros,
    )

    id1 = await handler.handle(cmd_sta)
    id2 = await handler.handle(cmd_dnf)

    assert id1 != id2
