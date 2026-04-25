from __future__ import annotations

import asyncio
from datetime import date
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import app
from identidad.api.dependencies import get_current_user
from registro.domain.aggregates.atleta import Atleta
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


def _atleta(atleta_id=None, apellido="García", nombre="Ana", email=None) -> Atleta:
    return Atleta(
        atleta_id=atleta_id or uuid4(),
        nombre=nombre,
        apellido=apellido,
        email=email or f"{apellido.lower()}@example.com",
        fecha_nacimiento=date(1990, 5, 15),
        categoria=Categoria.SENIOR_FEMENINO,
        club="Club Aqua",
    )


@pytest.fixture
def inscriptos_context(tmp_path, monkeypatch):
    registro_db = str(tmp_path / "registro.db")
    torneo_db = str(tmp_path / "torneo.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", registro_db)
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)

    organizador_id = uuid4()
    atleta1_id = uuid4()
    atleta2_id = uuid4()
    atleta_cancelado_id = uuid4()
    torneo_id = uuid4()
    torneo_vacio_id = uuid4()

    atleta_repo = SQLiteAtletaRepository(registro_db)
    inscripcion_repo = SQLiteInscripcionRepository(registro_db)
    torneo_repo = SQLiteTorneoRepository(torneo_db)

    async def _seed() -> None:
        # Atletas
        await atleta_repo.save(
            _atleta(atleta_id=atleta1_id, apellido="Garcia", nombre="Ana", email="ana@example.com")
        )
        await atleta_repo.save(
            _atleta(
                atleta_id=atleta2_id, apellido="Lopez", nombre="Carlos", email="carlos@example.com"
            )
        )
        await atleta_repo.save(
            _atleta(
                atleta_id=atleta_cancelado_id,
                apellido="Pepe",
                nombre="Pepe",
                email="pepe@example.com",
            )
        )

        # Torneo principal
        torneo = Torneo(
            torneo_id=torneo_id,
            nombre="BA Open 2026",
            descripcion="Torneo test",
            fecha_inicio=date(2026, 5, 15),
            fecha_fin=date(2026, 5, 16),
            sede=Sede(nombre="Club Nautico", ciudad="Buenos Aires", pais="Argentina"),
            entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
        )
        torneo.abrir_inscripcion()
        await torneo_repo.save(torneo)

        # Torneo vacío
        torneo_vacio = Torneo(
            torneo_id=torneo_vacio_id,
            nombre="Torneo Vacío",
            descripcion="Sin inscriptos",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 2),
            sede=Sede(nombre="Club", ciudad="BA", pais="Argentina"),
            entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
        )
        torneo_vacio.abrir_inscripcion()
        await torneo_repo.save(torneo_vacio)

        # Inscripciones ACTIVAS
        await inscripcion_repo.save(
            Inscripcion(
                atleta_id=atleta1_id,
                torneo_id=torneo_id,
                disciplinas=frozenset([Disciplina.DNF, Disciplina.STA]),
            )
        )
        await inscripcion_repo.save(
            Inscripcion(
                atleta_id=atleta2_id, torneo_id=torneo_id, disciplinas=frozenset([Disciplina.DYN])
            )
        )

        # Inscripción CANCELADA
        insc_cancelada = Inscripcion(
            atleta_id=atleta_cancelado_id,
            torneo_id=torneo_id,
            disciplinas=frozenset([Disciplina.DNF]),
        )
        insc_cancelada.estado = EstadoInscripcion.CANCELADA
        await inscripcion_repo.save(insc_cancelada)

    asyncio.run(_seed())

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(organizador_id),
        "email": "org@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }

    yield {
        "torneo_id": torneo_id,
        "torneo_vacio_id": torneo_vacio_id,
        "atleta1_id": atleta1_id,
        "atleta2_id": atleta2_id,
        "atleta_cancelado_id": atleta_cancelado_id,
        "organizador_id": organizador_id,
    }

    app.dependency_overrides.clear()


def test_organizador_obtiene_inscriptos_detalle(inscriptos_context):
    client = TestClient(app)
    torneo_id = inscriptos_context["torneo_id"]

    response = client.get(f"/registro/torneos/{torneo_id}/inscriptos-detalle")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    apellidos = {d["apellido"] for d in data}
    assert "Garcia" in apellidos
    assert "Lopez" in apellidos
    # Pepe (CANCELADA) no aparece
    assert "Pepe" not in apellidos


def test_respuesta_contiene_datos_atleta_completos(inscriptos_context):
    client = TestClient(app)
    torneo_id = inscriptos_context["torneo_id"]

    response = client.get(f"/registro/torneos/{torneo_id}/inscriptos-detalle")

    assert response.status_code == 200
    garcia = next(d for d in response.json() if d["apellido"] == "Garcia")
    assert garcia["nombre"] == "Ana"
    assert garcia["club"] == "Club Aqua"
    assert garcia["categoria"] == Categoria.SENIOR_FEMENINO.value
    assert set(garcia["disciplinas"]) == {"DNF", "STA"}
    assert garcia["estado"] == "ACTIVA"


def test_inscripciones_canceladas_no_aparecen(inscriptos_context):
    client = TestClient(app)
    torneo_id = inscriptos_context["torneo_id"]

    response = client.get(f"/registro/torneos/{torneo_id}/inscriptos-detalle")

    assert response.status_code == 200
    atleta_cancelado_id = str(inscriptos_context["atleta_cancelado_id"])
    ids = [d["atleta_id"] for d in response.json()]
    assert atleta_cancelado_id not in ids


def test_torneo_sin_inscriptos_devuelve_lista_vacia(inscriptos_context):
    client = TestClient(app)
    torneo_vacio_id = inscriptos_context["torneo_vacio_id"]

    response = client.get(f"/registro/torneos/{torneo_vacio_id}/inscriptos-detalle")

    assert response.status_code == 200
    assert response.json() == []


def test_acceso_con_rol_atleta_es_rechazado(inscriptos_context):
    client = TestClient(app)
    torneo_id = inscriptos_context["torneo_id"]

    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "atleta@example.com",
        "rol": "ATLETA",
    }

    response = client.get(f"/registro/torneos/{torneo_id}/inscriptos-detalle")

    assert response.status_code == 403

    # Restaurar override de organizador
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(inscriptos_context["organizador_id"]),
        "email": "org@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }
