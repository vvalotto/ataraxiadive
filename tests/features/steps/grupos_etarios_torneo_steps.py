from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

from identidad.api.dependencies import get_current_user
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router

scenarios("../US-6.2.5-grupos-etarios-torneo.feature")


@pytest.fixture
def context(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    return {}


@pytest.fixture
def client(context: dict[str, Any]) -> Iterator[TestClient]:
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
        "nombre": "Copa Grupos BDD 2026",
        "descripcion": "Torneo BDD con grupos etarios",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-06-03",
        "sede": {"nombre": "Piscina", "ciudad": "BA", "pais": "AR"},
        "entidad_organizadora": {"nombre": "AIDA", "tipo": "FEDERACION"},
        "grupos_etarios": ["JUNIOR", "MASTER"],
    }
    payload.update(overrides)
    return payload


@given("la base de datos de torneos esta limpia para grupos etarios")
@given("la base de datos de torneos está limpia para grupos etarios")
def base_limpia(context: dict[str, Any]) -> None:
    pass


@given("un payload de torneo con grupos etarios JUNIOR y MASTER")
def payload_junior_master(context: dict[str, Any]) -> None:
    context["payload"] = _payload()


@given("un payload de torneo sin grupos_etarios")
def payload_sin_grupos(context: dict[str, Any]) -> None:
    payload = _payload()
    del payload["grupos_etarios"]
    context["payload"] = payload


@given("un payload de torneo con grupos_etarios vacio")
@given("un payload de torneo con grupos_etarios vacío")
def payload_grupos_vacio(context: dict[str, Any]) -> None:
    context["payload"] = _payload(grupos_etarios=[])


@given("un payload de torneo con grupo etario INVALIDO")
def payload_grupo_invalido(context: dict[str, Any]) -> None:
    context["payload"] = _payload(grupos_etarios=["INVALIDO"])


@when("POST /torneos con el payload de grupos etarios")
def post_torneos(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.post("/torneos", json=context["payload"])


@then("la respuesta de creacion es 201 con torneo_id")
@then("la respuesta de creación es 201 con torneo_id")
def respuesta_201(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 201
    context["torneo_id"] = context["response"].json()["torneo_id"]


@then("GET /torneos/{torneo_id} retorna grupos_etarios JUNIOR y MASTER")
def get_retorna_grupos(client: TestClient, context: dict[str, Any]) -> None:
    response = client.get(f"/torneos/{context['torneo_id']}")

    assert response.status_code == 200
    assert response.json()["grupos_etarios"] == ["JUNIOR", "MASTER"]


@then("la respuesta de grupos etarios es 422")
def respuesta_422(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 422
