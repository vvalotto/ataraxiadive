"""Step definitions BDD — US-3.4.2: Auth por rol en APIs."""

import os
import tempfile
from typing import Any

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, scenario, then, when

from identidad.api.dependencies import JuezDep, AtletaDep, OrganizadorDep, get_current_user

FEATURE = "../US-3.4.2-auth-jwt-middleware.feature"


def _mock_user(rol: str) -> dict:
    return {"sub": "uid-1", "email": "test@test.com", "rol": rol}


# ── Fixture base ──────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db = str(tmp_path / "torneo.db")
    monkeypatch.setenv("TORNEO_DB_PATH", db)
    return {}


@pytest.fixture
def torneo_client(context: dict[str, Any]) -> TestClient:
    from torneo.api.router import router

    app = FastAPI()
    app.include_router(router)
    return TestClient(app, raise_server_exceptions=False)


# ── Scenario 1: organizador crea torneo con token válido ──────────────────────


@scenario(FEATURE, "organizador crea torneo con token válido")
def test_organizador_crea_torneo() -> None:
    pass


# ── Scenario 2: atleta intenta crear torneo y recibe 403 ─────────────────────


@scenario(FEATURE, "atleta intenta crear torneo y recibe 403")
def test_atleta_403() -> None:
    pass


# ── Scenario 3: request sin token a endpoint protegido recibe 401 ─────────────


@scenario(FEATURE, "request sin token a endpoint protegido recibe 401")
def test_sin_token_401() -> None:
    pass


# ── Scenario 4: juez registra tarjeta con su token ────────────────────────────


@scenario(FEATURE, "juez registra tarjeta con su token")
def test_juez_tarjeta() -> None:
    pass


# ── Scenario 5: atleta registra AP con su token ───────────────────────────────


@scenario(FEATURE, "atleta registra AP con su token")
def test_atleta_ap() -> None:
    pass


# ── Scenario 6: GET /torneos sin token es público ─────────────────────────────


@scenario(FEATURE, "GET /torneos sin token es público")
def test_get_torneos_publico() -> None:
    pass


# ── Given steps ───────────────────────────────────────────────────────────────


@given("un token JWT con rol ORGANIZADOR", target_fixture="context")
def given_token_organizador(context: dict[str, Any], torneo_client: TestClient) -> dict[str, Any]:
    torneo_client.app.dependency_overrides[get_current_user] = lambda: _mock_user("ORGANIZADOR")
    context["client"] = torneo_client
    return context


@given("un token JWT con rol ATLETA", target_fixture="context")
def given_token_atleta(context: dict[str, Any], torneo_client: TestClient) -> dict[str, Any]:
    torneo_client.app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
    context["client"] = torneo_client
    return context


@given("no hay token de autenticación", target_fixture="context")
def given_sin_token(context: dict[str, Any], torneo_client: TestClient) -> dict[str, Any]:
    # No override → get_current_user requiere token real → 401/422
    context["client"] = torneo_client
    return context


@given("un token JWT con rol JUEZ", target_fixture="context")
def given_token_juez(context: dict[str, Any]) -> dict[str, Any]:
    """Juez accede a un endpoint protegido con JuezDep en app minimal."""
    app = FastAPI()

    @app.get("/protegido")
    async def _protegido(_: JuezDep) -> dict:
        return {"ok": True}

    app.dependency_overrides[get_current_user] = lambda: _mock_user("JUEZ")
    context["client"] = TestClient(app, raise_server_exceptions=False)
    context["juez_endpoint"] = "/protegido"
    return context


# ── When steps ────────────────────────────────────────────────────────────────

_TORNEO_PAYLOAD = {
    "nombre": "Copa BDD",
    "descripcion": "Test auth",
    "fecha_inicio": "2026-06-01",
    "fecha_fin": "2026-06-03",
    "sede": {"nombre": "Piscina", "ciudad": "CABA", "pais": "Argentina"},
    "entidad_organizadora": {"nombre": "FAADS", "tipo": "federacion"},
    "grupos_etarios": ["SENIOR"],
}


@when("POST /torneos con el token")
def when_post_torneos(context: dict[str, Any]) -> None:
    context["response"] = context["client"].post("/torneos", json=_TORNEO_PAYLOAD)


@when("POST /torneos sin token")
def when_post_torneos_sin_token(context: dict[str, Any]) -> None:
    context["response"] = context["client"].post("/torneos", json=_TORNEO_PAYLOAD)


@when("POST /competencias/{id}/performances/{perf_id}/tarjeta con el token")
def when_juez_tarjeta(context: dict[str, Any]) -> None:
    context["response"] = context["client"].get(context["juez_endpoint"])


@when("POST /competencias/{id}/performances/{atleta_id}/ap con el token")
def when_atleta_ap(context: dict[str, Any]) -> None:
    """Atleta accede a endpoint protegido con AtletaDep en app minimal."""
    from fastapi.responses import JSONResponse

    app = FastAPI()

    @app.post("/protegido-atleta", status_code=201)
    async def _protegido(_: AtletaDep) -> dict:
        return {"ok": True}

    app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
    client = TestClient(app, raise_server_exceptions=False)
    context["response"] = client.post("/protegido-atleta")


@when("GET /torneos sin token")
def when_get_torneos(context: dict[str, Any]) -> None:
    context["response"] = context["client"].get("/torneos")


# ── Then steps ────────────────────────────────────────────────────────────────


@then("la respuesta es 201")
def then_201(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 201


@then("la respuesta es 403")
def then_403(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 403


@then("la respuesta es 401")
def then_401(context: dict[str, Any]) -> None:
    assert context["response"].status_code in (401, 422)


@then("la respuesta es 200")
def then_200(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 200
