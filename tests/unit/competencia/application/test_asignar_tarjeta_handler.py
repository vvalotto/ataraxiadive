"""Tests unitarios del AsignarTarjetaHandler — US-1.2.4."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
    PerformanceNoEncontrada,
)
from competencia.domain.exceptions import (
    DisciplinaNoAdmitePenalizaciones,
    DistanciaBlackoutNoAplica,
    EstadoInvalidoParaAsignarTarjeta,
    MotivoDQObligatorio,
    MotivoObligatorio,
    PenalizacionesObligatorias,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica
from competencia.domain.value_objects.tipo_penalizacion import TipoPenalizacion
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta

OT = datetime(2026, 3, 22, 10, 30, 0)


# ── Helpers ───────────────────────────────────────────────────────────────────


def _ap_event(performance_id: Any, competencia_id: Any, participante_id: Any) -> dict[str, Any]:
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


def _llamado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
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


def _resultado_event(performance_id: Any, participante_id: Any) -> dict[str, Any]:
    return {
        "event_type": "ResultadoRegistrado",
        "payload": {
            "performance_id": str(performance_id),
            "participante_id": str(participante_id),
            "disciplina": Disciplina.DNF.value,
            "valor_rp": "50.5",
            "unidad": "Metros",
            "registrado_por": "juez-001",
            "registrado_en": datetime(2026, 3, 22, 10, 35, 0).isoformat(),
            "occurred_at": datetime(2026, 3, 22, 10, 35, 0).isoformat(),
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
def mock_event_store_con_resultado(
    performance_id: Any, competencia_id: Any, participante_id: Any
) -> AsyncMock:
    """EventStore mock con stream en estado ResultadoRegistrado."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
        _resultado_event(performance_id, participante_id),
    ]
    store.append.return_value = None
    return store


def _make_command(
    competencia_id: Any,
    participante_id: Any,
    tipo: TipoTarjeta = TipoTarjeta.Blanca,
    motivo_dq: MotivoDQ | None = None,
    motivo_texto: str | None = None,
) -> AsignarTarjetaCommand:
    return AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DNF,
        tipo=tipo,
        asignada_por="juez-001",
        motivo_dq=motivo_dq,
        motivo_texto=motivo_texto,
    )


# ── Camino feliz — tarjeta blanca ─────────────────────────────────────────────


@pytest.mark.asyncio
async def test_asignar_tarjeta_blanca_persiste_evento(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """AsignarTarjetaHandler persiste TarjetaAsignada en el Event Store."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = _make_command(competencia_id, participante_id, TipoTarjeta.Blanca)

    await handler.handle(command)

    mock_event_store_con_resultado.append.assert_called_once()
    call_kwargs = mock_event_store_con_resultado.append.call_args.kwargs
    assert call_kwargs["event_type"] == "TarjetaAsignada"


@pytest.mark.asyncio
async def test_asignar_tarjeta_blanca_payload_correcto(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El payload de TarjetaAsignada (Blanca) contiene campos de motivo en null."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = _make_command(competencia_id, participante_id, TipoTarjeta.Blanca)

    await handler.handle(command)

    payload = mock_event_store_con_resultado.append.call_args.kwargs["payload"]
    assert payload["tipo"] == "Blanca"
    assert payload["motivo_dq_codigo"] is None
    assert payload["motivo_texto"] is None
    assert payload["asignada_por"] == "juez-001"


@pytest.mark.asyncio
async def test_asignar_tarjeta_amarilla_con_motivo_persiste(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """AsignarTarjetaHandler persiste TarjetaAsignada (Amarilla) con motivo."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = _make_command(
        competencia_id,
        participante_id,
        TipoTarjeta.Amarilla,
        motivo_texto="superficie sin protocolo",
    )

    await handler.handle(command)

    payload = mock_event_store_con_resultado.append.call_args.kwargs["payload"]
    assert payload["tipo"] == "Amarilla"
    assert payload["motivo_texto"] == "superficie sin protocolo"
    assert payload["motivo_dq_codigo"] is None


@pytest.mark.asyncio
async def test_asignar_tarjeta_roja_con_motivo_dq_persiste(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """AsignarTarjetaHandler persiste TarjetaAsignada (Roja) con MotivoDQ."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = _make_command(
        competencia_id,
        participante_id,
        TipoTarjeta.Roja,
        motivo_dq=MotivoDQ.PROTOCOLO_SUPERFICIE,
    )

    await handler.handle(command)

    payload = mock_event_store_con_resultado.append.call_args.kwargs["payload"]
    assert payload["tipo"] == "Roja"
    assert payload["motivo_dq_codigo"] == MotivoDQ.PROTOCOLO_SUPERFICIE.value
    assert payload["motivo_texto"] is None


# ── Performance no encontrada ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_asignar_tarjeta_stream_vacio_lanza_excepcion(
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """PerformanceNoEncontrada si no existe stream para este atleta."""
    store = AsyncMock()
    store.load.return_value = []

    handler = AsignarTarjetaHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(PerformanceNoEncontrada):
        await handler.handle(command)


# ── INV-P-07: Performance en estado ResultadoRegistrado ──────────────────────


@pytest.mark.asyncio
async def test_asignar_tarjeta_desde_llamada_lanza_excepcion(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-07: EstadoInvalidoParaAsignarTarjeta si Performance en Llamada."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
    ]

    handler = AsignarTarjetaHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaAsignarTarjeta):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_asignar_tarjeta_estado_invalido_no_persiste(
    performance_id: Any,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Si el estado es inválido no se persiste ningún evento."""
    store = AsyncMock()
    store.load.return_value = [
        _ap_event(performance_id, competencia_id, participante_id),
        _llamado_event(performance_id, participante_id),
    ]

    handler = AsignarTarjetaHandler(store)
    command = _make_command(competencia_id, participante_id)

    with pytest.raises(EstadoInvalidoParaAsignarTarjeta):
        await handler.handle(command)

    store.append.assert_not_called()


# ── INV-P-11: motivo obligatorio ──────────────────────────────────────────────


@pytest.mark.asyncio
async def test_asignar_tarjeta_amarilla_sin_motivo_lanza_excepcion(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-11: MotivoObligatorio si tarjeta Amarilla sin motivo."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = _make_command(competencia_id, participante_id, TipoTarjeta.Amarilla)

    with pytest.raises(MotivoObligatorio):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_asignar_tarjeta_roja_sin_motivo_no_persiste(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-11: si MotivoDQObligatorio falla, no se persiste ningún evento."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = _make_command(competencia_id, participante_id, TipoTarjeta.Roja)

    with pytest.raises(MotivoDQObligatorio):
        await handler.handle(command)

    mock_event_store_con_resultado.append.assert_not_called()


# ── US-1.4.1: black-out con distancia ────────────────────────────────────────


@pytest.mark.asyncio
async def test_handler_blackout_persiste_distancia(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Handler con BKO persiste TarjetaAsignada con distancia_blackout."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DNF,
        tipo=TipoTarjeta.Roja,
        asignada_por="juez-001",
        motivo_dq=MotivoDQ.BKO_SUPERFICIE,
        distancia_blackout=Decimal("45.5"),
    )
    await handler.handle(command)

    mock_event_store_con_resultado.append.assert_called_once()
    payload = mock_event_store_con_resultado.append.call_args.kwargs["payload"]
    assert payload["distancia_blackout"] == "45.5"


@pytest.mark.asyncio
async def test_handler_blackout_sin_distancia_lanza_excepcion(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Handler con BKO sin distancia lanza DistanciaBlackoutObligatoria."""
    from competencia.domain.aggregates.performance import DistanciaBlackoutObligatoria

    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DNF,
        tipo=TipoTarjeta.Roja,
        asignada_por="juez-001",
        motivo_dq=MotivoDQ.BKO_SUPERFICIE,
    )
    with pytest.raises(DistanciaBlackoutObligatoria):
        await handler.handle(command)

    mock_event_store_con_resultado.append.assert_not_called()


@pytest.mark.asyncio
async def test_handler_motivo_no_bko_rechaza_distancia(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Los motivos no BKO rechazan distancia_blackout."""
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DNF,
        tipo=TipoTarjeta.Roja,
        asignada_por="juez-001",
        motivo_dq=MotivoDQ.SALIDA_EN_FALSO,
        distancia_blackout=Decimal("20"),
    )

    with pytest.raises(DistanciaBlackoutNoAplica):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_handler_blanca_con_penalizaciones_persiste_rp_penalizado(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    for event in mock_event_store_con_resultado.load.return_value:
        event["payload"]["disciplina"] = Disciplina.DYN.value

    command = AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DYN,
        tipo=TipoTarjeta.BlancaConPenalizaciones,
        asignada_por="juez-001",
        penalizaciones=(PenalizacionTecnica(TipoPenalizacion.SIN_CONTACTO_PARED, Decimal("3")),),
    )
    await handler.handle(command)

    payload = mock_event_store_con_resultado.append.call_args.kwargs["payload"]
    assert payload["tipo"] == TipoTarjeta.BlancaConPenalizaciones.value
    assert payload["rp_medido"] == "50.5"
    assert payload["rp_penalizado"] == "47.5"
    assert len(payload["penalizaciones"]) == 1


@pytest.mark.asyncio
async def test_handler_blanca_con_penalizaciones_vacia_lanza_error(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    for event in mock_event_store_con_resultado.load.return_value:
        event["payload"]["disciplina"] = Disciplina.DYN.value

    command = AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.DYN,
        tipo=TipoTarjeta.BlancaConPenalizaciones,
        asignada_por="juez-001",
        penalizaciones=(),
    )
    with pytest.raises(PenalizacionesObligatorias):
        await handler.handle(command)


@pytest.mark.asyncio
async def test_handler_penalizaciones_en_sta_lanza_error(
    mock_event_store_con_resultado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    handler = AsignarTarjetaHandler(mock_event_store_con_resultado)
    command = AsignarTarjetaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        tipo=TipoTarjeta.BlancaConPenalizaciones,
        asignada_por="juez-001",
        penalizaciones=(PenalizacionTecnica(TipoPenalizacion.SIN_CONTACTO_PARED, Decimal("3")),),
    )
    with pytest.raises(DisciplinaNoAdmitePenalizaciones):
        await handler.handle(command)
