"""Step definitions BDD — US-3.2.1: BC Identidad JWT."""

from __future__ import annotations

import os
import tempfile
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../US-3.2.1-bc-identidad-jwt.feature")


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "identidad_test.db")
    monkeypatch.setenv("IDENTIDAD_DB_PATH", db_path)
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-bdd-32-chars-minimum!!")
    return {}


@pytest.fixture
def client(context: dict[str, Any]) -> TestClient:
    import importlib
    import app as app_module

    importlib.reload(app_module)
    from app import app as fastapi_app

    return TestClient(fastapi_app)


# ── Background ────────────────────────────────────────────────────────────────


@given("el sistema de identidad está inicializado")
def sistema_inicializado(context: dict[str, Any]) -> None:
    pass  # fixtures garantizan DB nueva + JWT secret


# ── Given helpers ─────────────────────────────────────────────────────────────


@given(parsers.parse('un email "{email}" no registrado'))
def email_no_registrado(context: dict[str, Any], email: str) -> None:
    context["email"] = email


@given(parsers.parse('un usuario registrado con email "{email}"'))
def usuario_ya_registrado(client: TestClient, context: dict[str, Any], email: str) -> None:
    client.post(
        "/auth/registro",
        json={
            "email": email,
            "nombre": "Test",
            "apellido": "User",
            "password": "Password1A",
            "roles": ["ATLETA"],
        },
    )
    context["email"] = email


@given(
    parsers.parse('un usuario registrado con email "{email}" y password "{password}" y rol "{rol}"')
)
def usuario_registrado_con_rol(
    client: TestClient, context: dict[str, Any], email: str, password: str, rol: str
) -> None:
    resp = client.post(
        "/auth/registro",
        json={
            "email": email,
            "nombre": "Test",
            "apellido": "User",
            "password": password,
            "roles": [rol],
        },
    )
    assert resp.status_code == 201
    context["email"] = email
    context["password"] = password
    context["rol"] = rol


@given("un access_token obtenido con esas credenciales")
def access_token_obtenido(client: TestClient, context: dict[str, Any]) -> None:
    resp = client.post(
        "/auth/login",
        json={"email": context["email"], "password": context["password"]},
    )
    assert resp.status_code == 200
    context["access_token"] = resp.json()["access_token"]


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('POST /auth/registro con email "{email}", password "{password}", rol "{rol}"'))
def post_registro(
    client: TestClient, context: dict[str, Any], email: str, password: str, rol: str
) -> None:
    context["response"] = client.post(
        "/auth/registro",
        json={
            "email": email,
            "nombre": "Test",
            "apellido": "User",
            "password": password,
            "roles": [rol],
        },
    )


@when(parsers.parse('POST /auth/login con email "{email}" y password "{password}"'))
def post_login(client: TestClient, context: dict[str, Any], email: str, password: str) -> None:
    context["response"] = client.post("/auth/login", json={"email": email, "password": password})


@when("se verifica el token con get_current_user")
def verificar_token(context: dict[str, Any]) -> None:
    from identidad.infrastructure.jwt_service import JWTService

    svc = JWTService()
    context["payload"] = svc.verify(context["access_token"])


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status_code:d}"))
def respuesta_status(context: dict[str, Any], status_code: int) -> None:
    assert context["response"].status_code == status_code


@then(parsers.parse('la respuesta contiene un campo "{campo}"'))
def respuesta_contiene_campo(context: dict[str, Any], campo: str) -> None:
    assert campo in context["response"].json()
    context[campo] = context["response"].json()[campo]


@then(parsers.parse('el token contiene email "{email}" y rol "{rol}"'))
def token_contiene_email_y_rol(context: dict[str, Any], email: str, rol: str) -> None:
    from identidad.infrastructure.jwt_service import JWTService

    svc = JWTService()
    payload = svc.verify(context["access_token"])
    assert payload["email"] == email
    assert payload["rol"] == rol


@then('el payload contiene "sub", "email" y "rol"')
def payload_contiene_campos(context: dict[str, Any]) -> None:
    assert "sub" in context["payload"]
    assert "email" in context["payload"]
    assert "rol" in context["payload"]


@then(parsers.parse('el campo "{campo}" es "{valor}"'))
def campo_es_valor(context: dict[str, Any], campo: str, valor: str) -> None:
    assert context["payload"][campo] == valor
