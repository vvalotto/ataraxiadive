from __future__ import annotations

from collections.abc import Iterator

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router


@pytest.fixture
def client(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ORGANIZADOR",
    }
    yield TestClient(app)
    app.dependency_overrides.clear()


def _payload(**overrides: object) -> dict[str, object]:
    payload: dict[str, object] = {
        "nombre": "Copa Grupos 2026",
        "descripcion": "Torneo con grupos etarios",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-06-03",
        "sede": {"nombre": "Piscina", "ciudad": "BA", "pais": "AR"},
        "entidad_organizadora": {"nombre": "AIDA", "tipo": "FEDERACION"},
        "grupos_etarios": ["JUNIOR", "MASTER"],
    }
    payload.update(overrides)
    return payload


def test_crear_torneo_persiste_grupos_etarios(client: TestClient) -> None:
    response = client.post("/torneos", json=_payload())

    assert response.status_code == 201
    torneo_id = response.json()["torneo_id"]

    get_response = client.get(f"/torneos/{torneo_id}")

    assert get_response.status_code == 200
    assert get_response.json()["grupos_etarios"] == ["JUNIOR", "MASTER"]


def test_crear_torneo_sin_grupos_etarios_retorna_422(client: TestClient) -> None:
    payload = _payload()
    del payload["grupos_etarios"]

    response = client.post("/torneos", json=payload)

    assert response.status_code == 422


def test_crear_torneo_con_grupos_etarios_vacio_retorna_422(client: TestClient) -> None:
    response = client.post("/torneos", json=_payload(grupos_etarios=[]))

    assert response.status_code == 422


def test_crear_torneo_con_grupo_etario_invalido_retorna_422(client: TestClient) -> None:
    response = client.post("/torneos", json=_payload(grupos_etarios=["INVALIDO"]))

    assert response.status_code == 422
