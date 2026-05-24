from __future__ import annotations

import asyncio
from datetime import date
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app import app
from identidad.api.dependencies import get_current_user
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from registro.domain.value_objects.estado_aceptacion import EstadoAceptacion
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina

scenarios("../US-ADJ-12.5-registro-estado-aceptacion.feature")


@pytest.fixture
def ctx(tmp_path: Any, monkeypatch: pytest.MonkeyPatch) -> dict[str, Any]:
    registro_db = tmp_path / "registro.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))

    atleta_id = uuid4()
    torneo_id = uuid4()

    atleta_repo = SQLiteAtletaRepository(str(registro_db))
    inscripcion_repo = SQLiteInscripcionRepository(str(registro_db))

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=atleta_id,
                nombre="Ana",
                apellido="Gomez",
                email="ana@email.com",
                fecha_nacimiento=date(1993, 7, 5),
                categoria=Categoria.SENIOR_FEMENINO,
                club="Azul",
            )
        )
        inscripcion = Inscripcion(
            atleta_id=atleta_id,
            torneo_id=torneo_id,
            disciplinas=frozenset({Disciplina.STA}),
        )
        await inscripcion_repo.save(inscripcion)

    asyncio.run(_seed())

    async def _get_id() -> str:
        ins = await inscripcion_repo.find_by_atleta_y_torneo(atleta_id, torneo_id)
        return str(ins.inscripcion_id)  # type: ignore[union-attr]

    data: dict[str, Any] = {
        "inscripcion_id": asyncio.run(_get_id()),
        "repo": inscripcion_repo,
        "response": None,
    }

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "orga@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }

    yield data

    app.dependency_overrides.clear()


# ── Given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('un torneo y un atleta inscripto activo con estado aceptación "{estado}"'))
def given_inscripcion_activa(ctx: dict[str, Any], estado: str) -> None:
    pass  # seeded in fixture


@given(parsers.parse('la inscripción tiene estado_aceptacion "{estado}"'))
def given_inscripcion_con_estado(ctx: dict[str, Any], estado: str) -> None:
    client = TestClient(app)
    client.patch(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/aceptacion",
        json={"estado": estado},
    )


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('el organizador cambia el estado de aceptación a "{estado}"'))
def when_cambia_aceptacion(ctx: dict[str, Any], estado: str) -> None:
    client = TestClient(app)
    ctx["response"] = client.patch(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/aceptacion",
        json={"estado": estado},
    )


@when("el organizador consulta el detalle de la inscripción")
def when_consulta_detalle(ctx: dict[str, Any]) -> None:
    client = TestClient(app)
    ctx["response"] = client.get(f"/registro/inscripciones/{ctx['inscripcion_id']}/detalle")


@when(parsers.parse('un usuario con rol "{rol}" intenta cambiar el estado de aceptación'))
def when_usuario_sin_permiso(ctx: dict[str, Any], rol: str) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "user@ataraxiadive.io",
        "rol": rol,
    }
    client = TestClient(app)
    ctx["response"] = client.patch(
        f"/registro/inscripciones/{ctx['inscripcion_id']}/aceptacion",
        json={"estado": "RECHAZADO"},
    )


@when("se recarga la inscripción desde la base de datos")
def when_recarga_inscripcion(ctx: dict[str, Any]) -> None:
    async def _load() -> Inscripcion:
        from uuid import UUID

        ins = await ctx["repo"].find_by_id(UUID(ctx["inscripcion_id"]))
        return ins  # type: ignore[return-value]

    ctx["inscripcion_recargada"] = asyncio.run(_load())


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('el estado_aceptacion de la inscripción es "{estado}"'))
def then_estado_aceptacion(ctx: dict[str, Any], estado: str) -> None:
    if ctx.get("response") is not None:
        assert ctx["response"].status_code == 200
        assert ctx["response"].json()["estado"] == estado
    else:

        async def _check() -> str:
            from uuid import UUID

            ins = await ctx["repo"].find_by_id(UUID(ctx["inscripcion_id"]))
            return ins.estado_aceptacion.value  # type: ignore[union-attr]

        assert asyncio.run(_check()) == estado


@then(parsers.parse("la respuesta es {status_code:d}"))
def then_status_code(ctx: dict[str, Any], status_code: int) -> None:
    assert ctx["response"].status_code == status_code


@then(
    "la respuesta incluye nombre, categoría, club, brevet, dni, telefono, estado_aceptacion y URLs de adjuntos"
)
def then_detalle_completo(ctx: dict[str, Any]) -> None:
    assert ctx["response"].status_code == 200
    data = ctx["response"].json()
    assert "nombre" in data
    assert "apellido" in data
    assert "categoria" in data
    assert "club" in data
    assert "brevet" in data
    assert "dni" in data
    assert "telefono" in data
    assert "estado_aceptacion" in data
    assert "apto_medico_url" in data
    assert "constancia_pago_url" in data


@then(parsers.parse('el estado_aceptacion cargado es "{estado}"'))
def then_estado_aceptacion_cargado(ctx: dict[str, Any], estado: str) -> None:
    assert ctx["inscripcion_recargada"].estado_aceptacion == EstadoAceptacion(estado)
