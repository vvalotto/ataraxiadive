"""Step definitions BDD — US-6.6.1: endpoint publico de torneos."""

from __future__ import annotations

import sys
from collections.abc import Iterator
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from identidad.api.dependencies import get_current_user
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router  # noqa: F401 — side-effect: loads module into sys.modules

_torneo_router_mod = sys.modules["torneo.api.router"]

scenarios("../US-6.6.1-endpoint-publico-torneos.feature")


@pytest.fixture
def context(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    monkeypatch.setattr(_torneo_router_mod, "_cierre_inscripcion_precondition", None)
    monkeypatch.setattr(_torneo_router_mod, "_ejecucion_precondition", None)
    monkeypatch.setattr(_torneo_router_mod, "_ejecucion_post_action", None)
    return {"created_ids": {}}


@pytest.fixture
def client(context: dict[str, Any]) -> Iterator[TestClient]:
    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    yield TestClient(app)
    app.dependency_overrides.clear()


def _organizador_override() -> dict[str, str]:
    return {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ORGANIZADOR",
    }


def _payload(nombre: str) -> dict[str, object]:
    return {
        "nombre": nombre,
        "descripcion": "Torneo para portal publico",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-06-03",
        "sede": {"nombre": "Piscina Municipal", "ciudad": "Buenos Aires", "pais": "Argentina"},
        "entidad_organizadora": {"nombre": "AIDA Argentina", "tipo": "FEDERACION"},
        "grupos_etarios": ["SENIOR"],
    }


def _with_organizador(client: TestClient) -> None:
    client.app.dependency_overrides[get_current_user] = _organizador_override


def _clear_auth(client: TestClient) -> None:
    client.app.dependency_overrides.clear()


def _crear_torneo(client: TestClient, context: dict[str, Any], estado: str) -> str:
    nombre = f"Torneo {estado} {len(context['created_ids']) + 1}"
    _with_organizador(client)
    response = client.post("/torneos", json=_payload(nombre))
    assert response.status_code == 201
    torneo_id = str(response.json()["torneo_id"])

    if estado == "INSCRIPCION_ABIERTA":
        assert client.put(f"/torneos/{torneo_id}/abrir-inscripcion").status_code == 200
    elif estado == "EJECUCION":
        assert client.put(f"/torneos/{torneo_id}/abrir-inscripcion").status_code == 200
        assert client.put(f"/torneos/{torneo_id}/cerrar-inscripcion").status_code == 200
        assert client.put(f"/torneos/{torneo_id}/iniciar-ejecucion").status_code == 200
    elif estado == "CANCELADO":
        assert client.put(f"/torneos/{torneo_id}/cancelar").status_code == 200
    elif estado != "CREADO":
        raise AssertionError(f"Estado no soportado por el escenario: {estado}")

    _clear_auth(client)
    context["created_ids"].setdefault(estado, []).append(torneo_id)
    return torneo_id


def _parse_estados(estados: str) -> list[str]:
    normalizados = estados.replace(" e ", ", ").replace(" y ", ", ")
    return [item.strip() for item in normalizados.split(",") if item.strip()]


@given("la base de datos de torneos publicos esta limpia")
def base_limpia(context: dict[str, Any]) -> None:
    context["created_ids"] = {}


@given(parsers.parse("existe un torneo publico con estado {estado}"))
def existe_torneo_estado(client: TestClient, context: dict[str, Any], estado: str) -> None:
    _crear_torneo(client, context, estado)


@given(parsers.parse("existen torneos publicos con estados {estados}"))
def existen_torneos_estados(client: TestClient, context: dict[str, Any], estados: str) -> None:
    for estado in _parse_estados(estados):
        _crear_torneo(client, context, estado)


@when("un visitante hace GET /torneos sin Authorization header")
def visitante_get_torneos(client: TestClient, context: dict[str, Any]) -> None:
    _clear_auth(client)
    context["public_response"] = client.get("/torneos")


@when("un organizador autenticado hace GET /torneos")
def organizador_get_torneos(client: TestClient, context: dict[str, Any]) -> None:
    _with_organizador(client)
    context["auth_response"] = client.get("/torneos", headers={"Authorization": "Bearer fake"})
    _clear_auth(client)


@then("la respuesta publica de torneos es 200 OK")
def respuesta_publica_200(context: dict[str, Any]) -> None:
    assert context["public_response"].status_code == 200


@then("el body es una lista de torneos")
def body_lista(context: dict[str, Any]) -> None:
    assert isinstance(context["public_response"].json(), list)


@then("la lista publica no contiene torneos con estado CANCELADO")
def lista_sin_cancelados(context: dict[str, Any]) -> None:
    torneos = context["public_response"].json()
    ids = {torneo["torneo_id"] for torneo in torneos}
    cancelados = set(context["created_ids"].get("CANCELADO", []))
    assert cancelados.isdisjoint(ids)
    assert all(torneo["estado"] != "CANCELADO" for torneo in torneos)


@then(
    "cada torneo publico incluye torneo_id, nombre, descripcion, fecha_inicio, "
    "fecha_fin, sede y estado"
)
def contrato_portal(context: dict[str, Any]) -> None:
    required = {"torneo_id", "nombre", "descripcion", "fecha_inicio", "fecha_fin", "sede", "estado"}
    for torneo in context["public_response"].json():
        assert required.issubset(torneo)
        assert {"ciudad", "pais"}.issubset(torneo["sede"])


@then("ambas respuestas publicas tienen status 200")
def ambas_200(context: dict[str, Any]) -> None:
    assert context["public_response"].status_code == 200
    assert context["auth_response"].status_code == 200


@then("ambas respuestas publicas tienen el mismo contrato de torneo")
def mismo_contrato(context: dict[str, Any]) -> None:
    assert context["public_response"].json() == context["auth_response"].json()
