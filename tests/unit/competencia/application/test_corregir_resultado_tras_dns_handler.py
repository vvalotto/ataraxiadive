"""Tests unitarios del CorregirResultadoTrasDNSHandler — US-ADJ-7.1."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.corregir_resultado_tras_dns import (
    CorregirResultadoTrasDNSCommand,
    CorregirResultadoTrasDNSHandler,
    PerformanceNoEncontrada,
)
from competencia.domain.exceptions import EstadoInvalidoParaCorregirResultadoTrasDNS
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida

OT = datetime(2026, 3, 23, 10, 30, 0)


def _ap_event(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "APRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "valor_ap": "50",
            "unidad": UnidadMedida.Metros.value,
        },
    }


def _llamado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "AtletaLlamado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "posicion_grilla": 1,
            "ot_programado": OT.isoformat(),
            "llamado_en": OT.isoformat(),
            "andarivel": 1,
        },
    }


def _dns_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "DNSRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "ot_programado": OT.isoformat(),
            "registrado_por": "juez-001",
            "registrado_en": OT.isoformat(),
        },
    }


def _make_command(competencia_id: Any, participante_id: Any) -> CorregirResultadoTrasDNSCommand:
    return CorregirResultadoTrasDNSCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DNF,
        valor_rp=Decimal("50.25"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-002",
        motivo_correccion="DNS cargado por error",
    )


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
def store_en_dns(performance_id: Any, competencia_id: Any, participante_id: Any) -> AsyncMock:
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
        _dns_event(performance_id, participante_id),
    ]
    store.append.return_value = None
    return store


@pytest.mark.asyncio
async def test_corregir_resultado_tras_dns_persiste_evento(
    store_en_dns: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = CorregirResultadoTrasDNSHandler(store_en_dns)

    await handler.handle(_make_command(competencia_id, participante_id))

    store_en_dns.append.assert_called_once()
    assert store_en_dns.append.call_args.kwargs["event_type"] == "ResultadoCorregidoTrasDNS"


@pytest.mark.asyncio
async def test_corregir_resultado_tras_dns_payload_correcto(
    store_en_dns: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = CorregirResultadoTrasDNSHandler(store_en_dns)

    await handler.handle(_make_command(competencia_id, participante_id))

    payload = store_en_dns.append.call_args.kwargs["payload"]
    assert payload["valor_rp"] == "50.25"
    assert payload["unidad"] == "Metros"
    assert payload["registrado_por"] == "juez-002"
    assert payload["motivo_correccion"] == "DNS cargado por error"


@pytest.mark.asyncio
async def test_corregir_resultado_tras_dns_stream_vacio_lanza_excepcion(
    competencia_id: Any,
    participante_id: Any,
) -> None:
    store = AsyncMock()
    store.load.return_value = []
    handler = CorregirResultadoTrasDNSHandler(store)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(_make_command(competencia_id, participante_id))


@pytest.mark.asyncio
async def test_corregir_resultado_tras_dns_desde_llamada_lanza_excepcion(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
    ]
    handler = CorregirResultadoTrasDNSHandler(store)

    with pytest.raises(EstadoInvalidoParaCorregirResultadoTrasDNS):
        await handler.handle(_make_command(competencia_id, participante_id))

    store.append.assert_not_called()
