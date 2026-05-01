"""Tests unitarios del GenerarGrillaHandler — US-2.1.2."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands._stream_ids import competencia_stream_id as _build_stream_id
from competencia.domain.exceptions import (
    IntervaloNoConfigurado,
    SinPerformancesParaGrilla,
)
from competencia.domain.ports.performances_ap_port import PerformancesAPData
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
A001 = UUID("00000000-0000-0000-0000-000000000011")

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


@pytest.fixture
def mock_event_store() -> AsyncMock:
    store = AsyncMock()
    store.load.return_value = [_INTERVALO_EVENT]
    store.append.return_value = None
    return store


@pytest.fixture
def mock_performances_ap() -> AsyncMock:
    port = AsyncMock()
    port.get_performances_con_ap.return_value = [
        PerformancesAPData(
            performance_id=uuid4(),
            atleta_id=A001,
            valor_ap=Decimal("330"),
            unidad=UnidadMedida.Segundos,
        )
    ]
    return port


_DESCRIPTOR_ADAPTER = DisciplinaDescriptorAdapter()


def _command() -> GenerarGrillaCommand:
    return GenerarGrillaCommand(
        competencia_id=COMPETENCIA_ID,
        disciplina=Disciplina.STA,
        ot_inicio=OT_INICIO,
    )


class TestGenerarGrillaHandlerExitoso:
    @pytest.mark.asyncio
    async def test_append_llamado_una_vez(
        self, mock_event_store: AsyncMock, mock_performances_ap: AsyncMock
    ) -> None:
        handler = GenerarGrillaHandler(mock_event_store, mock_performances_ap, _DESCRIPTOR_ADAPTER)
        await handler.handle(_command())
        assert mock_event_store.append.call_count == 1

    @pytest.mark.asyncio
    async def test_event_type_correcto(
        self, mock_event_store: AsyncMock, mock_performances_ap: AsyncMock
    ) -> None:
        handler = GenerarGrillaHandler(mock_event_store, mock_performances_ap, _DESCRIPTOR_ADAPTER)
        await handler.handle(_command())
        assert mock_event_store.append.call_args[1]["event_type"] == "GrillaDeSalidaGenerada"

    @pytest.mark.asyncio
    async def test_performances_ap_consultado_con_competencia_id(
        self, mock_event_store: AsyncMock, mock_performances_ap: AsyncMock
    ) -> None:
        handler = GenerarGrillaHandler(mock_event_store, mock_performances_ap, _DESCRIPTOR_ADAPTER)
        await handler.handle(_command())
        mock_performances_ap.get_performances_con_ap.assert_called_once_with(COMPETENCIA_ID)

    @pytest.mark.asyncio
    async def test_load_con_stream_id_correcto(
        self, mock_event_store: AsyncMock, mock_performances_ap: AsyncMock
    ) -> None:
        handler = GenerarGrillaHandler(mock_event_store, mock_performances_ap, _DESCRIPTOR_ADAPTER)
        await handler.handle(_command())
        assert mock_event_store.load.call_args_list[0].args == (_build_stream_id(COMPETENCIA_ID),)

    @pytest.mark.asyncio
    async def test_con_dos_andariveles_comparte_ot_por_tanda(
        self, mock_event_store: AsyncMock, mock_performances_ap: AsyncMock
    ) -> None:
        mock_performances_ap.get_performances_con_ap.return_value = [
            PerformancesAPData(
                performance_id=uuid4(),
                atleta_id=UUID("00000000-0000-0000-0000-000000000011"),
                valor_ap=Decimal("360"),
                unidad=UnidadMedida.Segundos,
            ),
            PerformancesAPData(
                performance_id=uuid4(),
                atleta_id=UUID("00000000-0000-0000-0000-000000000012"),
                valor_ap=Decimal("330"),
                unidad=UnidadMedida.Segundos,
            ),
            PerformancesAPData(
                performance_id=uuid4(),
                atleta_id=UUID("00000000-0000-0000-0000-000000000013"),
                valor_ap=Decimal("285"),
                unidad=UnidadMedida.Segundos,
            ),
        ]
        handler = GenerarGrillaHandler(mock_event_store, mock_performances_ap, _DESCRIPTOR_ADAPTER)
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=Disciplina.STA,
                ot_inicio=OT_INICIO,
                andariveles=2,
            )
        )
        payload = mock_event_store.append.call_args.kwargs["payload"]
        performances = payload["performances"]
        assert performances[0]["ot_programado"] == OT_INICIO.isoformat()
        assert performances[1]["ot_programado"] == OT_INICIO.isoformat()
        assert performances[2]["ot_programado"] == (
            OT_INICIO.replace(minute=OT_INICIO.minute + 9).isoformat()
        )


class TestGenerarGrillaHandlerErrores:
    @pytest.mark.asyncio
    async def test_sin_intervalo_lanza_excepcion(self, mock_performances_ap: AsyncMock) -> None:
        store = AsyncMock()
        store.load.return_value = []  # sin IntervaloOTConfigurado
        handler = GenerarGrillaHandler(store, mock_performances_ap, _DESCRIPTOR_ADAPTER)
        with pytest.raises(IntervaloNoConfigurado):
            await handler.handle(_command())

    @pytest.mark.asyncio
    async def test_sin_performances_lanza_excepcion(self, mock_event_store: AsyncMock) -> None:
        port = AsyncMock()
        port.get_performances_con_ap.return_value = []
        handler = GenerarGrillaHandler(mock_event_store, port, _DESCRIPTOR_ADAPTER)
        with pytest.raises(SinPerformancesParaGrilla):
            await handler.handle(_command())

    @pytest.mark.asyncio
    async def test_append_no_llamado_si_error(self, mock_event_store: AsyncMock) -> None:
        port = AsyncMock()
        port.get_performances_con_ap.return_value = []
        handler = GenerarGrillaHandler(mock_event_store, port, _DESCRIPTOR_ADAPTER)
        with pytest.raises(SinPerformancesParaGrilla):
            await handler.handle(_command())
        mock_event_store.append.assert_not_called()
