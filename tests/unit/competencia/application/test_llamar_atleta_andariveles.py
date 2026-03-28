"""Tests unitarios de LlamarAtletaHandler — INV-C-05 andariveles (US-2.3.1)."""
from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.llamar_atleta import (
    AndarivelesConflicto,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
)
from competencia.domain.value_objects.disciplina import Disciplina

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


def _make_command(
    competencia_id: Any, participante_id: Any, andarivel: int = 1
) -> LlamarAtletaCommand:
    return LlamarAtletaCommand(
        competencia_id=competencia_id,
        participante_id=participante_id,
        disciplina=Disciplina.STA,
        ot_programado=OT,
        posicion_grilla=1,
        andarivel=andarivel,
    )


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def competencia_id() -> Any:
    return uuid4()


@pytest.fixture
def participante_id() -> Any:
    return uuid4()


@pytest.fixture
def mock_store_con_ap(competencia_id: Any, participante_id: Any) -> AsyncMock:
    pid = uuid4()
    store = AsyncMock()
    store.load.return_value = [_ap_payload(pid, competencia_id, participante_id)]
    store.append.return_value = None
    return store


@pytest.fixture
def mock_en_ejecucion() -> AsyncMock:
    estado = AsyncMock()
    estado.is_en_ejecucion.return_value = True
    return estado


@pytest.fixture
def mock_andarivel_libre() -> AsyncMock:
    """AndarivelesActivosPort: andarivel libre."""
    port = AsyncMock()
    port.is_andarivel_activo.return_value = False
    return port


@pytest.fixture
def mock_andarivel_ocupado() -> AsyncMock:
    """AndarivelesActivosPort: andarivel ya ocupado."""
    port = AsyncMock()
    port.is_andarivel_activo.return_value = True
    return port


# ── Tests INV-C-05 ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_llamar_andarivel_libre_persiste_evento(
    mock_store_con_ap: AsyncMock,
    mock_en_ejecucion: AsyncMock,
    mock_andarivel_libre: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Llamar en andarivel libre persiste AtletaLlamado."""
    handler = LlamarAtletaHandler(mock_store_con_ap, mock_en_ejecucion, mock_andarivel_libre)
    await handler.handle(_make_command(competencia_id, participante_id, andarivel=2))

    mock_store_con_ap.append.assert_called_once()
    call_kwargs = mock_store_con_ap.append.call_args.kwargs
    assert call_kwargs["event_type"] == "AtletaLlamado"
    assert call_kwargs["payload"]["andarivel"] == 2


@pytest.mark.asyncio
async def test_llamar_andarivel_ocupado_lanza_conflicto(
    mock_store_con_ap: AsyncMock,
    mock_en_ejecucion: AsyncMock,
    mock_andarivel_ocupado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-C-05: AndarivelesConflicto si el andarivel ya tiene una Performance en Llamada."""
    handler = LlamarAtletaHandler(mock_store_con_ap, mock_en_ejecucion, mock_andarivel_ocupado)

    with pytest.raises(AndarivelesConflicto):
        await handler.handle(_make_command(competencia_id, participante_id, andarivel=1))


@pytest.mark.asyncio
async def test_llamar_andarivel_ocupado_no_persiste(
    mock_store_con_ap: AsyncMock,
    mock_en_ejecucion: AsyncMock,
    mock_andarivel_ocupado: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """INV-C-05: no se persiste ningún evento si el andarivel está ocupado."""
    handler = LlamarAtletaHandler(mock_store_con_ap, mock_en_ejecucion, mock_andarivel_ocupado)

    with pytest.raises(AndarivelesConflicto):
        await handler.handle(_make_command(competencia_id, participante_id, andarivel=1))

    mock_store_con_ap.append.assert_not_called()


@pytest.mark.asyncio
async def test_llamar_sin_port_andariveles_omite_verificacion(
    mock_store_con_ap: AsyncMock,
    mock_en_ejecucion: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """Sin AndarivelesActivosPort la verificación INV-C-05 se omite (backward compat)."""
    handler = LlamarAtletaHandler(mock_store_con_ap, mock_en_ejecucion)
    await handler.handle(_make_command(competencia_id, participante_id))

    mock_store_con_ap.append.assert_called_once()


@pytest.mark.asyncio
async def test_llamar_verifica_andarivel_correcto(
    mock_store_con_ap: AsyncMock,
    mock_en_ejecucion: AsyncMock,
    mock_andarivel_libre: AsyncMock,
    competencia_id: Any,
    participante_id: Any,
) -> None:
    """El port recibe el número de andarivel del command."""
    handler = LlamarAtletaHandler(mock_store_con_ap, mock_en_ejecucion, mock_andarivel_libre)
    await handler.handle(_make_command(competencia_id, participante_id, andarivel=3))

    mock_andarivel_libre.is_andarivel_activo.assert_called_once()
    call_args = mock_andarivel_libre.is_andarivel_activo.call_args
    assert call_args.args[2] == 3  # numero_andarivel
