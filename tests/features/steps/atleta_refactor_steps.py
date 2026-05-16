"""Step definitions BDD — US-ADJ-11.3: Atleta con campos opcionales y BT-002."""

from __future__ import annotations

import asyncio
from datetime import date
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from identidad.api.dependencies import get_current_user
from registro.api.router import router
from registro.domain.aggregates.atleta import Atleta
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository

scenarios("../US-ADJ-11.3-atleta-refactor.feature")


@pytest.fixture
def ctx(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    db_path = str(tmp_path / "registro.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", db_path)
    repo = SQLiteAtletaRepository(db_path)
    return {"repo": repo, "response": None, "email_activo": None}


@pytest.fixture
def client(ctx: dict) -> TestClient:
    app = FastAPI()
    app.include_router(router)

    def _current_user():
        return {
            "sub": str(uuid4()),
            "email": ctx["email_activo"] or "atleta@test.com",
            "rol": "ATLETA",
        }

    app.dependency_overrides[get_current_user] = _current_user
    return TestClient(app)


# ── Givens ────────────────────────────────────────────────────────────────────


@given("el repositorio de atletas está inicializado")
def repositorio_inicializado(ctx: dict) -> None:
    pass


@given(parsers.parse('no existe ningún atleta con email "{email}"'))
def no_existe_atleta(email: str, ctx: dict) -> None:
    ctx["email_activo"] = email


@given(parsers.parse('existe un atleta con email "{email}" sin dni ni telefono'))
def existe_atleta_sin_dni(email: str, ctx: dict) -> None:
    atleta = Atleta(
        atleta_id=uuid4(),
        nombre="Existente",
        apellido="Atleta",
        email=email,
        fecha_nacimiento=date(1990, 1, 1),
    )
    asyncio.run(ctx["repo"].save(atleta))
    ctx["email_activo"] = email


@given(parsers.parse('existe un atleta con email "{email}" con club "{club}"'))
def existe_atleta_con_club(email: str, club: str, ctx: dict) -> None:
    atleta = Atleta(
        atleta_id=uuid4(),
        nombre="Con",
        apellido="Club",
        email=email,
        fecha_nacimiento=date(1992, 3, 10),
        club=club,
    )
    asyncio.run(ctx["repo"].save(atleta))
    ctx["email_activo"] = email


# ── Whens ─────────────────────────────────────────────────────────────────────


@when(
    parsers.parse(
        'se registra un atleta con email "{email}" nombre "{nombre}" apellido "{apellido}" '
        'fecha_nacimiento "{fecha}" sin club ni categoria'
    )
)
def registrar_atleta_minimo(
    email: str, nombre: str, apellido: str, fecha: str, ctx: dict, client: TestClient
) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post(
        "/registro/atletas",
        json={"nombre": nombre, "apellido": apellido, "email": email, "fecha_nacimiento": fecha},
    )


@when(
    parsers.parse(
        'se registra un atleta con email "{email}" nombre "{nombre}" apellido "{apellido}" '
        'fecha_nacimiento "{fecha}" club "{club}" categoria "{categoria}" '
        'dni "{dni}" telefono "{telefono}"'
    )
)
def registrar_atleta_completo(
    email: str,
    nombre: str,
    apellido: str,
    fecha: str,
    club: str,
    categoria: str,
    dni: str,
    telefono: str,
    ctx: dict,
    client: TestClient,
) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post(
        "/registro/atletas",
        json={
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "fecha_nacimiento": fecha,
            "club": club,
            "categoria": categoria,
            "dni": dni,
            "telefono": telefono,
        },
    )


@when(parsers.parse('actualiza su perfil con dni "{dni}" y telefono "{telefono}"'))
def actualizar_dni_telefono(dni: str, telefono: str, ctx: dict, client: TestClient) -> None:
    ctx["response"] = client.patch(
        "/registro/atletas/me",
        json={"dni": dni, "telefono": telefono},
    )


@when("actualiza su perfil con club null")
def actualizar_club_null(ctx: dict, client: TestClient) -> None:
    ctx["response"] = client.patch("/registro/atletas/me", json={"club": None})


@when(
    parsers.parse(
        'se registra un atleta con email "{email}" nombre "{nombre}" apellido "{apellido}" '
        'fecha_nacimiento "{fecha}" sin club ni categoria'
    )
)
def registrar_atleta_duplicado(
    email: str, nombre: str, apellido: str, fecha: str, ctx: dict, client: TestClient
) -> None:
    ctx["response"] = client.post(
        "/registro/atletas",
        json={"nombre": nombre, "apellido": apellido, "email": email, "fecha_nacimiento": fecha},
    )


@when(
    parsers.parse(
        'se registra un atleta con email "{email}" nombre "{nombre}" apellido "{apellido}" '
        'fecha_nacimiento "{fecha}" club ""'
    )
)
def registrar_atleta_club_vacio(
    email: str, nombre: str, apellido: str, fecha: str, ctx: dict, client: TestClient
) -> None:
    ctx["email_activo"] = email
    ctx["response"] = client.post(
        "/registro/atletas",
        json={
            "nombre": nombre,
            "apellido": apellido,
            "email": email,
            "fecha_nacimiento": fecha,
            "club": "",
        },
    )


# ── Thens ─────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status:d}"))
def respuesta_status(status: int, ctx: dict) -> None:
    assert ctx["response"].status_code == status, ctx["response"].text


@then("la respuesta contiene un atleta_id generado por el backend")
def respuesta_contiene_atleta_id(ctx: dict) -> None:
    data = ctx["response"].json()
    assert "atleta_id" in data
    assert data["atleta_id"]


@then(parsers.parse('el atleta "{email}" tiene club null y categoria null'))
def atleta_club_categoria_null(email: str, ctx: dict) -> None:
    atleta = asyncio.run(ctx["repo"].find_by_email(email))
    assert atleta is not None
    assert atleta.club is None
    assert atleta.categoria is None


@then(parsers.parse('el atleta "{email}" tiene dni "{dni}" y telefono "{telefono}"'))
def atleta_tiene_dni_telefono(email: str, dni: str, telefono: str, ctx: dict) -> None:
    atleta = asyncio.run(ctx["repo"].find_by_email(email))
    assert atleta is not None
    assert atleta.dni == dni
    assert atleta.telefono == telefono
