"""Tests unitarios del CorregirResultadoHandler — US-1.2.6."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.corregir_resultado import (
    CorregirResultadoCommand,
    CorregirResultadoHandler,
    PerformanceNoEncontrada,
)
from competencia.domain.exceptions import (
    EstadoInvalidoParaCorregirResultado,
    MotivoObligatorio,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida

OT = datetime(2026, 3, 23, 10, 30, 0)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ap_event(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "APRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "valor_ap": "90",
            "unidad": "Metros",
            "occurred_at": datetime(2026, 3, 23, 9, 0, 0).isoformat(),
        },
    }


def _llamado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "AtletaLlamado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "posicion_grilla": 1,
            "ot_programado": OT.isoformat(),
            "llamado_en": datetime(2026, 3, 23, 10, 0, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 23, 10, 0, 0).isoformat(),
        },
    }


def _resultado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "ResultadoRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "valor_rp": "89.5",
            "unidad": "Metros",
            "registrado_por": "juez-001",
            "registrado_en": datetime(2026, 3, 23, 10, 35, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 23, 10, 35, 0).isoformat(),
        },
    }


def _tarjeta_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "TarjetaAsignada",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "tipo": "Blanca",
            "motivo": None,
            "asignada_por": "juez-001",
            "asignada_en": datetime(2026, 3, 23, 10, 36, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 23, 10, 36, 0).isoformat(),
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
def mock_event_store_en_ejecutada(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> AsyncMock:
    """EventStore mock con stream en estado Ejecutada."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
        _resultado_event(performance_id, participante_id),
        _tarjeta_event(performance_id, participante_id),
    ]
    store.append.return_value = None
    return store


def _make_command(
    competencia_id: Any,
    participante_id: Any,
    motivo: str = "Error de lectura",
) -> CorregirResultadoCommand:
    return CorregirResultadoCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        valor_rp=Decimal("90.0"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-001",
        motivo=motivo,
    )


# ── Camino feliz ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_corregir_resultado_persiste_evento(
    mock_event_store_en_ejecutada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """CorregirResultadoHandler persiste ResultadoCorregido en el Event Store."""
    handler = CorregirResultadoHandler(mock_event_store_en_ejecutada)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    mock_event_store_en_ejecutada.append.assert_called_once()
    call_kwargs = mock_event_store_en_ejecutada.append.call_args.kwargs
    assert call_kwargs["event_type"] == "ResultadoCorregido"


@pytest.mark.asyncio
async def test_corregir_resultado_payload_correcto(
    mock_event_store_en_ejecutada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El payload de ResultadoCorregido contiene los campos obligatorios."""
    handler = CorregirResultadoHandler(mock_event_store_en_ejecutada)
    command = _make_command(competencia_id, participante_id, motivo="Error de planilla")

    await handler.handle(command)

    payload = mock_event_store_en_ejecutada.append.call_args.kwargs["payload"]
    assert payload["valor_rp_anterior"] == "89.5"
    assert payload["valor_rp_nuevo"] == "90.0"
    assert payload["motivo"] == "Error de planilla"
    assert payload["registrado_por"] == "juez-001"


# ── Performance no encontrada ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_corregir_resultado_stream_vacio_lanza_excepcion(
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """PerformanceNoEncontrada si no existe stream para este atleta."""
    store = AsyncMock()
    store.load.return_value = []

    handler = CorregirResultadoHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(command)


# ── INV-P-12/13 ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_corregir_resultado_desde_anunciada_lanza_excepcion(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-12: EstadoInvalidoParaCorregirResultado si Performance en AnunciadaAP."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
    ]

    handler = CorregirResultadoHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_corregir_resultado_estado_invalido_no_persiste(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Si el estado es inválido no se persiste ningún evento."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
    ]

    handler = CorregirResultadoHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        await handler.handle(command)

    store.append.assert_not_called()


@pytest.mark.asyncio
async def test_corregir_resultado_sin_motivo_lanza_excepcion(
    mock_event_store_en_ejecutada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-12: MotivoObligatorio si motivo está vacío."""
    handler = CorregirResultadoHandler(mock_event_store_en_ejecutada)
    command = _make_command(competencia_id, participante_id, motivo="")

    with pytest.raises(MotivoObligatorio):
        await handler.handle(command)

    mock_event_store_en_ejecutada.append.assert_not_called()
