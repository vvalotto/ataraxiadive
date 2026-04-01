"""Tests unitarios del LlamarAtletaHandler — US-1.2.2."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.llamar_atleta import (
    CompetenciaNoEnEjecucion,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
    PerformanceNoEncontrada,
)
from competencia.domain.exceptions import EstadoInvalidoParaLlamar
from competencia.domain.value_objects.disciplina import Disciplina

OT = datetime(2026, 3, 22, 10, 30, 0)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ap_registrado_payload(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> dict[str, Any]:
    """Payload mínimo de APRegistrado para reconstituir una Performance."""
    from datetime import timezone

    return {
        "event_type": "APRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "valor_ap": "330",
            "unidad": "Segundos",
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
            "disciplina": Disciplina.STA.value,
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
def mock_event_store_con_ap(competencia_id: Any, participante_id: Any) -> AsyncMock:
    """EventStore mock con stream que contiene un APRegistrado."""
    pid = uuid4()
    store = AsyncMock()
    store.load.return_value = [_ap_registrado_payload(pid, competencia_id, participante_id)]
    store.append.return_value = None
    return store


@pytest.fixture
def mock_competencia_en_ejecucion() -> AsyncMock:
    """CompetenciaEstadoPort mock: competencia en EnEjecucion."""
    estado = AsyncMock()
    estado.is_en_ejecucion.return_value = True
    return estado


@pytest.fixture
def mock_competencia_no_en_ejecucion() -> AsyncMock:
    """CompetenciaEstadoPort mock: competencia NO en EnEjecucion."""
    estado = AsyncMock()
    estado.is_en_ejecucion.return_value = False
    return estado


def _make_command(competencia_id: Any, participante_id: Any) -> LlamarAtletaCommand:
    return LlamarAtletaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        ot_programado=OT,
        posicion_grilla=3,
    )


# ── Camino feliz ──────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_llamar_atleta_persiste_evento(
    mock_event_store_con_ap: AsyncMock,
    mock_competencia_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """LlamarAtletaHandler persiste AtletaLlamado en el Event Store."""
    handler = LlamarAtletaHandler(mock_event_store_con_ap, mock_competencia_en_ejecucion)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    mock_event_store_con_ap.append.assert_called_once()
    call_kwargs = mock_event_store_con_ap.append.call_args.kwargs
    assert call_kwargs["event_type"] == "AtletaLlamado"


@pytest.mark.asyncio
async def test_llamar_atleta_payload_correcto(
    mock_event_store_con_ap: AsyncMock,
    mock_competencia_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El payload de AtletaLlamado contiene posicion_grilla y ot_programado."""
    handler = LlamarAtletaHandler(mock_event_store_con_ap, mock_competencia_en_ejecucion)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    payload = mock_event_store_con_ap.append.call_args.kwargs["payload"]
    assert payload["posicion_grilla"] == 3
    assert payload["ot_programado"] == OT.isoformat()


# ── INV-P-05: Competencia en EnEjecucion ─────────────────────────────────────


@pytest.mark.asyncio
async def test_llamar_atleta_competencia_no_en_ejecucion_lanza_excepcion(
    mock_event_store_con_ap: AsyncMock,
    mock_competencia_no_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-05: CompetenciaNoEnEjecucion si la competencia no está iniciada."""
    handler = LlamarAtletaHandler(mock_event_store_con_ap, mock_competencia_no_en_ejecucion)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(CompetenciaNoEnEjecucion):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_llamar_atleta_competencia_no_en_ejecucion_no_persiste(
    mock_event_store_con_ap: AsyncMock,
    mock_competencia_no_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Si la competencia no está en ejecución no se persiste ningún evento."""
    handler = LlamarAtletaHandler(mock_event_store_con_ap, mock_competencia_no_en_ejecucion)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(CompetenciaNoEnEjecucion):
        await handler.handle(command)

    mock_event_store_con_ap.append.assert_not_called()


# ── Performance no encontrada ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_llamar_atleta_stream_vacio_lanza_excepcion(
    mock_competencia_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """PerformanceNoEncontrada si no existe AP previo en el stream."""
    store = AsyncMock()
    store.load.return_value = []

    handler = LlamarAtletaHandler(store, mock_competencia_en_ejecucion)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(command)


# ── Performance en estado incorrecto ─────────────────────────────────────────


@pytest.mark.asyncio
async def test_llamar_atleta_ya_llamada_lanza_excepcion(
    mock_competencia_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """EstadoInvalidoParaLlamar si la Performance ya está en Llamada."""
    pid = uuid4()
    store = AsyncMock()
    store.load.return_value = [
        _ap_registrado_payload(pid, competencia_id, participante_id),
        _atleta_llamado_payload(pid, participante_id),
    ]

    handler = LlamarAtletaHandler(store, mock_competencia_en_ejecucion)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaLlamar):
        await handler.handle(command)
