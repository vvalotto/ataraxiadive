"""Tests unitarios — ObtenerCompetenciasPorTorneoHandler (US-3.3.1)."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from competencia.application.queries.obtener_competencias_por_torneo import (
    ObtenerCompetenciasPorTorneoHandler,
    ObtenerCompetenciasPorTorneoQuery,
)

TORNEO_A = UUID("00000000-0000-0000-0000-000000000010")
TORNEO_B = UUID("00000000-0000-0000-0000-000000000020")
COMP_1 = UUID("00000000-0000-0000-0000-000000000001")
COMP_2 = UUID("00000000-0000-0000-0000-000000000002")
COMP_3 = UUID("00000000-0000-0000-0000-000000000003")


def _make_stream(comp_id: UUID, disciplina: str, torneo_id: UUID | None) -> list[dict]:
    return [
        {
            "event_type": "IntervaloOTConfigurado",
            "payload": {
                "competencia_id": str(comp_id),
                "disciplina": disciplina,
                "intervalo_minutos": 9,
                "configurado_por": "org-01",
                "torneo_id": str(torneo_id) if torneo_id else None,
                "occurred_at": "2026-01-01T00:00:00",
            },
        }
    ]


@pytest.fixture
def mock_event_store() -> AsyncMock:
    return AsyncMock()


@pytest.fixture
def handler(mock_event_store: AsyncMock) -> ObtenerCompetenciasPorTorneoHandler:
    return ObtenerCompetenciasPorTorneoHandler(mock_event_store)


class TestObtenerCompetenciasPorTorneo:
    @pytest.mark.asyncio
    async def test_retorna_competencias_del_torneo(
        self, handler: ObtenerCompetenciasPorTorneoHandler, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load_all_streams_with_prefix.return_value = [
            _make_stream(COMP_1, "STA", TORNEO_A),
            _make_stream(COMP_2, "DNF", TORNEO_A),
            _make_stream(COMP_3, "DYN", TORNEO_B),
        ]
        result = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        assert len(result) == 2
        ids = {r.competencia_id for r in result}
        assert COMP_1 in ids
        assert COMP_2 in ids

    @pytest.mark.asyncio
    async def test_excluye_competencias_de_otro_torneo(
        self, handler: ObtenerCompetenciasPorTorneoHandler, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load_all_streams_with_prefix.return_value = [
            _make_stream(COMP_1, "STA", TORNEO_A),
            _make_stream(COMP_3, "DYN", TORNEO_B),
        ]
        result = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_B))
        assert len(result) == 1
        assert result[0].competencia_id == COMP_3

    @pytest.mark.asyncio
    async def test_excluye_competencias_sin_torneo_id(
        self, handler: ObtenerCompetenciasPorTorneoHandler, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load_all_streams_with_prefix.return_value = [
            _make_stream(COMP_1, "STA", TORNEO_A),
            _make_stream(COMP_2, "DNF", None),  # standalone
        ]
        result = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        assert len(result) == 1
        assert result[0].competencia_id == COMP_1

    @pytest.mark.asyncio
    async def test_retorna_lista_vacia_si_no_hay_competencias(
        self, handler: ObtenerCompetenciasPorTorneoHandler, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load_all_streams_with_prefix.return_value = []
        result = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        assert result == []

    @pytest.mark.asyncio
    async def test_dto_contiene_disciplina_correcta(
        self, handler: ObtenerCompetenciasPorTorneoHandler, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load_all_streams_with_prefix.return_value = [
            _make_stream(COMP_1, "STA", TORNEO_A),
        ]
        result = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        assert result[0].disciplina == "STA"
        assert result[0].torneo_id == TORNEO_A

    @pytest.mark.asyncio
    async def test_usa_prefijo_competencia_para_cargar(
        self, handler: ObtenerCompetenciasPorTorneoHandler, mock_event_store: AsyncMock
    ) -> None:
        mock_event_store.load_all_streams_with_prefix.return_value = []
        await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        mock_event_store.load_all_streams_with_prefix.assert_called_once_with("competencia-")
