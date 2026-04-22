"""Tests unitarios del cierre manual de competencia — US-5.2.2."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.commands.finalizar_competencia_manual import (
    FinalizarCompetenciaManualCommand,
    FinalizarCompetenciaManualHandler,
)
from competencia.domain.exceptions import CompetenciaNoFinalizable
from competencia.domain.ports.performances_estado_port import PerformancesEstadoData
from competencia.domain.value_objects.disciplina import Disciplina


def _competencia_events(competencia_id: Any) -> list[dict[str, Any]]:
    return [
        {
            "event_type": "GrillaConfirmada",
            "payload": {
                "competencia_id": str(competencia_id),
                "disciplina": Disciplina.STA.value,
                "confirmada_en": datetime(2026, 4, 22, 9, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 4, 22, 9, 0, 0).isoformat(),
            },
        },
        {
            "event_type": "CompetenciaIniciada",
            "payload": {
                "competencia_id": str(competencia_id),
                "disciplina": Disciplina.STA.value,
                "juez_id": "juez-1",
                "iniciada_en": datetime(2026, 4, 22, 10, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 4, 22, 10, 0, 0).isoformat(),
            },
        },
    ]


def _competencia_finalizada_events(competencia_id: Any) -> list[dict[str, Any]]:
    return [
        *_competencia_events(competencia_id),
        {
            "event_type": "CompetenciaFinalizada",
            "payload": {
                "competencia_id": str(competencia_id),
                "disciplina": Disciplina.STA.value,
                "total_performances": 1,
                "ejecutadas": 1,
                "dns_count": 0,
                "finalizada_en": datetime(2026, 4, 22, 11, 0, 0).isoformat(),
                "hash_sha256": "a" * 64,
                "origen": "automatico",
                "finalizada_por": None,
                "occurred_at": datetime(2026, 4, 22, 11, 0, 0).isoformat(),
            },
        },
    ]


@pytest.mark.asyncio
async def test_finalizar_manual_persiste_origen_manual() -> None:
    competencia_id = uuid4()
    store = AsyncMock()
    store.load.return_value = _competencia_events(competencia_id)
    store.load_all_events_ordered.return_value = [
        {
            "sequence": 1,
            "stream_id": f"performance-{competencia_id}-{uuid4()}-{Disciplina.STA.value}",
            "event_type": "TarjetaAsignada",
            "payload": {"tipo": "Blanca"},
            "occurred_at": "2026-04-22T11:00:00",
        }
    ]
    estado = AsyncMock()
    estado.get_estado.return_value = PerformancesEstadoData(total=2, ejecutadas=1, dns_count=1)
    handler = FinalizarCompetenciaManualHandler(store, estado)

    await handler.handle(
        FinalizarCompetenciaManualCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            solicitado_por="org@ataraxia.com",
        )
    )

    payload = store.append.call_args.kwargs["payload"]
    assert store.append.call_args.kwargs["event_type"] == "CompetenciaFinalizada"
    assert payload["origen"] == "manual"
    assert payload["finalizada_por"] == "org@ataraxia.com"
    assert len(payload["hash_sha256"]) == 64


@pytest.mark.asyncio
async def test_finalizar_manual_rechaza_si_quedan_pendientes() -> None:
    competencia_id = uuid4()
    store = AsyncMock()
    store.load.return_value = _competencia_events(competencia_id)
    estado = AsyncMock()
    estado.get_estado.return_value = PerformancesEstadoData(total=3, ejecutadas=1, dns_count=1)
    handler = FinalizarCompetenciaManualHandler(store, estado)

    with pytest.raises(CompetenciaNoFinalizable, match="1 performance"):
        await handler.handle(
            FinalizarCompetenciaManualCommand(
                competencia_id=competencia_id,
                disciplina=Disciplina.STA,
                solicitado_por="org@ataraxia.com",
            )
        )

    store.append.assert_not_called()


@pytest.mark.asyncio
async def test_finalizar_manual_finalizada_es_noop() -> None:
    competencia_id = uuid4()
    store = AsyncMock()
    store.load.return_value = _competencia_finalizada_events(competencia_id)
    estado = AsyncMock()
    handler = FinalizarCompetenciaManualHandler(store, estado)

    await handler.handle(
        FinalizarCompetenciaManualCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
            solicitado_por="org@ataraxia.com",
        )
    )

    estado.get_estado.assert_not_called()
    store.append.assert_not_called()
