"""Tests unitarios de Política P-08 — AsignarTarjetaHandler y RegistrarDNSHandler (US-2.4.1)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.registrar_dns import (
    RegistrarDNSCommand,
    RegistrarDNSHandler,
)
from competencia.domain.ports.performances_estado_port import PerformancesEstadoData
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta

OT = datetime(2026, 3, 22, 10, 30, 0)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ap_payload(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "APRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "valor_ap": "300",
            "unidad": "Segundos",
            "occurred_at": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
        },
    }


def _resultado_payload(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "ResultadoRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "valor_rp": "295",
            "unidad": "Segundos",
            "registrado_por": "juez",
            "occurred_at": datetime(2026, 3, 22, 10, 35, 0).isoformat(),
        },
    }


def _llamada_payload(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "AtletaLlamado",
        "payload": {
            "performance_id": str(performance_id),
            "competencia_id": str(competencia_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.STA.value,
            "ot_programado": OT.isoformat(),
            "posicion_grilla": 1,
            "andarivel": 1,
            "occurred_at": OT.isoformat(),
        },
    }


def _make_store_con_resultado(cid: Any, pid: Any) -> AsyncMock:
    """Event Store con Performance en estado ResultadoRegistrado."""
    perf_id = uuid4()
    store = AsyncMock()
    store.load = AsyncMock(side_effect=lambda stream_id: (
        [
            _ap_payload(perf_id, cid, pid),
            _llamada_payload(perf_id, cid, pid),
            _resultado_payload(perf_id, cid, pid),
        ] if "performance" in stream_id else []
    ))
    store.append = AsyncMock(return_value=None)
    return store


def _make_store_con_llamada(cid: Any, pid: Any) -> AsyncMock:
    """Event Store con Performance en estado Llamada."""
    perf_id = uuid4()
    store = AsyncMock()
    store.load = AsyncMock(side_effect=lambda stream_id: (
        [
            _ap_payload(perf_id, cid, pid),
            _llamada_payload(perf_id, cid, pid),
        ] if "performance" in stream_id else []
    ))
    store.append = AsyncMock(return_value=None)
    return store


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def competencia_id() -> Any:
    return uuid4()


@pytest.fixture
def participante_id() -> Any:
    return uuid4()


@pytest.fixture
def mock_estado_no_finalizado() -> AsyncMock:
    """PerformancesEstadoPort: quedan performances pendientes."""
    port = AsyncMock()
    port.get_estado.return_value = PerformancesEstadoData(total=3, ejecutadas=1, dns_count=0)
    return port


@pytest.fixture
def mock_estado_finalizado() -> AsyncMock:
    """PerformancesEstadoPort: todas las performances terminaron."""
    port = AsyncMock()
    port.get_estado.return_value = PerformancesEstadoData(total=3, ejecutadas=2, dns_count=1)
    return port


# ── Tests AsignarTarjetaHandler + P-08 ────────────────────────────────────────


@pytest.mark.asyncio
async def test_asignar_sin_port_no_dispara_finalizacion(
    competencia_id: Any, participante_id: Any
) -> None:
    """Sin PerformancesEstadoPort la verificación P-08 se omite (backward compat)."""
    store = _make_store_con_resultado(competencia_id, participante_id)
    handler = AsignarTarjetaHandler(store)

    await handler.handle(AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        tipo=TipoTarjeta.Blanca,
        asignada_por="juez",
    ))

    # Solo se persiste TarjetaAsignada, no se carga stream de Competencia
    store.load.assert_called_once()


@pytest.mark.asyncio
async def test_asignar_con_port_no_finalizado_no_emite_competencia_finalizada(
    competencia_id: Any, participante_id: Any, mock_estado_no_finalizado: AsyncMock
) -> None:
    """P-08: no se emite CompetenciaFinalizada si quedan performances pendientes."""
    store = _make_store_con_resultado(competencia_id, participante_id)
    handler = AsignarTarjetaHandler(store, mock_estado_no_finalizado)

    await handler.handle(AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        tipo=TipoTarjeta.Blanca,
        asignada_por="juez",
    ))

    # El stream de Competencia no debe cargarse si no finaliza
    calls = [str(c) for c in store.load.call_args_list]
    assert all("competencia-" not in c for c in calls)


@pytest.mark.asyncio
async def test_asignar_con_port_finalizado_carga_competencia(
    competencia_id: Any, participante_id: Any, mock_estado_finalizado: AsyncMock
) -> None:
    """P-08: cuando todas finalizan, se carga el stream de Competencia."""
    store = _make_store_con_resultado(competencia_id, participante_id)
    handler = AsignarTarjetaHandler(store, mock_estado_finalizado)

    await handler.handle(AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        tipo=TipoTarjeta.Blanca,
        asignada_por="juez",
    ))

    # Se debe haber llamado load para el stream de Competencia también
    load_calls = [str(c) for c in store.load.call_args_list]
    assert any(f"competencia-{competencia_id}" in c for c in load_calls)


# ── Tests RegistrarDNSHandler + P-08 ──────────────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_dns_sin_port_no_dispara_finalizacion(
    competencia_id: Any, participante_id: Any
) -> None:
    """Sin PerformancesEstadoPort la verificación P-08 se omite (backward compat)."""
    store = _make_store_con_llamada(competencia_id, participante_id)
    handler = RegistrarDNSHandler(store)

    await handler.handle(RegistrarDNSCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        registrado_por="juez",
    ))

    store.load.assert_called_once()


@pytest.mark.asyncio
async def test_registrar_dns_con_port_finalizado_carga_competencia(
    competencia_id: Any, participante_id: Any, mock_estado_finalizado: AsyncMock
) -> None:
    """P-08 via RegistrarDNS: cuando todas finalizan, carga stream de Competencia."""
    store = _make_store_con_llamada(competencia_id, participante_id)
    handler = RegistrarDNSHandler(store, mock_estado_finalizado)

    await handler.handle(RegistrarDNSCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        registrado_por="juez",
    ))

    load_calls = [str(c) for c in store.load.call_args_list]
    assert any(f"competencia-{competencia_id}" in c for c in load_calls)


# ── Tests PerformancesEstadoData ──────────────────────────────────────────────


def test_performances_estado_data_todas_finalizadas_true() -> None:
    """todas_finalizadas es True cuando ejecutadas + dns_count == total."""
    data = PerformancesEstadoData(total=3, ejecutadas=2, dns_count=1)
    assert data.todas_finalizadas is True


def test_performances_estado_data_todas_finalizadas_false() -> None:
    """todas_finalizadas es False cuando quedan performances pendientes."""
    data = PerformancesEstadoData(total=3, ejecutadas=1, dns_count=0)
    assert data.todas_finalizadas is False


def test_performances_estado_data_total_cero_no_finalizado() -> None:
    """Con total=0 (sin performances) todas_finalizadas es False."""
    data = PerformancesEstadoData(total=0, ejecutadas=0, dns_count=0)
    assert data.todas_finalizadas is False
