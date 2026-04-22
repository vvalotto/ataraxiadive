from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from app import build_premiacion_precondition
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import PremiacionNoPermitida
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
    torneo.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF}))
    torneo.estado = EstadoTorneo.EJECUCION
    return torneo


@pytest.mark.asyncio
async def test_precondicion_rechaza_si_falta_competencia_configurada(
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    torneo_db = str(tmp_path / "torneo.db")
    competencia_db = str(tmp_path / "competencia.db")
    monkeypatch.setenv("COMPETENCIA_DB_PATH", competencia_db)
    torneo = _torneo()
    await SQLiteTorneoRepository(torneo_db).save(torneo)

    competencia_id = uuid4()
    await SQLiteCompetenciasPorTorneo(competencia_db).guardar(
        competencia_id=competencia_id,
        disciplina="DNF",
        torneo_id=torneo.torneo_id,
    )
    event_store = SQLiteEventStore(competencia_db)
    await event_store.append(
        f"competencia-{competencia_id}",
        "CompetenciaFinalizada",
        {"competencia_id": str(competencia_id), "disciplina": "DNF"},
    )

    precondition = build_premiacion_precondition(event_store, torneo_db)

    with pytest.raises(PremiacionNoPermitida) as exc_info:
        await precondition(torneo.torneo_id)

    assert "STA" in str(exc_info.value)


@pytest.mark.asyncio
async def test_precondicion_permite_si_todas_las_competencias_finalizaron(
    tmp_path: object,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    torneo_db = str(tmp_path / "torneo.db")
    competencia_db = str(tmp_path / "competencia.db")
    monkeypatch.setenv("COMPETENCIA_DB_PATH", competencia_db)
    torneo = _torneo()
    await SQLiteTorneoRepository(torneo_db).save(torneo)
    event_store = SQLiteEventStore(competencia_db)
    projection = SQLiteCompetenciasPorTorneo(competencia_db)

    for disciplina in ("DNF", "STA"):
        competencia_id = uuid4()
        await projection.guardar(
            competencia_id=competencia_id,
            disciplina=disciplina,
            torneo_id=torneo.torneo_id,
        )
        await event_store.append(
            f"competencia-{competencia_id}",
            "CompetenciaFinalizada",
            {"competencia_id": str(competencia_id), "disciplina": disciplina},
        )

    precondition = build_premiacion_precondition(event_store, torneo_db)

    await precondition(torneo.torneo_id)
