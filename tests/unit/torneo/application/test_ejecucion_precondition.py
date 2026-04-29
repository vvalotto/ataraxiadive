from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

import pytest

from app import build_ejecucion_precondition
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import EjecucionNoPermitida
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


def _torneo() -> Torneo:
    torneo = Torneo(
        nombre="BA 2026",
        descripcion="Torneo",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina", "BA", "AR"),
        entidad_organizadora=EntidadOrganizadora("AIDA", "FEDERACION"),
    )
    torneo.asignar_disciplinas(frozenset({Disciplina.STA}))
    torneo.estado = EstadoTorneo.PREPARACION
    return torneo


async def _registrar_competencia_confirmada(
    store: SQLiteEventStore,
    projection: SQLiteCompetenciasPorTorneo,
    torneo_id,
    *,
    disciplina: str = "STA",
    with_juez: bool,
) -> None:
    competencia_id = uuid4()
    performance_id = uuid4()
    atleta_id = uuid4()
    now = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc).isoformat()
    await projection.guardar(
        competencia_id=competencia_id,
        disciplina=disciplina,
        torneo_id=torneo_id,
    )
    await store.append(
        f"competencia-{competencia_id}",
        "IntervaloOTConfigurado",
        {
            "competencia_id": str(competencia_id),
            "disciplina": disciplina,
            "intervalo_minutos": 9,
            "configurado_por": "org-01",
            "torneo_id": str(torneo_id),
            "occurred_at": now,
        },
    )
    await store.append(
        f"competencia-{competencia_id}",
        "GrillaDeSalidaGenerada",
        {
            "competencia_id": str(competencia_id),
            "disciplina": disciplina,
            "ot_inicio": now,
            "generada_en": now,
            "occurred_at": now,
            "performances": [
                {
                    "performance_id": str(performance_id),
                    "atleta_id": str(atleta_id),
                    "posicion": 1,
                    "andarivel": 1,
                    "ot_programado": now,
                    "juez_id": None,
                }
            ],
        },
    )
    await store.append(
        f"competencia-{competencia_id}",
        "GrillaConfirmada",
        {
            "competencia_id": str(competencia_id),
            "disciplina": disciplina,
            "confirmada_en": now,
            "occurred_at": now,
        },
    )
    if with_juez:
        await store.append(
            f"competencia-{competencia_id}",
            "JuezPerformanceAsignado",
            {
                "competencia_id": str(competencia_id),
                "disciplina": disciplina,
                "performance_id": str(performance_id),
                "juez_id": "juez-01",
                "asignado_en": now,
                "occurred_at": now,
            },
        )


@pytest.mark.asyncio
async def test_precondicion_rechaza_si_faltan_jueces_por_performance(
    tmp_path: object,
) -> None:
    torneo_db = str(tmp_path / "torneo.db")
    competencia_db = str(tmp_path / "competencia.db")
    torneo = _torneo()
    await SQLiteTorneoRepository(torneo_db).save(torneo)
    store = SQLiteEventStore(competencia_db)
    projection = SQLiteCompetenciasPorTorneo(competencia_db)
    await _registrar_competencia_confirmada(
        store,
        projection,
        torneo.torneo_id,
        with_juez=False,
    )

    precondition = build_ejecucion_precondition(store, torneo_db, competencia_db)

    with pytest.raises(EjecucionNoPermitida) as exc_info:
        await precondition(torneo.torneo_id)

    assert "STA" in str(exc_info.value)
    assert "faltan jueces" in str(exc_info.value)


@pytest.mark.asyncio
async def test_precondicion_permite_si_grilla_confirmada_tiene_jueces(
    tmp_path: object,
) -> None:
    torneo_db = str(tmp_path / "torneo.db")
    competencia_db = str(tmp_path / "competencia.db")
    torneo = _torneo()
    await SQLiteTorneoRepository(torneo_db).save(torneo)
    store = SQLiteEventStore(competencia_db)
    projection = SQLiteCompetenciasPorTorneo(competencia_db)
    await _registrar_competencia_confirmada(
        store,
        projection,
        torneo.torneo_id,
        with_juez=True,
    )

    precondition = build_ejecucion_precondition(store, torneo_db, competencia_db)

    await precondition(torneo.torneo_id)
