"""Step definitions BDD — US-ADJ-11.2: Agregar/Quitar rol post-registro."""

from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../US-ADJ-11.2-agregar-quitar-rol.feature")


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "identidad_adj112_test.db")
    monkeypatch.setenv("IDENTIDAD_DB_PATH", db_path)
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-adj112-32chars-min!")
    return {}


@pytest.fixture
def client(context: dict[str, Any]) -> TestClient:
    import importlib
    import app as app_module

    importlib.reload(app_module)
    from app import app as fastapi_app

    return TestClient(fastapi_app)


# ── Background ────────────────────────────────────────────────────────────────


@given("el sistema de identidad está inicializado", target_fixture="context")
def sistema_inicializado_adj112(context: dict[str, Any]) -> dict[str, Any]:
    return context


# ── Given ─────────────────────────────────────────────────────────────────────


@given(
    parsers.parse(
        'existe un usuario autenticado con email "{email}" password "{password}" y roles "{roles_str}"'
    )
)
def existe_usuario_autenticado(
    client: TestClient,
    context: dict[str, Any],
    email: str,
    password: str,
    roles_str: str,
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

    login_resp = client.post(
        "/auth/login", json={"email": email, "password": password, "rol_elegido": roles[0]}
    )
    assert login_resp.status_code == 200, f"Login falló: {login_resp.status_code} {login_resp.text}"
    token = login_resp.json().get("access_token")
    assert token, "No hay access_token tras login"

    context["token"] = token
    context["auth_headers"] = {"Authorization": f"Bearer {token}"}


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('hace POST /auth/me/roles con rol "{rol}"'))
def post_agregar_rol(client: TestClient, context: dict[str, Any], rol: str) -> None:
    context["response"] = client.post(
        "/auth/me/roles",
        json={"rol": rol},
        headers=context.get("auth_headers", {}),
    )


@when(parsers.parse("hace DELETE /auth/me/roles/{rol}"))
def delete_quitar_rol(client: TestClient, context: dict[str, Any], rol: str) -> None:
    context["response"] = client.delete(
        f"/auth/me/roles/{rol}",
        headers=context.get("auth_headers", {}),
    )


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status_code:d}"))
def check_status(context: dict[str, Any], status_code: int) -> None:
    resp = context["response"]
    assert (
        resp.status_code == status_code
    ), f"Esperaba {status_code}, got {resp.status_code}: {resp.text}"


@then(parsers.parse('la respuesta incluye los roles "{roles_str}"'))
def check_roles(context: dict[str, Any], roles_str: str) -> None:
    expected = {r.strip() for r in roles_str.split(",")}
    actual = set(context["response"].json().get("roles", []))
    assert actual == expected, f"Esperaba roles {expected}, got {actual}"
