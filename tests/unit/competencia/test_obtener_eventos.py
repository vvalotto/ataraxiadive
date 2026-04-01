"""Tests unitarios — ObtenerEventosHandler (US-1.4.2)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from competencia.application.queries.obtener_eventos import (
    EventoDTO,
    ObtenerEventosHandler,
    ObtenerEventosQuery,
)
from competencia.domain.ports.event_store_port import EventStorePort

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
PERFORMANCE_ID = "aaaa0000-0000-0000-0000-000000000001"
PREFIX = f"performance-{COMPETENCIA_ID}-"
STREAM_ID = f"{PREFIX}{PERFORMANCE_ID}"


def _make_store(events: list[dict]) -> EventStorePort:
    store = AsyncMock(spec=EventStorePort)
    store.load_all_events_ordered = AsyncMock(return_value=events)
    return store


@pytest.mark.asyncio
async def test_retorna_lista_vacia_si_no_hay_eventos() -> None:
    store = _make_store([])
    handler = ObtenerEventosHandler(store)
    result = await handler.handle(ObtenerEventosQuery(competencia_id=COMPETENCIA_ID))
    assert result == []
    store.load_all_events_ordered.assert_called_once_with(PREFIX)


@pytest.mark.asyncio
async def test_retorna_eventos_en_orden_de_secuencia() -> None:
    raw = [
        {
            "sequence": 1,
            "stream_id": STREAM_ID,
            "event_type": "APRegistrado",
            "payload": {"valor_ap": 60.0},
            "occurred_at": "2026-03-23T10:00:00",
        },
        {
            "sequence": 2,
            "stream_id": STREAM_ID,
            "event_type": "AtletaLlamado",
            "payload": {"posicion_grilla": 1},
            "occurred_at": "2026-03-23T10:05:00",
        },
    ]
    store = _make_store(raw)
    handler = ObtenerEventosHandler(store)
    result = await handler.handle(ObtenerEventosQuery(competencia_id=COMPETENCIA_ID))

    assert len(result) == 2
    assert isinstance(result[0], EventoDTO)
    assert result[0].sequence == 1
    assert result[0].event_type == "APRegistrado"
    assert result[0].occurred_at == "2026-03-23T10:00:00"
    assert result[1].sequence == 2
    assert result[1].event_type == "AtletaLlamado"


@pytest.mark.asyncio
async def test_extrae_performance_id_del_stream_id() -> None:
    raw = [
        {
            "sequence": 1,
            "stream_id": STREAM_ID,
            "event_type": "APRegistrado",
            "payload": {},
            "occurred_at": "2026-03-23T10:00:00",
        }
    ]
    store = _make_store(raw)
    handler = ObtenerEventosHandler(store)
    result = await handler.handle(ObtenerEventosQuery(competencia_id=COMPETENCIA_ID))

    assert result[0].performance_id == PERFORMANCE_ID


@pytest.mark.asyncio
async def test_payload_se_incluye_en_data() -> None:
    payload = {"valor_ap": 60.0, "disciplina": "STA"}
    raw = [
        {
            "sequence": 1,
            "stream_id": STREAM_ID,
            "event_type": "APRegistrado",
            "payload": payload,
            "occurred_at": "2026-03-23T10:00:00",
        }
    ]
    store = _make_store(raw)
    handler = ObtenerEventosHandler(store)
    result = await handler.handle(ObtenerEventosQuery(competencia_id=COMPETENCIA_ID))

    assert result[0].data == payload


@pytest.mark.asyncio
async def test_multiples_performances_en_orden_global() -> None:
    perf_b = f"{PREFIX}bbbb0000-0000-0000-0000-000000000002"
    raw = [
        {
            "sequence": 1,
            "stream_id": STREAM_ID,
            "event_type": "APRegistrado",
            "payload": {},
            "occurred_at": "2026-03-23T10:00:00",
        },
        {
            "sequence": 2,
            "stream_id": perf_b,
            "event_type": "APRegistrado",
            "payload": {},
            "occurred_at": "2026-03-23T10:01:00",
        },
        {
            "sequence": 3,
            "stream_id": STREAM_ID,
            "event_type": "AtletaLlamado",
            "payload": {},
            "occurred_at": "2026-03-23T10:02:00",
        },
    ]
    store = _make_store(raw)
    handler = ObtenerEventosHandler(store)
    result = await handler.handle(ObtenerEventosQuery(competencia_id=COMPETENCIA_ID))

    assert len(result) == 3
    assert [r.sequence for r in result] == [1, 2, 3]
    assert result[0].performance_id == PERFORMANCE_ID
    assert result[1].performance_id == "bbbb0000-0000-0000-0000-000000000002"
