"""Integración HTTP — PATCH /registro/atletas/me (US-ADJ-10.2)."""

from __future__ import annotations

import asyncio
from datetime import date
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user
from registro.api.router import router
from registro.domain.aggregates.atleta import Atleta
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository


def _atleta_dep(email: str = "atleta@test.com") -> dict:
    return {"sub": "atleta-1", "email": email, "rol": "ATLETA"}


def _seed_atleta(repo: SQLiteAtletaRepository, email: str = "atleta@test.com") -> Atleta:
    atleta = Atleta(
        atleta_id=uuid4(),
        nombre="Ana",
        apellido="Garcia",
        email=email,
        fecha_nacimiento=date(1990, 5, 10),
        categoria=Categoria.SENIOR_FEMENINO,
        club="Poseidon",
    )
    asyncio.run(repo.save(atleta))
    return atleta


@pytest.fixture
def ctx(tmp_path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("REGISTRO_DB_PATH", str(tmp_path / "registro.db"))
    app = FastAPI()
    app.include_router(router)

    repo = SQLiteAtletaRepository(str(tmp_path / "registro.db"))
    client = TestClient(app)
    return {"client": client, "repo": repo}


def _override_atleta(app, email: str = "atleta@test.com"):
    app.dependency_overrides[get_current_user] = lambda: _atleta_dep(email)


def test_patch_actualiza_nombre_y_club(ctx):
    _seed_atleta(ctx["repo"])
    _override_atleta(ctx["client"].app)

    response = ctx["client"].patch(
        "/registro/atletas/me",
        json={"nombre": "Juan", "club": "Neptuno"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Juan"
    assert data["club"] == "Neptuno"


def test_patch_semantica_parcial_no_borra_campos(ctx):
    _seed_atleta(ctx["repo"])
    _override_atleta(ctx["client"].app)

    ctx["client"].patch("/registro/atletas/me", json={"club": "Neptuno"})

    atleta = asyncio.run(ctx["repo"].find_by_email("atleta@test.com"))
    assert atleta is not None
    assert atleta.nombre == "Ana"
    assert atleta.apellido == "Garcia"
    assert atleta.categoria == Categoria.SENIOR_FEMENINO
    assert atleta.club == "Neptuno"


def test_patch_actualiza_categoria(ctx):
    _seed_atleta(ctx["repo"])
    _override_atleta(ctx["client"].app)

    response = ctx["client"].patch(
        "/registro/atletas/me",
        json={"categoria": "MASTER_MASCULINO"},
    )

    assert response.status_code == 200
    assert response.json()["categoria"] == "MASTER_MASCULINO"


def test_patch_sin_perfil_retorna_404(ctx):
    _override_atleta(ctx["client"].app, email="noexiste@test.com")

    response = ctx["client"].patch(
        "/registro/atletas/me",
        json={"nombre": "Juan"},
    )

    assert response.status_code == 404


def test_patch_actualiza_fecha_nacimiento(ctx):
    _seed_atleta(ctx["repo"])
    _override_atleta(ctx["client"].app)

    response = ctx["client"].patch(
        "/registro/atletas/me",
        json={"fecha_nacimiento": "1985-03-20"},
    )

    assert response.status_code == 200
    assert response.json()["fecha_nacimiento"] == "1985-03-20"


def test_patch_actualiza_brevet(ctx):
    _seed_atleta(ctx["repo"])
    _override_atleta(ctx["client"].app)

    response = ctx["client"].patch(
        "/registro/atletas/me",
        json={"brevet": "AIDA-3"},
    )

    assert response.status_code == 200
    assert response.json()["brevet"] == "AIDA-3"


def test_patch_fecha_nacimiento_futura_retorna_error(ctx):
    _seed_atleta(ctx["repo"])
    _override_atleta(ctx["client"].app)

    response = ctx["client"].patch(
        "/registro/atletas/me",
        json={"fecha_nacimiento": "2099-01-01"},
    )

    assert response.status_code in (400, 422)
