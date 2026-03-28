"""Tests unitarios del ConfigurarIntervaloOTHandler — US-2.1.1."""
from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, call
from uuid import UUID, uuid4

import pytest

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands._stream_ids import competencia_stream_id as _build_stream_id
from competencia.domain.exceptions import GrillaYaConfirmada
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.intervalo_disciplina import IntervaloInvalido

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
DISCIPLINA = Disciplina.STA
CONFIGURADO_POR = "organizador-01"


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def mock_event_store() -> AsyncMock:
    """EventStorePort mock: stream vacío y append sin efecto."""
    store = AsyncMock()
    store.load.return_value = []
    store.append.return_value = None
    return store


@pytest.fixture
def handler(mock_event_store: AsyncMock) -> ConfigurarIntervaloOTHandler:
    return ConfigurarIntervaloOTHandler(mock_event_store)


def _command(intervalo_minutos: int = 9) -> ConfigurarIntervaloOTCommand:
    return ConfigurarIntervaloOTCommand(
        competencia_id=COMPETENCIA_ID,
        disciplina=DISCIPLINA,
        intervalo_minutos=intervalo_minutos,
        configurado_por=CONFIGURADO_POR,
    )


# ── Happy paths ───────────────────────────────────────────────────────────────


class TestConfiguracionExitosa:
    @pytest.mark.asyncio
    async def test_append_llamado_una_vez(self, handler: ConfigurarIntervaloOTHandler, mock_event_store: AsyncMock) -> None:
        await handler.handle(_command(9))
        assert mock_event_store.append.call_count == 1

    @pytest.mark.asyncio
    async def test_append_con_stream_id_correcto(self, handler: ConfigurarIntervaloOTHandler, mock_event_store: AsyncMock) -> None:
        await handler.handle(_command(9))
        stream_id = _build_stream_id(COMPETENCIA_ID)
        assert mock_event_store.append.call_args[1]["stream_id"] == stream_id

    @pytest.mark.asyncio
    async def test_append_con_event_type_correcto(self, handler: ConfigurarIntervaloOTHandler, mock_event_store: AsyncMock) -> None:
        await handler.handle(_command(9))
        assert mock_event_store.append.call_args[1]["event_type"] == "IntervaloOTConfigurado"

    @pytest.mark.asyncio
    async def test_payload_contiene_intervalo(self, handler: ConfigurarIntervaloOTHandler, mock_event_store: AsyncMock) -> None:
        await handler.handle(_command(9))
        payload = mock_event_store.append.call_args[1]["payload"]
        assert payload["intervalo_minutos"] == 9

    @pytest.mark.asyncio
    async def test_load_con_stream_id_correcto(self, handler: ConfigurarIntervaloOTHandler, mock_event_store: AsyncMock) -> None:
        await handler.handle(_command(9))
        stream_id = _build_stream_id(COMPETENCIA_ID)
        mock_event_store.load.assert_called_once_with(stream_id)


class TestReconfiguracion:
    @pytest.mark.asyncio
    async def test_reconfiguracion_sobre_stream_existente(
        self, mock_event_store: AsyncMock
    ) -> None:
        """Con eventos previos en el stream, el handler reconfigura correctamente."""
        mock_event_store.load.return_value = [
            {
                "event_type": "IntervaloOTConfigurado",
                "payload": {
                    "competencia_id": str(COMPETENCIA_ID),
                    "disciplina": DISCIPLINA.value,
                    "intervalo_minutos": 7,
                    "configurado_por": CONFIGURADO_POR,
                    "occurred_at": "2026-01-01T00:00:00+00:00",
                },
            }
        ]
        handler = ConfigurarIntervaloOTHandler(mock_event_store)
        await handler.handle(_command(10))
        assert mock_event_store.append.call_count == 1
        payload = mock_event_store.append.call_args[1]["payload"]
        assert payload["intervalo_minutos"] == 10


# ── Error cases ───────────────────────────────────────────────────────────────


class TestErrores:
    @pytest.mark.asyncio
    async def test_intervalo_cero_lanza_intervalo_invalido(
        self, handler: ConfigurarIntervaloOTHandler
    ) -> None:
        with pytest.raises(IntervaloInvalido):
            await handler.handle(_command(0))

    @pytest.mark.asyncio
    async def test_intervalo_negativo_lanza_intervalo_invalido(
        self, handler: ConfigurarIntervaloOTHandler
    ) -> None:
        with pytest.raises(IntervaloInvalido):
            await handler.handle(_command(-1))

    @pytest.mark.asyncio
    async def test_grilla_confirmada_lanza_excepcion(
        self, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load.return_value = [
            {
                "event_type": "GrillaConfirmada",
                "payload": {"competencia_id": str(COMPETENCIA_ID)},
            }
        ]
        handler = ConfigurarIntervaloOTHandler(mock_event_store)
        with pytest.raises(GrillaYaConfirmada):
            await handler.handle(_command(9))

    @pytest.mark.asyncio
    async def test_append_no_llamado_si_error(
        self, handler: ConfigurarIntervaloOTHandler, mock_event_store: AsyncMock
    ) -> None:
        with pytest.raises(IntervaloInvalido):
            await handler.handle(_command(0))
        mock_event_store.append.assert_not_called()


# ── Helper ────────────────────────────────────────────────────────────────────


class TestBuildStreamId:
    def test_stream_id_formato_correcto(self) -> None:
        cid = UUID("12345678-1234-5678-1234-567812345678")
        assert _build_stream_id(cid) == f"competencia-{cid}"
