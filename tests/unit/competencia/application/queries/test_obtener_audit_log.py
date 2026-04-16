"""Tests unitarios - ObtenerAuditLogHandler."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from competencia.application.queries.obtener_audit_log import (
    AuditLogDTO,
    AuditLogEventoDTO,
    ObtenerAuditLogHandler,
    ObtenerAuditLogQuery,
    PerformanceNoEncontrada,
)
from competencia.domain.ports.atleta_nombre_port import AtletaNombrePort
from competencia.domain.ports.event_store_port import EventStorePort

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
ATLETA_ID = UUID("aaaa0000-0000-0000-0000-000000000001")
PREFIX = f"performance-{COMPETENCIA_ID}-{ATLETA_ID}-"
STREAM_ID = f"{PREFIX}DNF"


def _make_store(events: list[dict]) -> EventStorePort:
    store = AsyncMock(spec=EventStorePort)
    store.load_all_events_ordered = AsyncMock(return_value=events)
    return store


def _make_nombres(nombre: str = "Martin Garcia") -> AtletaNombrePort:
    nombres = AsyncMock(spec=AtletaNombrePort)
    nombres.get_nombre = AsyncMock(return_value=nombre)
    return nombres


@pytest.mark.asyncio
async def test_retorna_audit_log_completo() -> None:
    store = _make_store(
        [
            {
                "sequence": 1,
                "stream_id": STREAM_ID,
                "event_type": "PerformanceRegistrada",
                "payload": {"ap": 60.0},
                "occurred_at": "2026-04-16T12:00:00Z",
            },
            {
                "sequence": 2,
                "stream_id": STREAM_ID,
                "event_type": "ResultadoRegistrado",
                "payload": {"rp": 58.0},
                "occurred_at": "2026-04-16T12:03:00Z",
            },
        ]
    )
    nombres = _make_nombres()
    handler = ObtenerAuditLogHandler(store, nombres)

    result = await handler.handle(
        ObtenerAuditLogQuery(competencia_id=COMPETENCIA_ID, atleta_id=ATLETA_ID)
    )

    assert isinstance(result, AuditLogDTO)
    assert result.competencia_id == str(COMPETENCIA_ID)
    assert result.atleta_id == str(ATLETA_ID)
    assert result.atleta_nombre == "Martin Garcia"
    assert result.disciplina == "DNF"
    assert len(result.eventos) == 2
    assert isinstance(result.eventos[0], AuditLogEventoDTO)
    store.load_all_events_ordered.assert_called_once_with(PREFIX)
    nombres.get_nombre.assert_called_once_with(ATLETA_ID)


@pytest.mark.asyncio
async def test_preserva_sequence_y_payload() -> None:
    store = _make_store(
        [
            {
                "sequence": 3,
                "stream_id": STREAM_ID,
                "event_type": "ResultadoCorregido",
                "payload": {"rp_anterior": 55.0, "rp_nuevo": 58.0},
                "occurred_at": "2026-04-16T12:05:00Z",
            }
        ]
    )
    handler = ObtenerAuditLogHandler(store, _make_nombres())

    result = await handler.handle(
        ObtenerAuditLogQuery(competencia_id=COMPETENCIA_ID, atleta_id=ATLETA_ID)
    )

    assert result.eventos[0].sequence == 3
    assert result.eventos[0].tipo == "ResultadoCorregido"
    assert result.eventos[0].timestamp == "2026-04-16T12:05:00Z"
    assert result.eventos[0].datos == {"rp_anterior": 55.0, "rp_nuevo": 58.0}


@pytest.mark.asyncio
async def test_lanza_performance_no_encontrada_si_no_hay_eventos() -> None:
    handler = ObtenerAuditLogHandler(_make_store([]), _make_nombres())

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(
            ObtenerAuditLogQuery(competencia_id=COMPETENCIA_ID, atleta_id=ATLETA_ID)
        )
