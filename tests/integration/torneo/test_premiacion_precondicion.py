from __future__ import annotations

import os
from collections.abc import Iterator
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import build_premiacion_precondition
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from identidad.api.dependencies import get_current_user
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import configure_premiacion_precondition, router


@pytest.fixture
def client(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    torneo_db = str(tmp_path / "torneo.db")
    competencia_db = str(tmp_path / "competencia.db")
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)
    monkeypatch.setenv("COMPETENCIA_DB_PATH", competencia_db)

    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ORGANIZADOR",
    }
    configure_premiacion_precondition(
        build_premiacion_precondition(SQLiteEventStore(competencia_db), torneo_db)
    )
    yield TestClient(app)
    configure_premiacion_precondition(None)
    app.dependency_overrides.clear()


def _crear_torneo_en_ejecucion(client: TestClient) -> UUID:
    response = client.post(
        "/torneos",
        json={
            "nombre": "BA 2026",
            "descripcion": "Torneo",
            "fecha_inicio": "2026-06-01",
            "fecha_fin": "2026-06-03",
            "sede": {"nombre": "Piscina", "ciudad": "BA", "pais": "AR"},
            "entidad_organizadora": {"nombre": "AIDA", "tipo": "FEDERACION"},
            "grupos_etarios": ["SENIOR"],
        },
    )
    assert response.status_code == 201
    torneo_id = UUID(response.json()["torneo_id"])

    disciplinas_response = client.put(
        f"/torneos/{torneo_id}/disciplinas",
        json={"disciplinas": ["DNF", "STA"]},
    )
    assert disciplinas_response.status_code == 200
    assert client.put(f"/torneos/{torneo_id}/abrir-inscripcion").status_code == 200
    assert client.put(f"/torneos/{torneo_id}/cerrar-inscripcion").status_code == 200
    assert client.put(f"/torneos/{torneo_id}/iniciar-ejecucion").status_code == 200
    return torneo_id


async def _registrar_competencia_finalizada(
    competencia_db: str,
    torneo_id: UUID,
    disciplina: str,
) -> None:
    competencia_id = uuid4()
    await SQLiteCompetenciasPorTorneo(competencia_db).guardar(
        competencia_id=competencia_id,
        disciplina=disciplina,
        torneo_id=torneo_id,
    )
    await SQLiteEventStore(competencia_db).append(
        f"competencia-{competencia_id}",
        "CompetenciaFinalizada",
        {"competencia_id": str(competencia_id), "disciplina": disciplina},
    )


@pytest.mark.asyncio
async def test_iniciar_premiacion_retorna_409_si_faltan_competencias(
    client: TestClient,
) -> None:
    torneo_id = _crear_torneo_en_ejecucion(client)

    response = client.put(f"/torneos/{torneo_id}/iniciar-premiacion")

    assert response.status_code == 409
    assert "DNF" in response.json()["detail"]
    assert "STA" in response.json()["detail"]


@pytest.mark.asyncio
async def test_iniciar_premiacion_permite_todas_las_competencias_finalizadas(
    client: TestClient,
) -> None:
    competencia_db = os.environ["COMPETENCIA_DB_PATH"]
    torneo_id = _crear_torneo_en_ejecucion(client)
    await _registrar_competencia_finalizada(competencia_db, torneo_id, "DNF")
    await _registrar_competencia_finalizada(competencia_db, torneo_id, "STA")

    response = client.put(f"/torneos/{torneo_id}/iniciar-premiacion")

    assert response.status_code == 200
