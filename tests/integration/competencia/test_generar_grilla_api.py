"""Tests de integración API — POST /competencia/{id}/generar-grilla."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from app import app
from competencia.api.router import get_event_store
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from identidad.api.dependencies import get_current_user

CREATE_EVENTS_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL
            DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""


@pytest.fixture
async def store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    db_path = str(tmp_path / "competencia_generar_grilla_api.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def client(store: SQLiteEventStore) -> TestClient:
    app.dependency_overrides[get_event_store] = lambda: store
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "organizador-01",
        "email": "org@ataraxia.com",
        "rol": "ORGANIZADOR",
    }
    yield TestClient(app)
    app.dependency_overrides.clear()


async def _seed_competencia_con_ap(store: SQLiteEventStore, competencia_id: UUID) -> None:
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=Disciplina.DNF,
            intervalo_minutos=8,
            configurado_por="organizador-01",
        )
    )
    handler = RegistrarAPHandler(
        store,
        StubCompetenciaEstadoAdapter(),
        DisciplinaDescriptorAdapter(),
    )
    for valor in ("50", "60", "70"):
        await handler.handle(
            RegistrarAPCommand(
                competencia_id=competencia_id,
                participante_id=uuid4(),
                disciplina=Disciplina.DNF,
                valor_ap=Decimal(valor),
                unidad=UnidadMedida.Metros,
            )
        )


@pytest.mark.asyncio
async def test_post_generar_grilla_expone_ot_calculados(
    store: SQLiteEventStore,
    client: TestClient,
) -> None:
    competencia_id = uuid4()
    await _seed_competencia_con_ap(store, competencia_id)

    response = client.post(
        f"/competencia/{competencia_id}/generar-grilla",
        json={
            "disciplina": "DNF",
            "ot_inicio": "2026-04-20T09:00:00Z",
            "andariveles": 1,
        },
    )
    grilla_response = client.get(f"/competencia/{competencia_id}/grilla?disciplina=DNF")

    assert response.status_code == 204
    assert grilla_response.status_code == 200
    grilla = grilla_response.json()
    assert len(grilla) == 3
    assert grilla[0]["ot_programado"].startswith("2026-04-20T09:00:00")
    assert grilla[1]["ot_programado"].startswith("2026-04-20T09:08:00")
    assert grilla[2]["ot_programado"].startswith("2026-04-20T09:16:00")
