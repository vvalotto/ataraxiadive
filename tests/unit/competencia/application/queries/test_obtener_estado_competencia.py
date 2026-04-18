"""Tests unitarios de ObtenerEstadoCompetenciaHandler."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.queries.obtener_estado_competencia import (
    ObtenerEstadoCompetenciaHandler,
    ObtenerEstadoCompetenciaQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina


def _event(event_type: str, payload: dict[str, object]) -> dict[str, object]:
    return {
        "event_type": event_type,
        "payload": payload,
        "version": 1,
        "occurred_at": datetime(2026, 4, 16, 10, 0, 0).isoformat(),
    }


@pytest.mark.asyncio
async def test_retorna_hash_sha256_si_la_competencia_finalizo() -> None:
    competencia_id = uuid4()
    hash_sha256 = "a" * 64
    store = AsyncMock()
    store.load.return_value = [
        _event(
            "IntervaloOTConfigurado",
            {
                "competencia_id": str(competencia_id),
                "disciplina": Disciplina.DNF.value,
                "intervalo_minutos": 7,
                "configurado_por": "org-1",
                "torneo_id": None,
            },
        ),
        _event(
            "CompetenciaFinalizada",
            {
                "competencia_id": str(competencia_id),
                "disciplina": Disciplina.DNF.value,
                "total_performances": 2,
                "ejecutadas": 2,
                "dns_count": 0,
                "finalizada_en": datetime(2026, 4, 16, 12, 0, 0).isoformat(),
                "hash_sha256": hash_sha256,
                "occurred_at": datetime(2026, 4, 16, 12, 0, 0).isoformat(),
            },
        ),
    ]
    handler = ObtenerEstadoCompetenciaHandler(store)

    dto = await handler.handle(
        ObtenerEstadoCompetenciaQuery(
            competencia_id=competencia_id,
            disciplina=Disciplina.DNF,
        )
    )

    assert dto.estado == "Finalizada"
    assert dto.intervalo_minutos == 7
    assert dto.hash_sha256 == hash_sha256


@pytest.mark.asyncio
async def test_retorna_hash_nulo_para_stream_historico_sin_campo() -> None:
    competencia_id = uuid4()
    store = AsyncMock()
    store.load.return_value = [
        _event(
            "CompetenciaFinalizada",
            {
                "competencia_id": str(competencia_id),
                "disciplina": Disciplina.STA.value,
                "total_performances": 0,
                "ejecutadas": 0,
                "dns_count": 0,
                "finalizada_en": datetime(2026, 4, 16, 12, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 4, 16, 12, 0, 0).isoformat(),
            },
        )
    ]
    handler = ObtenerEstadoCompetenciaHandler(store)

    dto = await handler.handle(
        ObtenerEstadoCompetenciaQuery(
            competencia_id=competencia_id,
            disciplina=Disciplina.STA,
        )
    )

    assert dto.estado == "Finalizada"
    assert dto.hash_sha256 is None
