"""Step definitions BDD — US-ADJ-10.3: Email bienvenida y auto-login post-registro."""

from __future__ import annotations

import os
import tempfile
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../US-ADJ-10.3-email-autologin-post-registro.feature")

_PASSWORD = "Apnea12345"


# ── Spies y stubs ─────────────────────────────────────────────────────────────


class SpyEmailSender:
    def __init__(self) -> None:
        self.calls: list[str] = []
        self.asuntos: list[str] = []

    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        self.calls.append(destinatario.email)
        self.asuntos.append(contenido.asunto)
        return "spy-id"


class FailingEmailSender:
    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        raise RuntimeError("SMTP no disponible")


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "identidad_bdd.db")
    monkeypatch.setenv("IDENTIDAD_DB_PATH", db_path)
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-bdd-us-adj-10-3-!!")
    return {}


@pytest.fixture
def client(context: dict[str, Any]) -> TestClient:
    import importlib
    import app as app_module

    importlib.reload(app_module)
    from app import app as fastapi_app

    return TestClient(fastapi_app)


# ── Givens ────────────────────────────────────────────────────────────────────


@given("el servicio de identidad esta inicializado con DB temporal")
def servicio_identidad_inicializado(context: dict[str, Any]) -> None:
    pass  # garantizado por fixtures context + client


@given("el email port esta disponible y captura llamadas")
def email_port_disponible(context: dict[str, Any], client: TestClient) -> None:
    from identidad.api.dependencies import get_email_sender

    spy = SpyEmailSender()
    context["email_spy"] = spy
    client.app.dependency_overrides[get_email_sender] = lambda: spy  # type: ignore[union-attr]


@given("el email port esta configurado para lanzar excepcion")
def email_port_falla(context: dict[str, Any], client: TestClient) -> None:
    from identidad.api.dependencies import get_email_sender

    context["email_spy"] = None
    client.app.dependency_overrides[get_email_sender] = lambda: FailingEmailSender()  # type: ignore[union-attr]


# ── Whens ─────────────────────────────────────────────────────────────────────


@when(parsers.parse('se registra un nuevo usuario con email "{email}" y rol "{rol}"'))
def registrar_usuario(context: dict[str, Any], client: TestClient, email: str, rol: str) -> None:
    context["email"] = email
    context["password"] = _PASSWORD
    context["rol"] = rol
    context["registro_response"] = client.post(
        "/auth/registro",
        json={
            "nombre": "Test",
            "apellido": "BDD",
            "email": email,
            "password": _PASSWORD,
            "rol": rol,
        },
    )


@when(parsers.parse('se intenta login con email "{email}" y password "{password}"'))
def intentar_login(context: dict[str, Any], client: TestClient, email: str, password: str) -> None:
    context["login_response"] = client.post(
        "/auth/login",
        json={"email": email, "password": password},
    )


# ── Thens ─────────────────────────────────────────────────────────────────────


@then("el registro responde 201")
def registro_responde_201(context: dict[str, Any]) -> None:
    assert context["registro_response"].status_code == 201


@then(parsers.parse("el email port recibio exactamente {n:d} llamada a enviar"))
def email_port_recibio_n_llamadas(context: dict[str, Any], n: int) -> None:
    spy: SpyEmailSender = context["email_spy"]
    assert len(spy.calls) == n


@then(parsers.parse('el destinatario del email es "{email}"'))
def destinatario_es(context: dict[str, Any], email: str) -> None:
    spy: SpyEmailSender = context["email_spy"]
    assert spy.calls[0] == email


@then(parsers.parse('el usuario queda registrado correctamente con email "{email}"'))
def usuario_registrado(context: dict[str, Any], email: str) -> None:
    assert context["registro_response"].status_code == 201


@then("el login responde 200")
def login_responde_200(context: dict[str, Any]) -> None:
    assert context["login_response"].status_code == 200


@then("la respuesta contiene un access_token valido")
def respuesta_contiene_token(context: dict[str, Any]) -> None:
    data = context["login_response"].json()
    assert "access_token" in data
    assert len(data["access_token"]) > 0


@then(parsers.parse('el token contiene rol "{rol}"'))
def token_contiene_rol(context: dict[str, Any], rol: str) -> None:
    from identidad.infrastructure.jwt_service import JWTService

    token = context["login_response"].json()["access_token"]
    payload = JWTService().verify(token)
    assert payload["rol"].lower() == rol.lower()
