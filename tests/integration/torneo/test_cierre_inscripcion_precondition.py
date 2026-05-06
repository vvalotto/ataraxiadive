from __future__ import annotations

from collections.abc import Iterator
from datetime import date
from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user
from registro.api.router import build_cierre_inscripcion_precondition
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import configure_cierre_inscripcion_precondition, router


@pytest.fixture
def client(tmp_path: object, monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    torneo_db = str(tmp_path / "torneo.db")
    registro_db = str(tmp_path / "registro.db")
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)
    monkeypatch.setenv("REGISTRO_DB_PATH", registro_db)

    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ORGANIZADOR",
    }
    configure_cierre_inscripcion_precondition(build_cierre_inscripcion_precondition())
    yield TestClient(app)
    configure_cierre_inscripcion_precondition(None)
    app.dependency_overrides.clear()


def _crear_torneo_con_disciplina(client: TestClient) -> UUID:
    response = client.post(
        "/torneos",
        json={
            "nombre": "BA 2026",
            "descripcion": "Torneo",
            "fecha_inicio": "2026-06-01",
            "fecha_fin": "2026-06-03",
            "sede": {"nombre": "Piscina", "ciudad": "BA", "pais": "AR"},
            "entidad_organizadora": {"nombre": "AIDA", "tipo": "FEDERACION"},
            "grupos_etarios": ["SENIOR"],
        },
    )
    torneo_id = UUID(response.json()["torneo_id"])
    disciplinas_response = client.put(
        f"/torneos/{torneo_id}/disciplinas",
        json={"disciplinas": ["DNF"]},
    )
    assert disciplinas_response.status_code == 200
    assert client.put(f"/torneos/{torneo_id}/abrir-inscripcion").status_code == 200
    return torneo_id


async def _seed_inscripcion(registro_db: str, torneo_id: UUID, con_ap: bool) -> None:
    atleta_id = uuid4()
    atleta_repo = SQLiteAtletaRepository(registro_db)
    inscripcion_repo = SQLiteInscripcionRepository(registro_db)

    await atleta_repo.save(
        Atleta(
            atleta_id=atleta_id,
            nombre="Ana",
            apellido="Garcia",
            email="ana@email.com",
            fecha_nacimiento=date(1994, 5, 10),
            categoria=Categoria.SENIOR_FEMENINO,
            club="Azul",
        )
    )
    inscripcion = Inscripcion(
        atleta_id=atleta_id,
        torneo_id=torneo_id,
        disciplinas=frozenset({Disciplina.DNF}),
    )
    if con_ap:
        inscripcion.declarar_ap(Disciplina.DNF, Decimal("72"))
    await inscripcion_repo.save(inscripcion)


@pytest.mark.asyncio
async def test_cerrar_inscripcion_rechaza_si_falta_ap(client: TestClient) -> None:
    import os

    torneo_id = _crear_torneo_con_disciplina(client)
    await _seed_inscripcion(os.environ["REGISTRO_DB_PATH"], torneo_id, con_ap=False)

    response = client.put(f"/torneos/{torneo_id}/cerrar-inscripcion")

    assert response.status_code == 409
    assert "Faltan AP por completar" in response.json()["detail"]


@pytest.mark.asyncio
async def test_cerrar_inscripcion_permite_si_todos_tienen_ap(client: TestClient) -> None:
    import os

    torneo_id = _crear_torneo_con_disciplina(client)
    atleta_id = uuid4()
    atleta_repo = SQLiteAtletaRepository(os.environ["REGISTRO_DB_PATH"])
    inscripcion_repo = SQLiteInscripcionRepository(os.environ["REGISTRO_DB_PATH"])
    await atleta_repo.save(
        Atleta(
            atleta_id=atleta_id,
            nombre="Ana",
            apellido="Garcia",
            email="ana@email.com",
            fecha_nacimiento=date(1994, 5, 10),
            categoria=Categoria.SENIOR_FEMENINO,
            club="Azul",
        )
    )
    inscripcion = Inscripcion(
        atleta_id=atleta_id,
        torneo_id=torneo_id,
        disciplinas=frozenset({Disciplina.DNF}),
    )
    inscripcion.declarar_ap(Disciplina.DNF, Decimal("72"))
    await inscripcion_repo.save(inscripcion)

    response = client.put(f"/torneos/{torneo_id}/cerrar-inscripcion")

    assert response.status_code == 200
