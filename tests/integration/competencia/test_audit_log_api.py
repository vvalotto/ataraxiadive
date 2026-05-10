"""Tests de integración - API audit log de performance."""

from __future__ import annotations

from uuid import uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from app import app
from competencia.api.router import get_event_store, get_obtener_audit_log_handler
from competencia.application.queries.obtener_audit_log import ObtenerAuditLogHandler
from tests.integration.competencia._stubs import StubAtletaNombrePort
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
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
    db_path = str(tmp_path / "competencia_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def client(store: SQLiteEventStore) -> TestClient:
    stub_nombre = StubAtletaNombrePort()
    app.dependency_overrides[get_event_store] = lambda: store
    app.dependency_overrides[get_obtener_audit_log_handler] = lambda: ObtenerAuditLogHandler(
        store, stub_nombre
    )
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "org-001",
        "email": "organizador@test.com",
        "rol": "ORGANIZADOR",
    }
    yield TestClient(app)
    app.dependency_overrides.clear()


async def _append_audit_events(
    store: SQLiteEventStore,
    competencia_id,
    atleta_id,
    disciplina: str = "DNF",
) -> None:
    stream_id = f"performance-{competencia_id}-{atleta_id}-{disciplina}"
    await store.append(
        stream_id=stream_id,
        event_type="PerformanceRegistrada",
        payload={"ap": 60.0},
    )
    await store.append(
        stream_id=stream_id,
        event_type="ResultadoRegistrado",
        payload={"rp": 58.0},
    )
    await store.append(
        stream_id=stream_id,
        event_type="TarjetaAsignada",
        payload={"tarjeta": "Blanca", "penalizaciones": 0},
    )


async def _append_correccion(
    store: SQLiteEventStore,
    competencia_id,
    atleta_id,
    disciplina: str = "DNF",
) -> None:
    stream_id = f"performance-{competencia_id}-{atleta_id}-{disciplina}"
    await store.append(
        stream_id=stream_id,
        event_type="ResultadoCorregido",
        payload={"rp_anterior": 58.0, "rp_nuevo": 57.0, "motivo": "Medicion ajustada"},
    )


@pytest.mark.asyncio
async def test_get_audit_log_retorna_eventos_de_una_performance(
    store: SQLiteEventStore, client: TestClient
) -> None:
    competencia_id = uuid4()
    atleta_id = uuid4()
    await _append_audit_events(store, competencia_id, atleta_id)

    response = client.get(f"/competencia/{competencia_id}/performances/{atleta_id}/audit-log")

    assert response.status_code == 200
    assert response.json()["competencia_id"] == str(competencia_id)
    assert response.json()["atleta_id"] == str(atleta_id)
    assert response.json()["disciplina"] == "DNF"
    assert [evento["tipo"] for evento in response.json()["eventos"]] == [
        "PerformanceRegistrada",
        "ResultadoRegistrado",
        "TarjetaAsignada",
    ]


@pytest.mark.asyncio
async def test_get_audit_log_retorna_404_si_no_existe_performance(
    store: SQLiteEventStore, client: TestClient
) -> None:
    competencia_id = uuid4()
    atleta_id = uuid4()

    response = client.get(f"/competencia/{competencia_id}/performances/{atleta_id}/audit-log")

    assert response.status_code == 404
    assert response.json()["detail"] == (
        "No existe una performance para el atleta en la competencia indicada"
    )


@pytest.mark.asyncio
async def test_get_audit_log_incluye_correccion_historica(
    store: SQLiteEventStore, client: TestClient
) -> None:
    competencia_id = uuid4()
    atleta_id = uuid4()
    await _append_audit_events(store, competencia_id, atleta_id)
    await _append_correccion(store, competencia_id, atleta_id)

    response = client.get(f"/competencia/{competencia_id}/performances/{atleta_id}/audit-log")

    assert response.status_code == 200
    assert len(response.json()["eventos"]) == 4
    assert response.json()["eventos"][-1]["tipo"] == "ResultadoCorregido"
    assert response.json()["eventos"][-1]["datos"]["rp_nuevo"] == 57.0


@pytest.mark.asyncio
async def test_get_audit_log_retorna_403_para_rol_juez(
    store: SQLiteEventStore, client: TestClient
) -> None:
    competencia_id = uuid4()
    atleta_id = uuid4()
    await _append_audit_events(store, competencia_id, atleta_id)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "juez-001",
        "email": "juez@test.com",
        "rol": "JUEZ",
    }

    response = client.get(f"/competencia/{competencia_id}/performances/{atleta_id}/audit-log")

    assert response.status_code == 403
    assert response.json()["detail"] == "Rol insuficiente"
