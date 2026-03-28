"""Tests unitarios del RegistrarDNSHandler — US-1.2.5."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.registrar_dns import (
    RegistrarDNSCommand,
    RegistrarDNSHandler,
    PerformanceNoEncontrada,
)
from competencia.domain.exceptions import EstadoInvalidoParaRegistrarDNS
from competencia.domain.value_objects.disciplina import Disciplina

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
            "valor_ap": "330",
            "unidad": "Segundos",
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
def mock_event_store_en_llamada(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> AsyncMock:
    """EventStore mock con stream en estado Llamada."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
    ]
    store.append.return_value = None
    return store


def _make_command(competencia_id: Any, participante_id: Any) -> RegistrarDNSCommand:
    return RegistrarDNSCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        registrado_por="juez-001",
    )


# ── Camino feliz ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_dns_persiste_evento(
    mock_event_store_en_llamada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """RegistrarDNSHandler persiste DNSRegistrado en el Event Store."""
    handler = RegistrarDNSHandler(mock_event_store_en_llamada)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    mock_event_store_en_llamada.append.assert_called_once()
    call_kwargs = mock_event_store_en_llamada.append.call_args.kwargs
    assert call_kwargs["event_type"] == "DNSRegistrado"


@pytest.mark.asyncio
async def test_registrar_dns_payload_correcto(
    mock_event_store_en_llamada: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El payload de DNSRegistrado contiene registradoPor y ot_programado correctos."""
    handler = RegistrarDNSHandler(mock_event_store_en_llamada)
    command = _make_command(competencia_id, participante_id)

    await handler.handle(command)

    payload = mock_event_store_en_llamada.append.call_args.kwargs["payload"]
    assert payload["registrado_por"] == "juez-001"
    assert payload["ot_programado"] == OT.isoformat()


# ── Performance no encontrada ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_dns_stream_vacio_lanza_excepcion(
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """PerformanceNoEncontrada si no existe stream para este atleta."""
    store = AsyncMock()
    store.load.return_value = []

    handler = RegistrarDNSHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(command)


# ── INV-P-08: Performance debe estar en Llamada ───────────────────────────────


@pytest.mark.asyncio
async def test_registrar_dns_desde_anunciada_lanza_excepcion(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-08: EstadoInvalidoParaRegistrarDNS si Performance en AnunciadaAP."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
    ]

    handler = RegistrarDNSHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaRegistrarDNS):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_registrar_dns_estado_invalido_no_persiste(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Si el estado es inválido no se persiste ningún evento."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
    ]

    handler = RegistrarDNSHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaRegistrarDNS):
        await handler.handle(command)

    store.append.assert_not_called()
