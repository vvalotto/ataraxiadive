"""Tests de integración — ConfigurarIntervaloOTHandler con SQLiteEventStore real."""

from __future__ import annotations

from uuid import UUID, uuid4

import aiosqlite
import pytest

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
    _build_stream_id,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import GrillaYaConfirmada
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.intervalo_disciplina import IntervaloInvalido
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

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
DISCIPLINA = Disciplina.STA
CONFIGURADO_POR = "organizador-01"


@pytest.fixture
async def event_store(tmp_path: Any) -> SQLiteEventStore:
    db_path = str(tmp_path / "test_competencia.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


def _command(intervalo_minutos: int = 9) -> ConfigurarIntervaloOTCommand:
    return ConfigurarIntervaloOTCommand(
        competencia_id=COMPETENCIA_ID,
        disciplina=DISCIPLINA,
        intervalo_minutos=intervalo_minutos,
        configurado_por=CONFIGURADO_POR,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


class TestConfigurarIntervaloOTIntegracion:
    @pytest.mark.asyncio
    async def test_persiste_evento_en_stream(self, event_store: SQLiteEventStore) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(9))

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "IntervaloOTConfigurado"

    @pytest.mark.asyncio
    async def test_payload_correcto_en_store(self, event_store: SQLiteEventStore) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(9))

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        payload = events[0]["payload"]
        assert payload["intervalo_minutos"] == 9
        assert payload["disciplina"] == DISCIPLINA.value
        assert payload["configurado_por"] == CONFIGURADO_POR

    @pytest.mark.asyncio
    async def test_reconfiguracion_agrega_segundo_evento(
        self, event_store: SQLiteEventStore
    ) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(7))
        await handler.handle(_command(10))

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        assert len(events) == 2
        assert events[1]["payload"]["intervalo_minutos"] == 10

    @pytest.mark.asyncio
    async def test_reconstituyendo_desde_store_refleja_ultimo_intervalo(
        self, event_store: SQLiteEventStore
    ) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(7))
        await handler.handle(_command(10))

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.intervalo is not None
        assert c.intervalo.minutos == 10

    @pytest.mark.asyncio
    async def test_stream_id_aislado_de_performance(self, event_store: SQLiteEventStore) -> None:
        """El stream competencia-* no interfiere con el stream performance-*."""
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(9))

        performance_events = await event_store.load(f"performance-{COMPETENCIA_ID}")
        assert len(performance_events) == 0

    @pytest.mark.asyncio
    async def test_intervalo_invalido_no_persiste(self, event_store: SQLiteEventStore) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        with pytest.raises(IntervaloInvalido):
            await handler.handle(_command(0))

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        assert len(events) == 0


# ── Type alias para fixture ────────────────────────────────────────────────────
from typing import Any  # noqa: E402
