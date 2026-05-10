"""Tests unitarios del CalcularOverallHandler — US-3.5.1 / US-5.6.4."""

from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.domain.ports.competencias_por_torneo_port import CompetenciaPorTorneoRecord
from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from resultados.domain.exceptions import DisciplinasNoFinalizadas
from shared.domain.value_objects.disciplina import Disciplina


def _ranking_event(
    competencia_id, disciplina: Disciplina, atleta_id, puntos: str = "80.00"
) -> dict:
    return {
        "event_type": "ResultadosCalculados",
        "payload": {
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "total": 1,
            "entries": [
                {
                    "posicion": 1,
                    "atleta_id": str(atleta_id),
                    "rp": "300",
                    "unidad": "Segundos",
                    "tarjeta": "Blanca",
                    "es_dns": False,
                    "en_podio": True,
                    "puntos": puntos,
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
            [_ranking_event(competencia_sta, Disciplina.STA, atleta_id, "100.00")],
            [],
        ]
    )
    ranking_store.append = AsyncMock()

    competencias_por_torneo = AsyncMock()
    competencias_por_torneo.listar_por_torneo = AsyncMock(
        return_value=[
            CompetenciaPorTorneoRecord(
                competencia_id=competencia_sta,
                disciplina=Disciplina.STA.value,
                torneo_id=torneo_id,
            )
        ]
    )
    competencia_store = AsyncMock()

    handler = CalcularOverallHandler(ranking_store, competencias_por_torneo)
    await handler.handle(CalcularOverallCommand(torneo_id=torneo_id, disciplinas=[Disciplina.STA]))

    competencias_por_torneo.listar_por_torneo.assert_awaited_once_with(torneo_id)
    competencia_store.load_all_streams_with_prefix.assert_not_called()
    ranking_store.append.assert_called_once()
    call = ranking_store.append.call_args.kwargs
    assert call["stream_id"] == f"ranking-overall-{torneo_id}"
    assert call["event_type"] == "RankingOverallCalculado"


@pytest.mark.asyncio
async def test_handle_disciplina_sin_ranking_lanza_excepcion() -> None:
    """INV-5.6.4-04: disciplina sin ranking calculado → DisciplinasNoFinalizadas."""
    torneo_id = uuid4()
    competencia_id = uuid4()

    ranking_store = AsyncMock()
    ranking_store.load = AsyncMock(side_effect=[[], []])
    ranking_store.append = AsyncMock()

    competencias_por_torneo = AsyncMock()
    competencias_por_torneo.listar_por_torneo = AsyncMock(
        return_value=[
            CompetenciaPorTorneoRecord(
                competencia_id=competencia_id,
                disciplina=Disciplina.STA.value,
                torneo_id=torneo_id,
            )
        ]
    )

    handler = CalcularOverallHandler(ranking_store, competencias_por_torneo)

    with pytest.raises(DisciplinasNoFinalizadas):
        await handler.handle(
            CalcularOverallCommand(torneo_id=torneo_id, disciplinas=[Disciplina.STA])
        )

    ranking_store.append.assert_not_called()


@pytest.mark.asyncio
async def test_handle_torneo_sin_competencias_materializadas_retorna_vacio() -> None:
    torneo_id = uuid4()

    ranking_store = AsyncMock()
    ranking_store.load = AsyncMock()
    ranking_store.append = AsyncMock()
    competencias_por_torneo = AsyncMock()
    competencias_por_torneo.listar_por_torneo = AsyncMock(return_value=[])

    handler = CalcularOverallHandler(ranking_store, competencias_por_torneo)

    result = await handler.handle(
        CalcularOverallCommand(torneo_id=torneo_id, disciplinas=[Disciplina.STA])
    )

    assert result == []
    competencias_por_torneo.listar_por_torneo.assert_awaited_once_with(torneo_id)
    ranking_store.load.assert_not_called()
    ranking_store.append.assert_not_called()
