"""Step definitions BDD — US-ADJ-11.1: BC Identidad multi-rol."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../US-ADJ-11.1-identidad-multi-rol.feature")


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "identidad_adj11_test.db")
    monkeypatch.setenv("IDENTIDAD_DB_PATH", db_path)
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-adj11-32-chars-min!!")
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
def sistema_inicializado_adj11(context: dict[str, Any]) -> None:
    pass  # fixtures garantizan DB nueva + JWT secret


# ── Given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('no existe ningún usuario con email "{email}"'))
def no_existe_usuario(context: dict[str, Any], email: str) -> None:
    context["email"] = email


@given(
    parsers.parse(
        'existe un usuario con email "{email}" password "{password}" y roles "{roles_str}"'
    )
)
def existe_usuario_con_roles(
    client: TestClient, context: dict[str, Any], email: str, password: str, roles_str: str
) -> None:
    roles = [r.strip() for r in roles_str.split(",")]
    resp = client.post(
        "/auth/registro",
        json={
            "email": email,
            "nombre": "Test",
            "apellido": "User",
            "password": password,
            "roles": roles,
        },
    )
    assert resp.status_code in (200, 201), f"Setup falló: {resp.status_code} {resp.text}"
    context["email"] = email
    context["password"] = password
    context["roles_str"] = roles_str


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('se registra con email "{email}" password "{password}" y roles "{roles_str}"'))
def registrar_con_roles(
    client: TestClient, context: dict[str, Any], email: str, password: str, roles_str: str
) -> None:
    roles = [r.strip() for r in roles_str.split(",")]
    context["response"] = client.post(
        "/auth/registro",
        json={
            "email": email,
            "nombre": "Test",
            "apellido": "User",
            "password": password,
            "roles": roles,
        },
    )


@when(parsers.parse('hace login con email "{email}" password "{password}" sin rol_elegido'))
def login_sin_rol_elegido(
    client: TestClient, context: dict[str, Any], email: str, password: str
) -> None:
    context["response"] = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


@when(parsers.parse('hace login con email "{email}" password "{password}" y rol_elegido "{rol}"'))
def login_con_rol_elegido(
    client: TestClient, context: dict[str, Any], email: str, password: str, rol: str
) -> None:
    context["response"] = client.post(
        "/auth/login",
        json={"email": email, "password": password, "rol_elegido": rol},
    )


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status_code:d}"))
def respuesta_status(context: dict[str, Any], status_code: int) -> None:
    assert (
        context["response"].status_code == status_code
    ), f"Esperaba {status_code}, got {context['response'].status_code}: {context['response'].text}"


@then(parsers.parse('la respuesta contiene campo "{campo}"'))
def respuesta_contiene_campo(context: dict[str, Any], campo: str) -> None:
    body = context["response"].json()
    assert campo in body, f"Campo '{campo}' no encontrado en: {body}"
    context[campo] = body[campo]


@then(parsers.parse('la respuesta no contiene campo "{campo}"'))
def respuesta_no_contiene_campo(context: dict[str, Any], campo: str) -> None:
    body = context["response"].json()
    assert campo not in body, f"Campo '{campo}' encontrado (no esperado) en: {body}"


@then(parsers.parse('el token del registro contiene rol "{rol}"'))
def token_registro_contiene_rol(context: dict[str, Any], rol: str) -> None:
    from identidad.infrastructure.jwt_service import JWTService

    svc = JWTService()
    token = context["response"].json().get("access_token")
    assert token, "No hay access_token en la respuesta de registro"
    payload = svc.verify(token)
    assert payload["rol"] == rol, f"Esperaba rol '{rol}', got '{payload['rol']}'"


@then(parsers.parse('el token del login contiene rol "{rol}"'))
def token_login_contiene_rol(context: dict[str, Any], rol: str) -> None:
    from identidad.infrastructure.jwt_service import JWTService

    svc = JWTService()
    token = context["response"].json().get("access_token")
    assert token, "No hay access_token en la respuesta de login"
    payload = svc.verify(token)
    assert payload["rol"] == rol, f"Esperaba rol '{rol}', got '{payload['rol']}'"
