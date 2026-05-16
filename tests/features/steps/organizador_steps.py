"""Step definitions BDD — US-ADJ-11.5: entidad Organizador."""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from identidad.api.dependencies import get_current_user
from registro.api.router import router
from registro.infrastructure.repositories.sqlite_organizador_repository import (
    SQLiteOrganizadorRepository,
)

scenarios("../US-ADJ-11.5-organizador.feature")


@pytest.fixture
def ctx(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    db_path = str(tmp_path / "registro.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", db_path)
    repo = SQLiteOrganizadorRepository(db_path)
    return {"repo": repo, "response": None, "email_activo": None, "rol_activo": "ORGANIZADOR"}


@pytest.fixture
def client(ctx: dict) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    def _current_user():
        return {
            "sub": str(uuid4()),
            "email": ctx["email_activo"] or "org@test.com",
            "rol": ctx["rol_activo"],
        }

    app.dependency_overrides[get_current_user] = _current_user
    return TestClient(app)


# ── Givens ────────────────────────────────────────────────────────────────────


@given("el repositorio de organizadores está inicializado")
def repositorio_inicializado(ctx: dict) -> None:
    pass


@given(parsers.parse('no existe perfil Organizador para "{email}"'))
def no_existe_organizador(email: str, ctx: dict) -> None:
    ctx["email_activo"] = email


@given(parsers.parse('existe un perfil Organizador para "{email}" sin nombre'))
def existe_organizador_sin_nombre(email: str, ctx: dict) -> None:
    from registro.domain.aggregates.organizador import Organizador

    org = Organizador(organizador_id=uuid4(), email=email)
    asyncio.run(ctx["repo"].save(org))
    ctx["email_activo"] = email


@given(parsers.parse('existe un perfil Organizador para "{email}" con nombre "{nombre}"'))
def existe_organizador_con_nombre(email: str, nombre: str, ctx: dict) -> None:
    from registro.domain.aggregates.organizador import Organizador

    org = Organizador(organizador_id=uuid4(), email=email, nombre_organizacion=nombre)
    asyncio.run(ctx["repo"].save(org))
    ctx["email_activo"] = email


# ── Whens ─────────────────────────────────────────────────────────────────────


@when(parsers.parse('hace POST /registro/organizadores con body vacío como "{email}"'))
def post_organizador_vacio(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post("/registro/organizadores", json={})


@when(
    parsers.parse(
        'hace POST /registro/organizadores con nombre_organizacion "{nombre}" como "{email}"'
    )
)
def post_organizador_con_nombre(nombre: str, email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post(
        "/registro/organizadores",
        json={"nombre_organizacion": nombre},
    )


@when(parsers.parse('hace GET /registro/organizadores/me como "{email}"'))
def get_organizador_me(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.get("/registro/organizadores/me")


@when(
    parsers.parse(
        'hace PATCH /registro/organizadores/me con nombre_organizacion "{nombre}" como "{email}"'
    )
)
def patch_organizador_nombre(nombre: str, email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.patch(
        "/registro/organizadores/me", json={"nombre_organizacion": nombre}
    )


@when(
    parsers.parse(
        'hace PATCH /registro/organizadores/me con nombre_organizacion null como "{email}"'
    )
)
def patch_organizador_nombre_null(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.patch("/registro/organizadores/me", json={"nombre_organizacion": None})


@when(parsers.parse('hace POST /registro/organizadores como ATLETA con email "{email}"'))
def post_organizador_como_atleta(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["rol_activo"] = "ATLETA"
    ctx["response"] = client.post("/registro/organizadores", json={})


# ── Thens ─────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status:d}"))
def respuesta_status(status: int, ctx: dict) -> None:
    assert ctx["response"].status_code == status, ctx["response"].text


@then("la respuesta contiene un organizador_id generado por el backend")
def respuesta_contiene_organizador_id(ctx: dict) -> None:
    data = ctx["response"].json()
    assert "organizador_id" in data
    assert data["organizador_id"]


@then(parsers.parse('el organizador "{email}" tiene nombre_organizacion null'))
def organizador_sin_nombre(email: str, ctx: dict) -> None:
    org = asyncio.run(ctx["repo"].find_by_email(email))
    assert org is not None
    assert org.nombre_organizacion is None


@then(parsers.parse('el organizador "{email}" tiene nombre_organizacion "{nombre}"'))
def organizador_con_nombre(email: str, nombre: str, ctx: dict) -> None:
    org = asyncio.run(ctx["repo"].find_by_email(email))
    assert org is not None
    assert org.nombre_organizacion == nombre


@then(parsers.parse('el cuerpo contiene el email "{email}"'))
def cuerpo_contiene_email(email: str, ctx: dict) -> None:
    data = ctx["response"].json()
    assert data.get("email") == email


@then(parsers.parse('el detalle contiene "{texto}"'))
def detalle_contiene(texto: str, ctx: dict) -> None:
    data = ctx["response"].json()
    assert texto in data.get("detail", ""), data
