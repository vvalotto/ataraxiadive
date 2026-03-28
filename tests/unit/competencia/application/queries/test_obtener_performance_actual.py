"""Tests unitarios de ObtenerPerformanceActualHandler — US-1.3.1."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.queries.obtener_performance_actual import (
    ObtenerPerformanceActualHandler,
    ObtenerPerformanceActualQuery,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)


# ── Helpers ────────────────────────────────────────────────────────────────────


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ap_stream(
    competencia_id: str,
    participante_id: str,
    valor: str = "50",
    unidad: str = "Metros",
    performance_id: str | None = None,
) -> list[dict[str, Any]]:
    pid = performance_id or str(uuid4())
    return [
        {
            "event_type": "APRegistrado",
            "payload": {
                "performance_id": pid,
                "competencia_id": competencia_id,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "valor_ap": valor,
                "unidad": unidad,
            },
            "version": 1,
            "occurred_at": _ts(),
        }
    ]


def _llamado_stream(
    competencia_id: str,
    participante_id: str,
    posicion_grilla: int = 1,
    performance_id: str | None = None,
) -> list[dict[str, Any]]:
    stream = _ap_stream(competencia_id, participante_id, performance_id=performance_id)
    stream.append(
        {
            "event_type": "AtletaLlamado",
            "payload": {
                "performance_id": stream[0]["payload"]["performance_id"],
                "participante_id": participante_id,
                "disciplina": "DNF",
                "posicion_grilla": posicion_grilla,
                "ot_programado": _ts(),
                "llamado_en": _ts(),
            },
            "version": 2,
            "occurred_at": _ts(),
        }
    )
    return stream


def _ejecutada_stream(
    competencia_id: str, participante_id: str
) -> list[dict[str, Any]]:
    stream = _llamado_stream(competencia_id, participante_id)
    pid = stream[0]["payload"]["performance_id"]
    stream.append(
        {
            "event_type": "ResultadoRegistrado",
            "payload": {
                "performance_id": pid,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "valor_rp": "48",
                "unidad": "Metros",
                "registrado_por": "juez-001",
                "registrado_en": _ts(),
            },
            "version": 3,
            "occurred_at": _ts(),
        }
    )
    stream.append(
        {
            "event_type": "TarjetaAsignada",
            "payload": {
                "performance_id": pid,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "tipo": "Blanca",
                "motivo": None,
                "asignada_por": "juez-001",
                "asignada_en": _ts(),
            },
            "version": 4,
            "occurred_at": _ts(),
        }
    )
    return stream


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retorna_performance_en_estado_llamada() -> None:
    competencia_id = uuid4()
    participante_id = str(uuid4())
    stream = _llamado_stream(str(competencia_id), participante_id, posicion_grilla=3)

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = [stream]
    handler = ObtenerPerformanceActualHandler(store, DisciplinaDescriptorAdapter())

    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=competencia_id))

    assert result is not None
    assert result.estado == "Llamada"
    assert result.andarivel == 3
    assert result.ap_declarado == "50"
    assert result.nombre_atleta == f"Atleta-{participante_id[:8]}"


@pytest.mark.asyncio
async def test_retorna_none_si_solo_hay_performances_en_anunciada_ap() -> None:
    competencia_id = uuid4()
    stream = _ap_stream(str(competencia_id), str(uuid4()))

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = [stream]
    handler = ObtenerPerformanceActualHandler(store, DisciplinaDescriptorAdapter())

    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=competencia_id))

    assert result is None


@pytest.mark.asyncio
async def test_retorna_none_si_no_hay_performances() -> None:
    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = []
    handler = ObtenerPerformanceActualHandler(store, DisciplinaDescriptorAdapter())

    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=uuid4()))

    assert result is None


@pytest.mark.asyncio
async def test_retorna_unidad_esperada_en_dto() -> None:
    """US-2.2.2: el DTO incluye unidad_esperada de la disciplina."""
    competencia_id = uuid4()
    participante_id = str(uuid4())
    stream = _llamado_stream(str(competencia_id), participante_id)

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = [stream]
    handler = ObtenerPerformanceActualHandler(store, DisciplinaDescriptorAdapter())

    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=competencia_id))

    assert result is not None
    assert result.unidad_esperada == "Metros"  # DNF requiere Metros


@pytest.mark.asyncio
async def test_ignora_performances_ejecutadas() -> None:
    competencia_id = uuid4()
    ejecutada = _ejecutada_stream(str(competencia_id), str(uuid4()))
    llamada = _llamado_stream(str(competencia_id), str(uuid4()), posicion_grilla=2)

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = [ejecutada, llamada]
    handler = ObtenerPerformanceActualHandler(store, DisciplinaDescriptorAdapter())

    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=competencia_id))

    assert result is not None
    assert result.estado == "Llamada"
    assert result.andarivel == 2
