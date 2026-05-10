from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app import build_ejecucion_post_action, build_ejecucion_precondition
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from identidad.api.dependencies import get_current_user
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import (
    configure_ejecucion_post_action,
    configure_ejecucion_precondition,
    router,
)


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
    configure_ejecucion_precondition(
        build_ejecucion_precondition(SQLiteEventStore(competencia_db), torneo_db, competencia_db)
    )
    configure_ejecucion_post_action(
        build_ejecucion_post_action(SQLiteEventStore(competencia_db), torneo_db, competencia_db)
    )
    yield TestClient(app)
    configure_ejecucion_precondition(None)
    configure_ejecucion_post_action(None)
    app.dependency_overrides.clear()


def _crear_torneo_en_preparacion(client: TestClient) -> UUID:
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

    assert (
        client.put(f"/torneos/{torneo_id}/disciplinas", json={"disciplinas": ["STA"]}).status_code
        == 200
    )
    assert client.put(f"/torneos/{torneo_id}/abrir-inscripcion").status_code == 200
    assert client.put(f"/torneos/{torneo_id}/cerrar-inscripcion").status_code == 200
    return torneo_id


async def _registrar_competencia_preparada(
    competencia_db: str,
    torneo_id: UUID,
    *,
    with_juez: bool,
) -> None:
    competencia_id = uuid4()
    performance_id = uuid4()
    atleta_id = uuid4()
    now = datetime(2026, 6, 1, 9, 0, tzinfo=timezone.utc).isoformat()
    projection = SQLiteCompetenciasPorTorneo(competencia_db)
    store = SQLiteEventStore(competencia_db)
    await projection.guardar(
        competencia_id=competencia_id,
        disciplina="STA",
        torneo_id=torneo_id,
    )
    await store.append(
        f"competencia-{competencia_id}",
        "IntervaloOTConfigurado",
        {
            "competencia_id": str(competencia_id),
            "disciplina": "STA",
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
            "disciplina": "STA",
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
            "disciplina": "STA",
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
                "disciplina": "STA",
                "performance_id": str(performance_id),
                "juez_id": "juez-01",
                "asignado_en": now,
                "occurred_at": now,
            },
        )


@pytest.mark.asyncio
async def test_iniciar_ejecucion_retorna_409_si_faltan_jueces_asignados(
    client: TestClient,
) -> None:
    competencia_db = os.environ["COMPETENCIA_DB_PATH"]
    torneo_id = _crear_torneo_en_preparacion(client)
    await _registrar_competencia_preparada(competencia_db, torneo_id, with_juez=False)

    response = client.put(f"/torneos/{torneo_id}/iniciar-ejecucion")

    assert response.status_code == 409
    assert "STA" in response.json()["detail"]
    assert "faltan jueces" in response.json()["detail"]


@pytest.mark.asyncio
async def test_iniciar_ejecucion_permite_si_toda_la_grilla_tiene_juez(
    client: TestClient,
) -> None:
    competencia_db = os.environ["COMPETENCIA_DB_PATH"]
    torneo_id = _crear_torneo_en_preparacion(client)
    await _registrar_competencia_preparada(competencia_db, torneo_id, with_juez=True)

    response = client.put(f"/torneos/{torneo_id}/iniciar-ejecucion")

    assert response.status_code == 200
    competencias = await SQLiteCompetenciasPorTorneo(competencia_db).listar_por_torneo(torneo_id)
    assert len(competencias) == 1
    events = await SQLiteEventStore(competencia_db).load(
        f"competencia-{competencias[0].competencia_id}"
    )
    assert any(event["event_type"] == "CompetenciaIniciada" for event in events)
