"""Tests unitarios del AjustarGrillaHandler — US-2.1.3."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from competencia.application.commands.ajustar_grilla import (
    AjustarGrillaCommand,
    AjustarGrillaHandler,
    _build_stream_id,
)
from competencia.domain.exceptions import GrillaNoGenerada, GrillaYaConfirmada
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
A001 = UUID("00000000-0000-0000-0000-000000000011")
A002 = UUID("00000000-0000-0000-0000-000000000012")
P_A001 = uuid4()
P_A002 = uuid4()

_INTERVALO_EVENT = {
    "event_type": "IntervaloOTConfigurado",
    "payload": {
        "competencia_id": str(COMPETENCIA_ID),
        "disciplina": "STA",
        "intervalo_minutos": 9,
        "configurado_por": "org",
        "occurred_at": "2026-01-01T00:00:00+00:00",
    },
}

_GRILLA_GENERADA_EVENT = {
    "event_type": "GrillaDeSalidaGenerada",
    "payload": {
        "competencia_id": str(COMPETENCIA_ID),
        "disciplina": "STA",
        "ot_inicio": OT_INICIO.isoformat(),
        "performances": [
            {
                "performance_id": str(P_A002),
                "atleta_id": str(A002),
                "posicion": 1,
                "andarivel": 1,
                "ot_programado": OT_INICIO.isoformat(),
            },
            {
                "performance_id": str(P_A001),
                "atleta_id": str(A001),
                "posicion": 2,
                "andarivel": 1,
                "ot_programado": (OT_INICIO + timedelta(minutes=9)).isoformat(),
            },
        ],
        "generada_en": OT_INICIO.isoformat(),
        "occurred_at": OT_INICIO.isoformat(),
    },
}


@pytest.fixture
def mock_event_store() -> AsyncMock:
    store = AsyncMock()
    store.load.return_value = [_INTERVALO_EVENT, _GRILLA_GENERADA_EVENT]
    store.append.return_value = None
    return store


def _command(cambios: list[CambioGrilla] | None = None) -> AjustarGrillaCommand:
    return AjustarGrillaCommand(
        competencia_id=COMPETENCIA_ID,
        disciplina=Disciplina.STA,
        cambios=cambios or [CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)],
    )


class TestAjustarGrillaHandlerExitoso:
    @pytest.mark.asyncio
    async def test_append_llamado_una_vez(self, mock_event_store: AsyncMock) -> None:
        handler = AjustarGrillaHandler(mock_event_store)
        await handler.handle(_command())
        assert mock_event_store.append.call_count == 1

    @pytest.mark.asyncio
    async def test_event_type_correcto(self, mock_event_store: AsyncMock) -> None:
        handler = AjustarGrillaHandler(mock_event_store)
        await handler.handle(_command())
        assert mock_event_store.append.call_args[1]["event_type"] == "GrillaDeSalidaAjustada"

    @pytest.mark.asyncio
    async def test_load_con_stream_id_correcto(self, mock_event_store: AsyncMock) -> None:
        handler = AjustarGrillaHandler(mock_event_store)
        await handler.handle(_command())
        mock_event_store.load.assert_called_once_with(_build_stream_id(COMPETENCIA_ID))


class TestAjustarGrillaHandlerErrores:
    @pytest.mark.asyncio
    async def test_sin_grilla_generada_lanza_excepcion(self) -> None:
        store = AsyncMock()
        store.load.return_value = [_INTERVALO_EVENT]  # sin GrillaDeSalidaGenerada
        handler = AjustarGrillaHandler(store)
        with pytest.raises(GrillaNoGenerada):
            await handler.handle(_command())

    @pytest.mark.asyncio
    async def test_grilla_confirmada_lanza_excepcion(self) -> None:
        store = AsyncMock()
        store.load.return_value = [
            _INTERVALO_EVENT,
            _GRILLA_GENERADA_EVENT,
            {"event_type": "GrillaConfirmada", "payload": {"competencia_id": str(COMPETENCIA_ID)}},
        ]
        handler = AjustarGrillaHandler(store)
        with pytest.raises(GrillaYaConfirmada):
            await handler.handle(_command())

    @pytest.mark.asyncio
    async def test_append_no_llamado_si_error(self) -> None:
        store = AsyncMock()
        store.load.return_value = [_INTERVALO_EVENT]  # sin grilla
        handler = AjustarGrillaHandler(store)
        with pytest.raises(GrillaNoGenerada):
            await handler.handle(_command())
        store.append.assert_not_called()
