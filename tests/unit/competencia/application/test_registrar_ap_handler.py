"""Tests unitarios del RegistrarAPHandler — US-1.2.1."""
from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.registrar_ap import (
    APYaRegistrado,
    GrillaYaConfirmadaError,
    PlazoAPVencidoError,
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.value_objects.ap import ValorAPInvalido
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def competencia_id() -> Any:
    return uuid4()


@pytest.fixture
def participante_id() -> Any:
    return uuid4()


@pytest.fixture
def mock_event_store() -> AsyncMock:
    """EventStorePort mock: stream vacío y append sin efecto."""
    store = AsyncMock()
    store.load.return_value = []
    store.append.return_value = None
    return store


@pytest.fixture
def mock_estado_port() -> AsyncMock:
    """CompetenciaEstadoPort mock: plazo activo, grilla no confirmada."""
    estado = AsyncMock()
    estado.is_plazo_vencido.return_value = False
    estado.is_grilla_confirmada.return_value = False
    return estado


@pytest.fixture
def handler(mock_event_store: AsyncMock, mock_estado_port: AsyncMock) -> RegistrarAPHandler:
    return RegistrarAPHandler(
        event_store=mock_event_store,
        competencia_estado=mock_estado_port,
        disciplina_descriptor=DisciplinaDescriptorAdapter(),
    )


def make_command(
    competencia_id: Any,
    participante_id: Any,
    valor: str = "330",
    unidad: UnidadMedida = UnidadMedida.Segundos,
    disciplina: Disciplina = Disciplina.STA,
) -> RegistrarAPCommand:
    return RegistrarAPCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=disciplina,
        valor_ap=Decimal(valor),
        unidad=unidad,
    )


# ── Happy path ────────────────────────────────────────────────────────────────


async def test_handle_retorna_performance_id(
    handler: RegistrarAPHandler,
    mock_event_store: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """handle retorna un UUID como performance_id."""
    cmd = make_command(competencia_id, participante_id)
    result = await handler.handle(cmd)

    assert result is not None
    mock_event_store.append.assert_called_once()


async def test_handle_llama_append_con_ap_registrado(
    handler: RegistrarAPHandler,
    mock_event_store: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """handle llama append con event_type=APRegistrado."""
    cmd = make_command(competencia_id, participante_id)
    await handler.handle(cmd)

    call_kwargs = mock_event_store.append.call_args
    assert call_kwargs.kwargs["event_type"] == "APRegistrado"


async def test_handle_stream_id_contiene_natural_key(
    handler: RegistrarAPHandler,
    mock_event_store: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El stream_id incluye competencia_id, participante_id y disciplina."""
    cmd = make_command(competencia_id, participante_id, disciplina=Disciplina.DNF, unidad=UnidadMedida.Metros)
    await handler.handle(cmd)

    call_kwargs = mock_event_store.append.call_args
    stream_id = call_kwargs.kwargs["stream_id"]
    assert str(competencia_id) in stream_id
    assert str(participante_id) in stream_id
    assert "DNF" in stream_id


# ── INV-P-02: AP ya registrado ────────────────────────────────────────────────


async def test_handle_ap_ya_registrado_lanza_excepcion(
    handler: RegistrarAPHandler,
    mock_event_store: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-02: stream no vacío lanza APYaRegistrado."""
    mock_event_store.load.return_value = [{"event_type": "APRegistrado", "payload": {}}]

    cmd = make_command(competencia_id, participante_id)
    with pytest.raises(APYaRegistrado):
        await handler.handle(cmd)

    mock_event_store.append.assert_not_called()


# ── INV-P-03: plazo vencido ───────────────────────────────────────────────────


async def test_handle_plazo_vencido_lanza_excepcion(
    handler: RegistrarAPHandler,
    mock_estado_port: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-03: is_plazo_vencido=True lanza PlazoAPVencidoError."""
    mock_estado_port.is_plazo_vencido.return_value = True

    cmd = make_command(competencia_id, participante_id)
    with pytest.raises(PlazoAPVencidoError):
        await handler.handle(cmd)


# ── INV-P-04: grilla confirmada ───────────────────────────────────────────────


async def test_handle_grilla_confirmada_lanza_excepcion(
    handler: RegistrarAPHandler,
    mock_estado_port: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-04: is_grilla_confirmada=True lanza GrillaYaConfirmadaError."""
    mock_estado_port.is_grilla_confirmada.return_value = True

    cmd = make_command(competencia_id, participante_id)
    with pytest.raises(GrillaYaConfirmadaError):
        await handler.handle(cmd)


# ── INV-P-01 vía handler ──────────────────────────────────────────────────────


async def test_handle_valor_cero_lanza_valor_ap_invalido(
    handler: RegistrarAPHandler,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-P-01: valor=0 propagado desde AP value object."""
    cmd = make_command(competencia_id, participante_id, valor="0")
    with pytest.raises(ValorAPInvalido):
        await handler.handle(cmd)


# ── US-2.2.2: validación de unidad ────────────────────────────────────────────


async def test_handle_unidad_incompatible_lanza_excepcion(
    handler: RegistrarAPHandler,
    mock_event_store: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """US-2.2.2: STA con Metros lanza UnidadIncompatible."""
    from competencia.application.commands.registrar_resultado import UnidadIncompatible

    cmd = make_command(
        competencia_id, participante_id,
        disciplina=Disciplina.STA, unidad=UnidadMedida.Metros,  # STA requiere Segundos
    )
    with pytest.raises(UnidadIncompatible):
        await handler.handle(cmd)

    mock_event_store.append.assert_not_called()
