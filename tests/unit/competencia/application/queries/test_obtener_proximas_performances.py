"""Tests unitarios de ObtenerProximasPerformancesHandler — US-1.3.1."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.queries.obtener_proximas_performances import (
    ObtenerProximasPerformancesHandler,
    ObtenerProximasPerformancesQuery,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _ap_stream(
    competencia_id: str, participante_id: str, occurred_at: str | None = None
) -> list[dict[str, Any]]:
    ts = occurred_at or datetime.now(timezone.utc).isoformat()
    return [
        {
            "event_type": "APRegistrado",
            "payload": {
                "performance_id": str(uuid4()),
                "competencia_id": competencia_id,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "valor_ap": "50",
                "unidad": "Metros",
            },
            "version": 1,
            "occurred_at": ts,
        }
    ]


def _llamado_stream(competencia_id: str, participante_id: str) -> list[dict[str, Any]]:
    stream = _ap_stream(competencia_id, participante_id)
    pid = stream[0]["payload"]["performance_id"]
    stream.append(
        {
            "event_type": "AtletaLlamado",
            "payload": {
                "performance_id": pid,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "posicion_grilla": 1,
                "ot_programado": datetime.now(timezone.utc).isoformat(),
                "llamado_en": datetime.now(timezone.utc).isoformat(),
            },
            "version": 2,
            "occurred_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return stream


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retorna_hasta_3_proximas_en_anunciada_ap() -> None:
    competencia_id = uuid4()
    cid = str(competencia_id)
    streams = [_ap_stream(cid, str(uuid4())) for _ in range(5)]
    streams[0] = _llamado_stream(cid, str(uuid4()))
    streams[1] = _llamado_stream(cid, str(uuid4()))

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(ObtenerProximasPerformancesQuery(competencia_id=competencia_id))

    assert len(result) == 3
    for i, dto in enumerate(result, start=1):
        assert dto.posicion == i


@pytest.mark.asyncio
async def test_retorna_menos_de_3_si_hay_pocas_disponibles() -> None:
    competencia_id = uuid4()
    cid = str(competencia_id)
    streams = [_ap_stream(cid, str(uuid4())) for _ in range(2)]

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(ObtenerProximasPerformancesQuery(competencia_id=competencia_id))

    assert len(result) == 2


@pytest.mark.asyncio
async def test_retorna_lista_vacia_si_todas_llamadas() -> None:
    competencia_id = uuid4()
    cid = str(competencia_id)
    streams = [_llamado_stream(cid, str(uuid4())) for _ in range(3)]

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(ObtenerProximasPerformancesQuery(competencia_id=competencia_id))

    assert result == []


@pytest.mark.asyncio
async def test_retorna_lista_vacia_sin_performances() -> None:
    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = []
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(
        ObtenerProximasPerformancesQuery(competencia_id=uuid4())
    )

    assert result == []
