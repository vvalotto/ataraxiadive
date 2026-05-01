"""Tests unitarios de ObtenerOverallHandler — US-3.5.3 / US-5.6.4."""

from __future__ import annotations

from decimal import Decimal
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.domain.value_objects.categoria import Categoria
from resultados.application.queries.obtener_overall import (
    ObtenerOverallHandler,
    ObtenerOverallQuery,
)


def _raw_event_ranking_overall_calculado(torneo_id, atleta_id_1, atleta_id_2) -> dict[str, Any]:
    return {
        "event_type": "RankingOverallCalculado",
        "payload": {
            "torneo_id": str(torneo_id),
            "disciplinas": ["STA", "DNF"],
            "total": 2,
            "entries": [
                {
                    "posicion": 1,
                    "atleta_id": str(atleta_id_1),
                    "categoria": Categoria.SENIOR_MASCULINO.value,
                    "puntos_overall": "175.00",
                    "detalle": {"STA": "100.00", "DNF": "75.00"},
                    "en_podio": True,
                },
                {
                    "posicion": 2,
                    "atleta_id": str(atleta_id_2),
                    "categoria": Categoria.SENIOR_MASCULINO.value,
                    "puntos_overall": "140.00",
                    "detalle": {"STA": "80.00", "DNF": "60.00"},
                    "en_podio": True,
                },
            ],
            "calculado_en": "2026-04-02T12:00:00+00:00",
            "occurred_at": "2026-04-02T12:00:00+00:00",
        },
    }


class TestObtenerOverallHandler:
    @pytest.mark.asyncio
    async def test_handle_sin_eventos_devuelve_lista_vacia(self) -> None:
        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(return_value=[])

        handler = ObtenerOverallHandler(ranking_store=ranking_store)
        result = await handler.handle(ObtenerOverallQuery(torneo_id=uuid4()))

        assert result == []

    @pytest.mark.asyncio
    async def test_handle_con_evento_devuelve_entradas(self) -> None:
        torneo_id = uuid4()
        atleta_id_1 = uuid4()
        atleta_id_2 = uuid4()
        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(
            return_value=[_raw_event_ranking_overall_calculado(torneo_id, atleta_id_1, atleta_id_2)]
        )

        handler = ObtenerOverallHandler(ranking_store=ranking_store)
        result = await handler.handle(ObtenerOverallQuery(torneo_id=torneo_id))

        assert len(result) == 1
        assert result[0].categoria == Categoria.SENIOR_MASCULINO.value
        assert len(result[0].entradas) == 2
        assert result[0].entradas[0].atleta_id == str(atleta_id_1)
        assert result[0].entradas[0].puntos_overall == Decimal("175.00")
        assert result[0].entradas[0].detalle == {
            "STA": Decimal("100.00"),
            "DNF": Decimal("75.00"),
        }
        assert result[0].entradas[0].en_podio is True
        assert result[0].entradas[1].atleta_id == str(atleta_id_2)
        assert result[0].entradas[1].puntos_overall == Decimal("140.00")

    @pytest.mark.asyncio
    async def test_handle_lee_stream_correcto(self) -> None:
        torneo_id = uuid4()
        ranking_store = AsyncMock()
        ranking_store.load = AsyncMock(return_value=[])

        handler = ObtenerOverallHandler(ranking_store=ranking_store)
        await handler.handle(ObtenerOverallQuery(torneo_id=torneo_id))

        ranking_store.load.assert_called_once_with(f"ranking-overall-{torneo_id}")
