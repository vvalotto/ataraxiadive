"""Step definitions BDD — US-ADJ-11.4: entidad Juez."""

from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from identidad.api.dependencies import get_current_user
from registro.api.router import router
from registro.infrastructure.repositories.sqlite_juez_repository import SQLiteJuezRepository

scenarios("../US-ADJ-11.4-juez.feature")


@pytest.fixture
def ctx(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    db_path = str(tmp_path / "registro.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", db_path)
    repo = SQLiteJuezRepository(db_path)
    return {"repo": repo, "response": None, "email_activo": None, "rol_activo": "JUEZ"}


@pytest.fixture
def client(ctx: dict) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    def _current_user():
        return {
            "sub": str(uuid4()),
            "email": ctx["email_activo"] or "juez@test.com",
            "rol": ctx["rol_activo"],
        }

    app.dependency_overrides[get_current_user] = _current_user
    return TestClient(app)


# ── Givens ────────────────────────────────────────────────────────────────────


@given("el repositorio de jueces está inicializado")
def repositorio_inicializado(ctx: dict) -> None:
    pass


@given(parsers.parse('no existe perfil Juez para "{email}"'))
def no_existe_juez(email: str, ctx: dict) -> None:
    ctx["email_activo"] = email


@given(parsers.parse('existe un perfil Juez para "{email}" sin licencia'))
def existe_juez_sin_licencia(email: str, ctx: dict) -> None:
    from registro.domain.aggregates.juez import Juez

    juez = Juez(juez_id=uuid4(), email=email)
    asyncio.run(ctx["repo"].save(juez))
    ctx["email_activo"] = email


# ── Whens ─────────────────────────────────────────────────────────────────────


@when(parsers.parse('hace POST /registro/jueces con body vacío como "{email}"'))
def post_juez_vacio(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post("/registro/jueces", json={})


@when(
    parsers.parse(
        'hace POST /registro/jueces con numero_licencia "{licencia}" y federacion "{fed}" '
        'como "{email}"'
    )
)
def post_juez_completo(licencia: str, fed: str, email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post(
        "/registro/jueces",
        json={"numero_licencia": licencia, "federacion": fed},
    )


@when(parsers.parse('hace GET /registro/jueces/me como "{email}"'))
def get_juez_me(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.get("/registro/jueces/me")


@when(
    parsers.parse('hace PATCH /registro/jueces/me con numero_licencia "{licencia}" como "{email}"')
)
def patch_juez_licencia(licencia: str, email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.patch("/registro/jueces/me", json={"numero_licencia": licencia})


@when(parsers.parse('hace POST /registro/jueces como ATLETA con email "{email}"'))
def post_juez_como_atleta(email: str, ctx: dict, client: TestClient) -> None:
    ctx["email_activo"] = email
    ctx["rol_activo"] = "ATLETA"
    ctx["response"] = client.post("/registro/jueces", json={})


# ── Thens ─────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status:d}"))
def respuesta_status(status: int, ctx: dict) -> None:
    assert ctx["response"].status_code == status, ctx["response"].text


@then("la respuesta contiene un juez_id generado por el backend")
def respuesta_contiene_juez_id(ctx: dict) -> None:
    data = ctx["response"].json()
    assert "juez_id" in data
    assert data["juez_id"]


@then(parsers.parse('el juez "{email}" tiene numero_licencia null y federacion null'))
def juez_sin_datos(email: str, ctx: dict) -> None:
    juez = asyncio.run(ctx["repo"].find_by_email(email))
    assert juez is not None
    assert juez.numero_licencia is None
    assert juez.federacion is None


@then(parsers.parse('el juez "{email}" tiene numero_licencia "{licencia}" y federacion "{fed}"'))
def juez_con_datos(email: str, licencia: str, fed: str, ctx: dict) -> None:
    juez = asyncio.run(ctx["repo"].find_by_email(email))
    assert juez is not None
    assert juez.numero_licencia == licencia
    assert juez.federacion == fed


@then(parsers.parse('el juez "{email}" tiene numero_licencia "{licencia}" y federacion null'))
def juez_con_licencia_sin_federacion(email: str, licencia: str, ctx: dict) -> None:
    juez = asyncio.run(ctx["repo"].find_by_email(email))
    assert juez is not None
    assert juez.numero_licencia == licencia
    assert juez.federacion is None


@then(parsers.parse('el cuerpo contiene el email "{email}"'))
def cuerpo_contiene_email(email: str, ctx: dict) -> None:
    data = ctx["response"].json()
    assert data.get("email") == email
