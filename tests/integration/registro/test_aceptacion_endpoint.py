from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

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


@pytest.fixture
def aceptacion_context(tmp_path, monkeypatch):
    registro_db = tmp_path / "registro.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))

    torneo_id = uuid4()
    atleta_id = uuid4()

    atleta_repo = SQLiteAtletaRepository(str(registro_db))
    inscripcion_repo = SQLiteInscripcionRepository(str(registro_db))

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=atleta_id,
                nombre="Laura",
                apellido="Diaz",
                email="laura@email.com",
                fecha_nacimiento=date(1995, 3, 20),
                categoria=Categoria.SENIOR_FEMENINO,
                club="Azul",
                brevet="B-123",
                dni="12345678",
                telefono="555-1234",
            )
        )
        inscripcion = Inscripcion(
            atleta_id=atleta_id,
            torneo_id=torneo_id,
            disciplinas=frozenset({Disciplina.DNF}),
        )
        await inscripcion_repo.save(inscripcion)

    import asyncio

    asyncio.run(_seed())

    async def _get_inscripcion_id() -> str:
        ins = await inscripcion_repo.find_by_atleta_y_torneo(atleta_id, torneo_id)
        return str(ins.inscripcion_id)  # type: ignore[union-attr]

    inscripcion_id = asyncio.run(_get_inscripcion_id())

    yield {
        "inscripcion_id": inscripcion_id,
        "atleta_id": str(atleta_id),
    }

    app.dependency_overrides.clear()


def _orga_override():
    return {
        "sub": str(uuid4()),
        "email": "orga@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }


def _atleta_override():
    return {
        "sub": str(uuid4()),
        "email": "atleta@ataraxiadive.io",
        "rol": "ATLETA",
    }


def test_patch_aceptacion_rechaza_inscripcion(aceptacion_context):
    app.dependency_overrides[get_current_user] = _orga_override
    client = TestClient(app)

    response = client.patch(
        f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/aceptacion",
        json={"estado": "RECHAZADO"},
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "RECHAZADO"


def test_patch_aceptacion_acepta_inscripcion(aceptacion_context):
    app.dependency_overrides[get_current_user] = _orga_override
    client = TestClient(app)

    client.patch(
        f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/aceptacion",
        json={"estado": "RECHAZADO"},
    )
    response = client.patch(
        f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/aceptacion",
        json={"estado": "ACEPTADO"},
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "ACEPTADO"


def test_patch_aceptacion_rechaza_rol_atleta(aceptacion_context):
    app.dependency_overrides[get_current_user] = _atleta_override
    client = TestClient(app)

    response = client.patch(
        f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/aceptacion",
        json={"estado": "RECHAZADO"},
    )

    assert response.status_code == 403


def test_patch_aceptacion_inscripcion_no_encontrada(aceptacion_context):
    app.dependency_overrides[get_current_user] = _orga_override
    client = TestClient(app)

    response = client.patch(
        f"/registro/inscripciones/{uuid4()}/aceptacion",
        json={"estado": "RECHAZADO"},
    )

    assert response.status_code == 404


def test_get_detalle_devuelve_datos_atleta_y_estado_aceptacion(aceptacion_context):
    app.dependency_overrides[get_current_user] = _orga_override
    client = TestClient(app)

    response = client.get(f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/detalle")

    assert response.status_code == 200
    data = response.json()
    assert data["nombre"] == "Laura"
    assert data["apellido"] == "Diaz"
    assert data["categoria"] == "SENIOR_FEMENINO"
    assert data["club"] == "Azul"
    assert data["brevet"] == "B-123"
    assert data["dni"] == "12345678"
    assert data["telefono"] == "555-1234"
    assert data["estado_aceptacion"] == "ACEPTADO"
    assert data["apto_medico_url"] is None
    assert data["constancia_pago_url"] is None


def test_get_detalle_refleja_cambio_de_aceptacion(aceptacion_context):
    app.dependency_overrides[get_current_user] = _orga_override
    client = TestClient(app)

    client.patch(
        f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/aceptacion",
        json={"estado": "RECHAZADO"},
    )

    response = client.get(f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/detalle")

    assert response.status_code == 200
    assert response.json()["estado_aceptacion"] == "RECHAZADO"


def test_get_detalle_rechaza_rol_atleta(aceptacion_context):
    app.dependency_overrides[get_current_user] = _atleta_override
    client = TestClient(app)

    response = client.get(f"/registro/inscripciones/{aceptacion_context['inscripcion_id']}/detalle")

    assert response.status_code == 403
