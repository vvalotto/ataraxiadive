"""Tests unitarios de ObtenerProgresoHandler — US-1.3.1."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.queries.obtener_progreso import (
    ObtenerProgresoHandler,
    ObtenerProgresoQuery,
)

# ── Helpers ────────────────────────────────────────────────────────────────────


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ap_event(competencia_id: str, participante_id: str) -> dict[str, Any]:
    return {
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
        "occurred_at": _ts(),
    }


def _llamado_event(performance_id: str, participante_id: str) -> dict[str, Any]:
    return {
        "event_type": "AtletaLlamado",
        "payload": {
            "performance_id": performance_id,
            "participante_id": participante_id,
            "disciplina": "DNF",
            "posicion_grilla": 1,
            "ot_programado": _ts(),
            "llamado_en": _ts(),
        },
        "version": 2,
        "occurred_at": _ts(),
    }


def _ejecutada_stream(competencia_id: str) -> list[dict[str, Any]]:
    pid = str(uuid4())
    part_id = str(uuid4())
    ap = _ap_event(competencia_id, part_id)
    ap["payload"]["performance_id"] = pid
    return [
        ap,
        _llamado_event(pid, part_id),
        {
            "event_type": "ResultadoRegistrado",
            "payload": {
                "performance_id": pid,
                "participante_id": part_id,
                "disciplina": "DNF",
                "valor_rp": "48",
                "unidad": "Metros",
                "registrado_por": "juez-001",
                "registrado_en": _ts(),
            },
            "version": 3,
            "occurred_at": _ts(),
        },
        {
            "event_type": "TarjetaAsignada",
            "payload": {
                "performance_id": pid,
                "participante_id": part_id,
                "disciplina": "DNF",
                "tipo": "Blanca",
                "motivo": None,
                "asignada_por": "juez-001",
                "asignada_en": _ts(),
            },
            "version": 4,
            "occurred_at": _ts(),
        },
    ]


def _dns_stream(competencia_id: str) -> list[dict[str, Any]]:
    pid = str(uuid4())
    part_id = str(uuid4())
    ap = _ap_event(competencia_id, part_id)
    ap["payload"]["performance_id"] = pid
    return [
        ap,
        _llamado_event(pid, part_id),
        {
            "event_type": "DNSRegistrado",
            "payload": {
                "performance_id": pid,
                "participante_id": part_id,
                "disciplina": "DNF",
                "ot_programado": _ts(),
                "registrado_por": "juez-001",
                "registrado_en": _ts(),
            },
            "version": 3,
            "occurred_at": _ts(),
        },
    ]


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_conteo_correcto_con_mix_de_estados() -> None:
    cid = str(uuid4())
    competencia_id = uuid4()
    streams = [
        _ejecutada_stream(cid),
        _ejecutada_stream(cid),
        _dns_stream(cid),
        [_ap_event(cid, str(uuid4()))],  # AnunciadaAP
    ]

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    handler = ObtenerProgresoHandler(store)

    result = await handler.handle(ObtenerProgresoQuery(competencia_id=competencia_id))

    assert result.total == 4
    assert result.ejecutadas == 2
    assert result.dns_count == 1
    assert result.completadas == 3


@pytest.mark.asyncio
async def test_retorna_ceros_sin_performances() -> None:
    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = []
    handler = ObtenerProgresoHandler(store)

    result = await handler.handle(ObtenerProgresoQuery(competencia_id=uuid4()))

    assert result.total == 0
    assert result.ejecutadas == 0
    assert result.dns_count == 0
    assert result.completadas == 0
