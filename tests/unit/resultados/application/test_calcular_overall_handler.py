"""Tests unitarios del CalcularOverallHandler — US-3.5.1."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from shared.domain.value_objects.disciplina import Disciplina


def _competencia_event(competencia_id, torneo_id, disciplina: Disciplina) -> dict:
    return {
        "event_type": "IntervaloOTConfigurado",
        "payload": {
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "intervalo_minutos": 3,
            "configurado_por": "organizador",
            "torneo_id": str(torneo_id),
            "occurred_at": "2026-04-02T12:00:00+00:00",
        },
    }


def _ranking_event(competencia_id, disciplina: Disciplina, atleta_id, posicion: int) -> dict:
    return {
        "event_type": "ResultadosCalculados",
        "payload": {
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "total": 1,
            "entries": [
                {
                    "posicion": posicion,
                    "atleta_id": str(atleta_id),
                    "rp": "300",
                    "unidad": "Segundos",
                    "tarjeta": "Blanca",
                    "es_dns": False,
                    "en_podio": True,
                }
            ],
            "calculado_en": "2026-04-02T12:00:00+00:00",
            "occurred_at": "2026-04-02T12:00:00+00:00",
        },
    }


@pytest.mark.asyncio
async def test_handle_persiste_ranking_overall_calculado() -> None:
    torneo_id = uuid4()
    competencia_sta = uuid4()
    atleta_id = uuid4()

    ranking_store = AsyncMock()
    ranking_store.load = AsyncMock(
        side_effect=[
            [_ranking_event(competencia_sta, Disciplina.STA, atleta_id, 1)],
            [],
        ]
    )
    ranking_store.append = AsyncMock()

    competencia_store = AsyncMock()
    competencia_store.load_all_streams_with_prefix = AsyncMock(
        return_value=[[_competencia_event(competencia_sta, torneo_id, Disciplina.STA)]]
    )

    handler = CalcularOverallHandler(ranking_store, competencia_store)
    await handler.handle(CalcularOverallCommand(torneo_id=torneo_id, disciplinas=[Disciplina.STA]))

    ranking_store.append.assert_called_once()
    call = ranking_store.append.call_args.kwargs
    assert call["stream_id"] == f"ranking-overall-{torneo_id}"
    assert call["event_type"] == "RankingOverallCalculado"


@pytest.mark.asyncio
async def test_handle_sin_rankings_fuente_no_persiste() -> None:
    torneo_id = uuid4()
    competencia_id = uuid4()

    ranking_store = AsyncMock()
    ranking_store.load = AsyncMock(side_effect=[[], []])
    ranking_store.append = AsyncMock()

    competencia_store = AsyncMock()
    competencia_store.load_all_streams_with_prefix = AsyncMock(
        return_value=[[_competencia_event(competencia_id, torneo_id, Disciplina.STA)]]
    )

    handler = CalcularOverallHandler(ranking_store, competencia_store)
    result = await handler.handle(
        CalcularOverallCommand(torneo_id=torneo_id, disciplinas=[Disciplina.STA])
    )

    assert result == []
    ranking_store.append.assert_not_called()
