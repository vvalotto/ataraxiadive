"""Tests unitarios de ExportarResultadosHandler — US-4.6.4."""

from __future__ import annotations

from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.domain.ports.competencias_por_torneo_port import CompetenciaPorTorneoRecord
from registro.domain.value_objects.categoria import Categoria
from resultados.application.queries.exportar_resultados import (
    ExportarResultadosHandler,
    ExportarResultadosQuery,
)
from resultados.domain.exceptions import TorneoNoEncontrado
from resultados.infrastructure.repositories.atleta_info_adapter import AtletaInfo


def _competencia_event(competencia_id, disciplina: str, hash_sha256: str | None = None) -> dict:
    payload = {
        "competencia_id": str(competencia_id),
        "disciplina": disciplina,
        "total_performances": 1,
        "ejecutadas": 1,
        "dns_count": 0,
        "finalizada_en": datetime(2026, 4, 16, 15, 0, 0).isoformat(),
        "occurred_at": datetime(2026, 4, 16, 15, 0, 0).isoformat(),
    }
    if hash_sha256 is not None:
        payload["hash_sha256"] = hash_sha256
    return {"event_type": "CompetenciaFinalizada", "payload": payload}


def _performance_stream(competencia_id, atleta_id, disciplina: str, ap: str, rp: str) -> list[dict]:
    return [
        {
            "event_type": "APRegistrado",
            "payload": {
                "competencia_id": str(competencia_id),
                "participante_id": str(atleta_id),
                "disciplina": disciplina,
                "valor_ap": ap,
                "unidad": "Metros",
            },
        },
        {
            "event_type": "ResultadoRegistrado",
            "payload": {
                "participante_id": str(atleta_id),
                "disciplina": disciplina,
                "valor_rp": rp,
                "unidad": "Metros",
            },
        },
        {
            "event_type": "TarjetaAsignada",
            "payload": {
                "participante_id": str(atleta_id),
                "disciplina": disciplina,
                "tipo": "Blanca",
                "penalizaciones": [],
                "rp_medido": rp,
            },
        },
    ]


@pytest.mark.asyncio
async def test_handle_torneo_inexistente_lanza_404_logico() -> None:
    ranking_store = AsyncMock()
    competencia_store = AsyncMock()
    competencias_por_torneo = AsyncMock()
    torneo_repo = AsyncMock()
    torneo_repo.find_by_id.return_value = None
    atleta_info = AsyncMock()

    handler = ExportarResultadosHandler(
        ranking_store=ranking_store,
        competencia_store=competencia_store,
        competencias_por_torneo=competencias_por_torneo,
        torneo_repo=torneo_repo,
        atleta_info_adapter=atleta_info,
    )

    with pytest.raises(TorneoNoEncontrado):
        await handler.handle(ExportarResultadosQuery(torneo_id=uuid4()))


@pytest.mark.asyncio
async def test_handle_incluye_hash_solo_para_disciplina_finalizada() -> None:
    torneo_id = uuid4()
    competencia_finalizada = uuid4()
    competencia_en_ejecucion = uuid4()
    atleta_a = uuid4()
    atleta_b = uuid4()
    ranking_store = AsyncMock()
    ranking_store.load.return_value = []
    competencia_store = AsyncMock()
    hash_sha = "a" * 64

    async def load_side_effect(stream_id: str):
        if stream_id == f"competencia-{competencia_finalizada}":
            return [_competencia_event(competencia_finalizada, "DNF", hash_sha)]
        if stream_id == f"competencia-{competencia_en_ejecucion}":
            return [
                {
                    "event_type": "CompetenciaIniciada",
                    "payload": {
                        "competencia_id": str(competencia_en_ejecucion),
                        "disciplina": "STA",
                        "juez_id": "j1",
                        "iniciada_en": datetime(2026, 4, 16, 12, 0, 0).isoformat(),
                        "occurred_at": datetime(2026, 4, 16, 12, 0, 0).isoformat(),
                    },
                }
            ]
        return []

    async def streams_side_effect(prefix: str):
        if prefix == f"performance-{competencia_finalizada}-":
            return [_performance_stream(competencia_finalizada, atleta_a, "DNF", "60", "58")]
        if prefix == f"performance-{competencia_en_ejecucion}-":
            return [_performance_stream(competencia_en_ejecucion, atleta_b, "STA", "300", "295")]
        return []

    competencia_store.load.side_effect = load_side_effect
    competencia_store.load_all_streams_with_prefix.side_effect = streams_side_effect

    competencias_por_torneo = AsyncMock()
    competencias_por_torneo.listar_por_torneo.return_value = [
        CompetenciaPorTorneoRecord(
            competencia_id=competencia_finalizada,
            disciplina="DNF",
            torneo_id=torneo_id,
        ),
        CompetenciaPorTorneoRecord(
            competencia_id=competencia_en_ejecucion,
            disciplina="STA",
            torneo_id=torneo_id,
        ),
    ]
    torneo_repo = AsyncMock()
    torneo_repo.find_by_id.return_value = SimpleNamespace(nombre="Open BA 2026")

    atleta_info = AsyncMock()

    async def atleta_info_side_effect(atleta_id):
        if atleta_id == atleta_a:
            return AtletaInfo(
                atleta_id=atleta_a,
                nombre_completo="Martin Garcia",
                categoria=Categoria.SENIOR_MASCULINO,
                club="Club Nautico",
            )
        return AtletaInfo(
            atleta_id=atleta_b,
            nombre_completo="Ana Flores",
            categoria=Categoria.SENIOR_FEMENINO,
            club="FAAS",
        )

    atleta_info.get_atleta_info.side_effect = atleta_info_side_effect

    handler = ExportarResultadosHandler(
        ranking_store=ranking_store,
        competencia_store=competencia_store,
        competencias_por_torneo=competencias_por_torneo,
        torneo_repo=torneo_repo,
        atleta_info_adapter=atleta_info,
    )

    result = await handler.handle(ExportarResultadosQuery(torneo_id=torneo_id))

    assert result.torneo_nombre == "Open BA 2026"
    assert len(result.disciplinas) == 2
    assert result.disciplinas[0].disciplina == "DNF"
    assert result.disciplinas[0].hash_sha256 == hash_sha
    assert result.disciplinas[0].ranking[0].atleta_nombre == "Martin Garcia"
    assert result.disciplinas[1].disciplina == "STA"
    assert result.disciplinas[1].estado == "EnEjecucion"
    assert result.disciplinas[1].hash_sha256 is None
    assert result.disciplinas[1].ranking[0].atleta_nombre == "Ana Flores"
