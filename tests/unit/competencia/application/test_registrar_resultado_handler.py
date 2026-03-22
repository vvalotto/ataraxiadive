"""Tests unitarios del RegistrarResultadoHandler — US-1.2.3."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.registrar_resultado import (
    PerformanceNoEncontrada,
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import EstadoInvalidoParaRegistrarResultado
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida

OT = datetime(2026, 3, 22, 10, 30, 0)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ap_registrado_payload(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> dict[str, Any]:
    """Payload mínimo de APRegistrado para reconstituir una Performance."""
    return {
        "event_type": "APRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "valor_ap": "50",
            "unidad": "Metros",
            "occurred_at": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
        },
    }


def _atleta_llamado_payload(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    """Payload de AtletaLlamado para reconstituir Performance en estado Llamada."""
    return {
        "event_type": "AtletaLlamado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "posicion_grilla": 1,
            "ot_programado": OT.isoformat(),
            "llamado_en": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
        },
    }


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def competencia_id() -> Any:
    return uuid4()


@pytest.fixture
def participante_id() -> Any:
    return uuid4()


@pytest.fixture
def performance_id() -> Any:
    return uuid4()


@pytest.fixture
def mock_event_store_llamada(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> AsyncMock:
    """EventStore mock con stream en estado Llamada (AP + AtletaLlamado)."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_registrado_payload(performance_id, competencia_id, participante_id),
        _atleta_llamado_payload(performance_id, participante_id),
    ]
    store.append.return_value = None
    return store


def _make_command(competencia_id: Any, participante_id: Any) -> RegistrarResultadoCommand:
    return RegistrarResultadoCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DNF,
        valor_rp=Decimal("50.5"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-001",
    )


# ── Camino feliz ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_resultado_persiste_evento(
    mock_event_store_llamada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """RegistrarResultadoHandler persiste ResultadoRegistrado en el Event Store."""
    handler = RegistrarResultadoHandler(mock_event_store_llamada)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    mock_event_store_llamada.append.assert_called_once()
    call_kwargs = mock_event_store_llamada.append.call_args.kwargs
    assert call_kwargs["event_type"] == "ResultadoRegistrado"


@pytest.mark.asyncio
async def test_registrar_resultado_payload_correcto(
    mock_event_store_llamada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El payload de ResultadoRegistrado contiene valorRP, unidad y registradoPor."""
    handler = RegistrarResultadoHandler(mock_event_store_llamada)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    payload = mock_event_store_llamada.append.call_args.kwargs["payload"]
    assert payload["valor_rp"] == "50.5"
    assert payload["unidad"] == UnidadMedida.Metros.value
    assert payload["registrado_por"] == "juez-001"


# ── Performance no encontrada ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_resultado_stream_vacio_lanza_excepcion(
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """PerformanceNoEncontrada si no existe stream para este atleta."""
    store = AsyncMock()
    store.load.return_value = []

    handler = RegistrarResultadoHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(command)


# ── INV-P-06: Performance en estado Llamada ───────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_resultado_desde_anunciada_lanza_excepcion(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-06: EstadoInvalidoParaRegistrarResultado si Performance en AnunciadaAP."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_registrado_payload(performance_id, competencia_id, participante_id)
    ]

    handler = RegistrarResultadoHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaRegistrarResultado):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_registrar_resultado_estado_invalido_no_persiste(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Si el estado es inválido no se persiste ningún evento."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_registrado_payload(performance_id, competencia_id, participante_id)
    ]

    handler = RegistrarResultadoHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaRegistrarResultado):
        await handler.handle(command)

    store.append.assert_not_called()
