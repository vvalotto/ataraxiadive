"""Tests de integración — API disciplinas + jueces Torneo [US-3.4.1]"""

from __future__ import annotations

import tempfile
from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


def _repo_con_torneo() -> tuple[SQLiteTorneoRepository, Torneo]:
    import asyncio

    db = tempfile.mktemp(suffix=".db")
    repo = SQLiteTorneoRepository(db_path=db)
    torneo = Torneo(
        nombre="Copa Integración",
        descripcion="Test",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina", "CABA", "Argentina"),
        entidad_organizadora=EntidadOrganizadora("FAADS", "federacion"),
    )
    asyncio.get_event_loop().run_until_complete(repo.save(torneo))
    return repo, torneo


@pytest.fixture
def client_con_torneo() -> tuple[TestClient, Torneo]:
    import os
    from fastapi import FastAPI
    from torneo.api.router import router

    db = tempfile.mktemp(suffix=".db")
    os.environ["TORNEO_DB_PATH"] = db

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    # Crear torneo vía API
    resp = client.post(
        "/torneos",
        json={
            "nombre": "Copa Test",
            "descripcion": "Torneo de prueba",
            "fecha_inicio": "2026-06-01",
            "fecha_fin": "2026-06-03",
            "sede": {"nombre": "Piscina", "ciudad": "CABA", "pais": "Argentina"},
            "entidad_organizadora": {"nombre": "FAADS", "tipo": "federacion"},
        },
    )
    assert resp.status_code == 201
    torneo_id = resp.json()["torneo_id"]

    from torneo.domain.aggregates.torneo import Torneo as T

    t = T.__new__(T)
    t.torneo_id = __import__("uuid").UUID(torneo_id)  # type: ignore[attr-defined]
    return client, t


@pytest.fixture
def app_client(tmp_path: object) -> TestClient:
    import os
    from fastapi import FastAPI
    from torneo.api.router import router
    from identidad.api.dependencies import get_current_user

    db = tempfile.mktemp(suffix=".db")
    os.environ["TORNEO_DB_PATH"] = db
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ORGANIZADOR",
    }
    yield TestClient(app)
    app.dependency_overrides.clear()


def _crear_torneo(client: TestClient) -> str:
    resp = client.post(
        "/torneos",
        json={
            "nombre": "Copa Test",
            "descripcion": "Test",
            "fecha_inicio": "2026-06-01",
            "fecha_fin": "2026-06-03",
            "sede": {"nombre": "Piscina", "ciudad": "CABA", "pais": "Argentina"},
            "entidad_organizadora": {"nombre": "FAADS", "tipo": "federacion"},
        },
    )
    assert resp.status_code == 201
    return resp.json()["torneo_id"]


class TestAsignarDisciplinasAPI:
    def test_put_disciplinas_200(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        resp = app_client.put(
            f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA", "DNF", "DYNB"]}
        )
        assert resp.status_code == 200

    def test_get_disciplinas_retorna_lista(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA", "DNF"]})
        resp = app_client.get(f"/torneos/{tid}/disciplinas")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert all(d["juez_id"] is None for d in data)

    def test_put_disciplinas_invalidas_422(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        resp = app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["INVALIDA"]})
        assert resp.status_code == 422

    def test_disciplinas_persisten_en_repo(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA"]})
        # Re-fetch via GET
        resp = app_client.get(f"/torneos/{tid}/disciplinas")
        disciplinas = [d["disciplina"] for d in resp.json()]
        assert "STA" in disciplinas


class TestAsignarJuezAPI:
    def test_put_juez_200(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA"]})
        juez_id = str(uuid4())
        resp = app_client.put(
            f"/torneos/{tid}/disciplinas/STA/juez",
            json={"juez_id": juez_id},
        )
        assert resp.status_code == 200
        assert resp.json()["juez_id"] == juez_id

    def test_asignar_juez_disciplina_no_en_torneo_409(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA"]})
        resp = app_client.put(
            f"/torneos/{tid}/disciplinas/DYN/juez",
            json={"juez_id": str(uuid4())},
        )
        assert resp.status_code == 409

    def test_reasignar_juez_permitido(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA"]})
        juez1, juez2 = str(uuid4()), str(uuid4())
        app_client.put(f"/torneos/{tid}/disciplinas/STA/juez", json={"juez_id": juez1})
        resp = app_client.put(f"/torneos/{tid}/disciplinas/STA/juez", json={"juez_id": juez2})
        assert resp.status_code == 200

    def test_juez_persiste_tras_asignacion(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA"]})
        juez_id = str(uuid4())
        app_client.put(f"/torneos/{tid}/disciplinas/STA/juez", json={"juez_id": juez_id})
        resp = app_client.get(f"/torneos/{tid}/disciplinas")
        sta = next(d for d in resp.json() if d["disciplina"] == "STA")
        assert sta["juez_id"] == juez_id


class TestDisciplinasDeJuezAPI:
    def test_get_disciplinas_juez(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA", "DNF", "DYNB"]})
        juez_id = str(uuid4())
        app_client.put(f"/torneos/{tid}/disciplinas/STA/juez", json={"juez_id": juez_id})
        app_client.put(f"/torneos/{tid}/disciplinas/DNF/juez", json={"juez_id": juez_id})
        resp = app_client.get(f"/torneos/{tid}/jueces/{juez_id}/disciplinas")
        assert resp.status_code == 200
        assert set(resp.json()) == {"STA", "DNF"}

    def test_juez_sin_disciplinas_retorna_lista_vacia(self, app_client: TestClient) -> None:
        tid = _crear_torneo(app_client)
        app_client.put(f"/torneos/{tid}/disciplinas", json={"disciplinas": ["STA"]})
        resp = app_client.get(f"/torneos/{tid}/jueces/{uuid4()}/disciplinas")
        assert resp.status_code == 200
        assert resp.json() == []
