from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router


@pytest.fixture
def app_client(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _payload(nombre: str = "Open Publico 2026") -> dict[str, object]:
    return {
        "nombre": nombre,
        "descripcion": "Torneo visible para el portal publico",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-06-03",
        "sede": {"nombre": "Piscina Municipal", "ciudad": "Buenos Aires", "pais": "Argentina"},
        "entidad_organizadora": {"nombre": "AIDA Argentina", "tipo": "FEDERACION"},
        "grupos_etarios": ["SENIOR"],
    }


def _organizador_override() -> dict[str, str]:
    return {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ORGANIZADOR",
    }


def _crear_torneo(client: TestClient, nombre: str) -> str:
    client.app.dependency_overrides[get_current_user] = _organizador_override
    response = client.post("/torneos", json=_payload(nombre))
    client.app.dependency_overrides.clear()
    assert response.status_code == 201
    return str(response.json()["torneo_id"])


def _cancelar_torneo(client: TestClient, torneo_id: str) -> None:
    client.app.dependency_overrides[get_current_user] = _organizador_override
    response = client.put(f"/torneos/{torneo_id}/cancelar")
    client.app.dependency_overrides.clear()
    assert response.status_code == 200


def _abrir_inscripcion(client: TestClient, torneo_id: str) -> None:
    client.app.dependency_overrides[get_current_user] = _organizador_override
    response = client.put(f"/torneos/{torneo_id}/abrir-inscripcion")
    client.app.dependency_overrides.clear()
    assert response.status_code == 200


def _torneo_fields(torneo: dict[str, Any]) -> set[str]:
    return {
        "torneo_id",
        "nombre",
        "descripcion",
        "fecha_inicio",
        "fecha_fin",
        "sede",
        "estado",
    }.intersection(torneo)


def test_get_torneos_es_publico_sin_authorization(app_client: TestClient) -> None:
    _crear_torneo(app_client, "Torneo sin token")

    response = app_client.get("/torneos")

    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 1


def test_get_torneos_excluye_cancelados(app_client: TestClient) -> None:
    visible_id = _crear_torneo(app_client, "Torneo visible")
    cancelado_id = _crear_torneo(app_client, "Torneo cancelado")
    _cancelar_torneo(app_client, cancelado_id)

    response = app_client.get("/torneos")

    assert response.status_code == 200
    ids = {torneo["torneo_id"] for torneo in response.json()}
    estados = {torneo["estado"] for torneo in response.json()}
    assert visible_id in ids
    assert cancelado_id not in ids
    assert "CANCELADO" not in estados


def test_get_torneos_incluye_campos_del_portal(app_client: TestClient) -> None:
    creado_id = _crear_torneo(app_client, "Torneo creado")
    abierto_id = _crear_torneo(app_client, "Torneo abierto")
    _abrir_inscripcion(app_client, abierto_id)

    response = app_client.get("/torneos")

    assert response.status_code == 200
    torneos = response.json()
    assert {torneo["torneo_id"] for torneo in torneos} == {creado_id, abierto_id}
    required = {"torneo_id", "nombre", "descripcion", "fecha_inicio", "fecha_fin", "sede", "estado"}
    for torneo in torneos:
        assert _torneo_fields(torneo) == required
        assert {"ciudad", "pais"}.issubset(torneo["sede"])


def test_get_torneos_con_auth_mantiene_contrato_publico(app_client: TestClient) -> None:
    _crear_torneo(app_client, "Torneo creado")
    abierto_id = _crear_torneo(app_client, "Torneo abierto")
    _abrir_inscripcion(app_client, abierto_id)

    public_response = app_client.get("/torneos")
    app_client.app.dependency_overrides[get_current_user] = _organizador_override
    auth_response = app_client.get("/torneos", headers={"Authorization": "Bearer fake-token"})
    app_client.app.dependency_overrides.clear()

    assert public_response.status_code == 200
    assert auth_response.status_code == 200
    assert public_response.json() == auth_response.json()
