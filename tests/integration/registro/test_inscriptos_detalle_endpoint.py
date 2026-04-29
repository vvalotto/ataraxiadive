from __future__ import annotations

from datetime import date
from decimal import Decimal
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app import app
from competencia.domain.value_objects.disciplina import Disciplina
from identidad.api.dependencies import get_current_user
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)


@pytest.fixture
def inscriptos_detalle_context(tmp_path, monkeypatch):
    registro_db = tmp_path / "registro.db"
    monkeypatch.setenv("REGISTRO_DB_PATH", str(registro_db))

    torneo_id = uuid4()
    ana_id = uuid4()
    carlos_id = uuid4()
    pepe_id = uuid4()

    atleta_repo = SQLiteAtletaRepository(str(registro_db))
    inscripcion_repo = SQLiteInscripcionRepository(str(registro_db))

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=ana_id,
                nombre="Ana",
                apellido="Garcia",
                email="ana@email.com",
                fecha_nacimiento=date(1994, 5, 10),
                categoria=Categoria.SENIOR_FEMENINO,
                club="Azul",
            )
        )
        await atleta_repo.save(
            Atleta(
                atleta_id=carlos_id,
                nombre="Carlos",
                apellido="Lopez",
                email="carlos@email.com",
                fecha_nacimiento=date(1991, 8, 20),
                categoria=Categoria.SENIOR_MASCULINO,
                club="Rojo",
            )
        )
        await atleta_repo.save(
            Atleta(
                atleta_id=pepe_id,
                nombre="Pepe",
                apellido="Suarez",
                email="pepe@email.com",
                fecha_nacimiento=date(1990, 2, 15),
                categoria=Categoria.SENIOR_MASCULINO,
                club="Verde",
            )
        )

        ana_inscripcion = Inscripcion(
            atleta_id=ana_id,
            torneo_id=torneo_id,
            disciplinas=frozenset({Disciplina.DNF}),
        )
        ana_inscripcion.declarar_ap(Disciplina.DNF, Decimal("72"))
        await inscripcion_repo.save(ana_inscripcion)
        await inscripcion_repo.save(
            Inscripcion(
                atleta_id=carlos_id,
                torneo_id=torneo_id,
                disciplinas=frozenset({Disciplina.DYN}),
            )
        )
        await inscripcion_repo.save(
            Inscripcion(
                atleta_id=pepe_id,
                torneo_id=torneo_id,
                disciplinas=frozenset({Disciplina.DNF}),
                estado=EstadoInscripcion.CANCELADA,
            )
        )

    import asyncio

    asyncio.run(_seed())

    yield {
        "torneo_id": torneo_id,
    }

    app.dependency_overrides.clear()


def test_get_inscriptos_detalle_devuelve_activos_y_ap_por_disciplina(
    inscriptos_detalle_context,
) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "orga@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }
    client = TestClient(app)

    response = client.get(
        f"/registro/torneos/{inscriptos_detalle_context['torneo_id']}/inscriptos-detalle"
    )

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    assert [item["apellido"] for item in payload] == ["Garcia", "Lopez"]

    ana = next(item for item in payload if item["apellido"] == "Garcia")
    carlos = next(item for item in payload if item["apellido"] == "Lopez")

    assert ana["club"] == "Azul"
    assert ana["categoria"] == "SENIOR_FEMENINO"
    assert ana["disciplinas"] == [
        {
            "disciplina": "DNF",
            "ap": "72",
            "unidad": "Metros",
        }
    ]

    assert carlos["club"] == "Rojo"
    assert carlos["categoria"] == "SENIOR_MASCULINO"
    assert carlos["disciplinas"] == [
        {
            "disciplina": "DYN",
            "ap": None,
            "unidad": None,
        }
    ]


def test_get_inscriptos_detalle_rechaza_rol_atleta(inscriptos_detalle_context) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "atleta@ataraxiadive.io",
        "rol": "ATLETA",
    }
    client = TestClient(app)

    response = client.get(
        f"/registro/torneos/{inscriptos_detalle_context['torneo_id']}/inscriptos-detalle"
    )

    assert response.status_code == 403


def test_put_ap_inscripcion_actualiza_fuente_primaria(inscriptos_detalle_context) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "orga@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }
    client = TestClient(app)

    detalle_response = client.get(
        f"/registro/torneos/{inscriptos_detalle_context['torneo_id']}/inscriptos-detalle"
    )
    inscripcion_carlos = next(
        item["inscripcion_id"] for item in detalle_response.json() if item["apellido"] == "Lopez"
    )

    put_response = client.put(
        f"/registro/inscripciones/{inscripcion_carlos}/ap",
        json={"disciplina": "DYN", "valor_ap": "88"},
    )

    assert put_response.status_code == 200
    assert put_response.json()["ap"] == "88"
    assert put_response.json()["unidad"] == "Metros"
