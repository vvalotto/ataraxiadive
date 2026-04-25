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
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

scenarios("../US-5.5.2-vista-organizador-inscriptos.feature")


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    registro_db = str(tmp_path / "registro.db")
    torneo_db = str(tmp_path / "torneo.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", registro_db)
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)

    organizador_id = uuid4()
    torneo_id = uuid4()

    return {
        "registro_db": registro_db,
        "torneo_db": torneo_db,
        "torneo_id": torneo_id,
        "torneo_vacio_id": None,
        "organizador_id": organizador_id,
        "atleta1_id": uuid4(),
        "atleta2_id": uuid4(),
        "atleta_cancelado_id": uuid4(),
        "response": None,
    }


@pytest.fixture
def client() -> TestClient:
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── Background ────────────────────────────────────────────────────────────────


@given('el torneo "BA Open 2026" tiene inscriptos activos con datos completos')
def torneo_con_inscriptos(context: dict[str, Any]) -> None:
    atleta_repo = SQLiteAtletaRepository(context["registro_db"])
    torneo_repo = SQLiteTorneoRepository(context["torneo_db"])
    torneo_id = context["torneo_id"]

    async def _seed() -> None:
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

    asyncio.run(_seed())


@given('la atleta "ana@email.com" esta inscripta en DNF y STA con nombre "Garcia, Ana"')
def atleta_ana_inscripta(context: dict[str, Any]) -> None:
    atleta_repo = SQLiteAtletaRepository(context["registro_db"])
    inscripcion_repo = SQLiteInscripcionRepository(context["registro_db"])
    atleta1_id = context["atleta1_id"]

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=atleta1_id,
                nombre="Ana",
                apellido="Garcia",
                email="ana@email.com",
                fecha_nacimiento=date(1990, 5, 15),
                categoria=Categoria.SENIOR_FEMENINO,
                club="Club Aqua",
            )
        )
        await inscripcion_repo.save(
            Inscripcion(
                atleta_id=atleta1_id,
                torneo_id=context["torneo_id"],
                disciplinas=frozenset([Disciplina.DNF, Disciplina.STA]),
            )
        )

    asyncio.run(_seed())


@given('el atleta "carlos@email.com" esta inscripto en DYN con nombre "Lopez, Carlos"')
def atleta_carlos_inscripto(context: dict[str, Any]) -> None:
    atleta_repo = SQLiteAtletaRepository(context["registro_db"])
    inscripcion_repo = SQLiteInscripcionRepository(context["registro_db"])
    atleta2_id = context["atleta2_id"]

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=atleta2_id,
                nombre="Carlos",
                apellido="Lopez",
                email="carlos@email.com",
                fecha_nacimiento=date(1985, 3, 10),
                categoria=Categoria.MASTER_MASCULINO,
                club="Club Mar",
            )
        )
        await inscripcion_repo.save(
            Inscripcion(
                atleta_id=atleta2_id,
                torneo_id=context["torneo_id"],
                disciplinas=frozenset([Disciplina.DYN]),
            )
        )

    asyncio.run(_seed())


@given('existe una inscripcion CANCELADA de "pepe@email.com"')
def inscripcion_cancelada(context: dict[str, Any]) -> None:
    atleta_repo = SQLiteAtletaRepository(context["registro_db"])
    inscripcion_repo = SQLiteInscripcionRepository(context["registro_db"])
    cancelado_id = context["atleta_cancelado_id"]

    async def _seed() -> None:
        await atleta_repo.save(
            Atleta(
                atleta_id=cancelado_id,
                nombre="Pepe",
                apellido="Gomez",
                email="pepe@email.com",
                fecha_nacimiento=date(1988, 1, 1),
                categoria=Categoria.SENIOR_MASCULINO,
                club="Club X",
            )
        )
        insc = Inscripcion(
            atleta_id=cancelado_id,
            torneo_id=context["torneo_id"],
            disciplinas=frozenset([Disciplina.DNF]),
        )
        insc.estado = EstadoInscripcion.CANCELADA
        await inscripcion_repo.save(insc)

    asyncio.run(_seed())


# ── Scenario: torneo vacío ─────────────────────────────────────────────────────


@given('existe el torneo "Torneo Vacio" sin inscriptos activos')
def torneo_vacio(context: dict[str, Any]) -> None:
    torneo_repo = SQLiteTorneoRepository(context["torneo_db"])
    torneo_vacio_id = uuid4()
    context["torneo_vacio_id"] = torneo_vacio_id

    async def _seed() -> None:
        torneo = Torneo(
            torneo_id=torneo_vacio_id,
            nombre="Torneo Vacio",
            descripcion="Sin inscriptos",
            fecha_inicio=date(2026, 6, 1),
            fecha_fin=date(2026, 6, 2),
            sede=Sede(nombre="Club", ciudad="BA", pais="Argentina"),
            entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
        )
        torneo.abrir_inscripcion()
        await torneo_repo.save(torneo)

    asyncio.run(_seed())


# ── Auth steps ────────────────────────────────────────────────────────────────


@given("el organizador esta autenticado")
def organizador_autenticado(client: TestClient, context: dict[str, Any]) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(context["organizador_id"]),
        "email": "org@ataraxiadive.io",
        "rol": "ORGANIZADOR",
    }


@given("el usuario esta autenticado con rol ATLETA")
def usuario_rol_atleta(client: TestClient) -> None:
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(uuid4()),
        "email": "atleta@example.com",
        "rol": "ATLETA",
    }


# ── When steps ────────────────────────────────────────────────────────────────


@when("realiza GET /registro/torneos/{id}/inscriptos-detalle")
def get_inscriptos_detalle(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.get(f"/registro/torneos/{context['torneo_id']}/inscriptos-detalle")


@when("el organizador realiza GET /registro/torneos/{id-vacio}/inscriptos-detalle")
def get_inscriptos_detalle_vacio(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.get(
        f"/registro/torneos/{context['torneo_vacio_id']}/inscriptos-detalle"
    )


# ── Then steps ────────────────────────────────────────────────────────────────


@then(parsers.parse("el sistema responde {codigo:d}"))
def sistema_responde(context: dict[str, Any], codigo: int) -> None:
    assert context["response"].status_code == codigo


@then('la respuesta contiene a "Garcia" con disciplinas DNF y STA')
def contiene_garcia(context: dict[str, Any]) -> None:
    data = context["response"].json()
    garcia = next((d for d in data if d["apellido"] == "Garcia"), None)
    assert garcia is not None
    assert set(garcia["disciplinas"]) == {"DNF", "STA"}


@then('la respuesta contiene a "Lopez" con disciplinas DYN')
def contiene_lopez(context: dict[str, Any]) -> None:
    data = context["response"].json()
    lopez = next((d for d in data if d["apellido"] == "Lopez"), None)
    assert lopez is not None
    assert set(lopez["disciplinas"]) == {"DYN"}


@then("la respuesta no contiene la inscripcion CANCELADA")
def no_contiene_cancelada(context: dict[str, Any]) -> None:
    data = context["response"].json()
    ids = [d["atleta_id"] for d in data]
    assert str(context["atleta_cancelado_id"]) not in ids


@then("la respuesta no incluye inscripciones con estado CANCELADA")
def no_incluye_canceladas(context: dict[str, Any]) -> None:
    data = context["response"].json()
    estados = [d["estado"] for d in data]
    assert "CANCELADA" not in estados


@then("la respuesta es una lista vacia")
def lista_vacia(context: dict[str, Any]) -> None:
    assert context["response"].json() == []
