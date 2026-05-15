"""Step definitions BDD — US-ADJ-10.2: Pagina Mis Datos del atleta."""

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
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository

scenarios("../US-ADJ-10.2-mis-datos-atleta.feature")

_EMAIL = "atleta@test.com"


@pytest.fixture
def context(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setenv("REGISTRO_DB_PATH", str(tmp_path / "registro.db"))
    repo = SQLiteAtletaRepository(str(tmp_path / "registro.db"))
    return {"repo": repo, "response": None}


@pytest.fixture
def client(context: dict) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "atleta-1",
        "email": _EMAIL,
        "rol": "ATLETA",
    }
    return TestClient(app)


def _seed(
    repo: SQLiteAtletaRepository,
    nombre: str = "Ana",
    apellido: str = "Garcia",
    categoria: Categoria = Categoria.SENIOR_FEMENINO,
    club: str = "Poseidon",
) -> None:
    atleta = Atleta(
        atleta_id=uuid4(),
        nombre=nombre,
        apellido=apellido,
        email=_EMAIL,
        fecha_nacimiento=date(1990, 5, 10),
        categoria=categoria,
        club=club,
    )
    asyncio.run(repo.save(atleta))


@given(
    parsers.parse(
        'el atleta esta autenticado y tiene perfil en registro con nombre "{nombre}" y club "{club}"'
    )
)
def given_perfil_nombre_club(context: dict, nombre: str, club: str) -> None:
    _seed(context["repo"], nombre=nombre, club=club)


@given(
    parsers.parse("el atleta esta autenticado y tiene perfil en registro con categoria {categoria}")
)
def given_perfil_categoria(context: dict, categoria: str) -> None:
    _seed(context["repo"], categoria=Categoria[categoria])


@given(
    parsers.parse(
        'el atleta esta autenticado y tiene perfil con nombre "{nombre}" apellido "{apellido}" categoria {categoria} y club "{club}"'
    )
)
def given_perfil_completo(
    context: dict, nombre: str, apellido: str, categoria: str, club: str
) -> None:
    _seed(
        context["repo"], nombre=nombre, apellido=apellido, categoria=Categoria[categoria], club=club
    )


@given("el usuario autenticado no tiene perfil de atleta en registro")
def given_sin_perfil(context: dict) -> None:
    pass


@when(parsers.parse('llama a PATCH /registro/atletas/me con nombre "{nombre}" y club "{club}"'))
def when_patch_nombre_club(client: TestClient, context: dict, nombre: str, club: str) -> None:
    context["response"] = client.patch(
        "/registro/atletas/me", json={"nombre": nombre, "club": club}
    )


@when(parsers.parse("llama a PATCH /registro/atletas/me con categoria {categoria}"))
def when_patch_categoria(client: TestClient, context: dict, categoria: str) -> None:
    context["response"] = client.patch("/registro/atletas/me", json={"categoria": categoria})


@when('llama a PATCH /registro/atletas/me con solo club "Neptuno"')
def when_patch_solo_club(client: TestClient, context: dict) -> None:
    context["response"] = client.patch("/registro/atletas/me", json={"club": "Neptuno"})


@when(parsers.parse('llama a PATCH /registro/atletas/me con nombre "{nombre}"'))
def when_patch_nombre(client: TestClient, context: dict, nombre: str) -> None:
    context["response"] = client.patch("/registro/atletas/me", json={"nombre": nombre})


@then("la respuesta es 200 OK")
def then_200(context: dict) -> None:
    assert context["response"].status_code == 200


@then("la respuesta es 404")
def then_404(context: dict) -> None:
    assert context["response"].status_code == 404


@then(parsers.parse('el perfil del atleta tiene nombre "{nombre}" y club "{club}"'))
def then_nombre_club(context: dict, nombre: str, club: str) -> None:
    atleta = asyncio.run(context["repo"].find_by_email(_EMAIL))
    assert atleta is not None
    assert atleta.nombre == nombre
    assert atleta.club == club


@then(parsers.parse("el perfil del atleta tiene categoria {categoria}"))
def then_categoria(context: dict, categoria: str) -> None:
    atleta = asyncio.run(context["repo"].find_by_email(_EMAIL))
    assert atleta is not None
    assert atleta.categoria == Categoria[categoria]


@then(parsers.parse('el nombre sigue siendo "{nombre}"'))
def then_nombre_igual(context: dict, nombre: str) -> None:
    atleta = asyncio.run(context["repo"].find_by_email(_EMAIL))
    assert atleta is not None
    assert atleta.nombre == nombre


@then(parsers.parse('el apellido sigue siendo "{apellido}"'))
def then_apellido_igual(context: dict, apellido: str) -> None:
    atleta = asyncio.run(context["repo"].find_by_email(_EMAIL))
    assert atleta is not None
    assert atleta.apellido == apellido


@then(parsers.parse("la categoria sigue siendo {categoria}"))
def then_categoria_igual(context: dict, categoria: str) -> None:
    atleta = asyncio.run(context["repo"].find_by_email(_EMAIL))
    assert atleta is not None
    assert atleta.categoria == Categoria[categoria]


@then(parsers.parse('el club queda como "{club}"'))
def then_club(context: dict, club: str) -> None:
    atleta = asyncio.run(context["repo"].find_by_email(_EMAIL))
    assert atleta is not None
    assert atleta.club == club
