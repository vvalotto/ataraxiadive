"""Step definitions BDD — US-3.2.3: BC Registro Inscripcion."""

from __future__ import annotations

from datetime import date, timedelta
from typing import Any
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

scenarios("../US-3.2.3-inscripcion-atleta.feature")


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "registro_test.db")
    torneo_db_path = str(tmp_path / "torneo_test.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", db_path)
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db_path)
    monkeypatch.setenv("IDENTIDAD_DB_PATH", str(tmp_path / "identidad_test.db"))
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-bdd-32-chars-minimum!!")
    return {"torneo_db_path": torneo_db_path}


@pytest.fixture
def client(context: dict[str, Any]) -> TestClient:
    import importlib
    import app as app_module

    importlib.reload(app_module)
    from app import app as fastapi_app
    from identidad.api.dependencies import get_current_user

    fastapi_app.dependency_overrides[get_current_user] = lambda: {
        "sub": "test-user",
        "email": "test@test.com",
        "rol": "ADMIN",
    }
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


def _seed_torneo(torneo_db_path: str, torneo_id: str, estado: str, fecha_inicio: str) -> None:
    """Inserta un torneo directamente en torneo.db para los tests BDD."""
    import sqlite3

    conn = sqlite3.connect(torneo_db_path)
    conn.execute("""CREATE TABLE IF NOT EXISTS torneos (
            torneo_id TEXT PRIMARY KEY, nombre TEXT, descripcion TEXT,
            fecha_inicio TEXT, fecha_fin TEXT, sede TEXT, entidad TEXT, estado TEXT
        )""")
    conn.execute(
        "INSERT OR REPLACE INTO torneos VALUES (?,?,?,?,?,?,?,?)",
        (
            torneo_id,
            "Torneo Test",
            "desc",
            fecha_inicio,
            "2026-12-31",
            "Mar del Plata",
            "Club Test",
            estado,
        ),
    )
    conn.commit()
    conn.close()


# ── Given ─────────────────────────────────────────────────────────────────────


@given("atleta registrado y torneo en estado INSCRIPCION_ABIERTA con disciplinas STA y DNF")
def given_atleta_y_torneo_abierto(context: dict[str, Any], client: TestClient) -> None:
    atleta_id = str(uuid4())
    torneo_id = str(uuid4())
    context["atleta_id"] = atleta_id
    context["torneo_id"] = torneo_id
    client.post(
        "/registro/atletas",
        json={
            "atleta_id": atleta_id,
            "nombre": "Ana",
            "apellido": "Lopez",
            "email": "ana@test.com",
            "fecha_nacimiento": "1990-01-01",
            "categoria": "SENIOR_FEMENINO",
        },
    )
    _seed_torneo(context["torneo_db_path"], torneo_id, "INSCRIPCION_ABIERTA", "2026-12-01")


@given("torneo en estado CREADO no INSCRIPCION_ABIERTA")
def given_torneo_cerrado(context: dict[str, Any], client: TestClient) -> None:
    torneo_id = str(uuid4())
    context["atleta_id"] = str(uuid4())
    context["torneo_id"] = torneo_id
    _seed_torneo(context["torneo_db_path"], torneo_id, "CREADO", "2026-12-01")


@given("torneo con disciplinas STA y DNF")
def given_torneo_con_disciplinas(context: dict[str, Any], client: TestClient) -> None:
    torneo_id = str(uuid4())
    context["atleta_id"] = str(uuid4())
    context["torneo_id"] = torneo_id
    # ACL retorna todas las disciplinas hasta US-3.4.1; simular disciplinas restringidas via mock
    _seed_torneo(context["torneo_db_path"], torneo_id, "INSCRIPCION_ABIERTA", "2026-12-01")
    context["disciplinas_restringidas"] = True


@given("atleta ya inscripto en el torneo")
def given_atleta_ya_inscripto(context: dict[str, Any], client: TestClient) -> None:
    atleta_id = str(uuid4())
    torneo_id = str(uuid4())
    context["atleta_id"] = atleta_id
    context["torneo_id"] = torneo_id
    client.post(
        "/registro/atletas",
        json={
            "atleta_id": atleta_id,
            "nombre": "Carlos",
            "apellido": "Ruiz",
            "email": "carlos@test.com",
            "fecha_nacimiento": "1985-05-20",
            "categoria": "SENIOR_MASCULINO",
        },
    )
    _seed_torneo(context["torneo_db_path"], torneo_id, "INSCRIPCION_ABIERTA", "2026-12-01")
    resp = client.post(
        "/registro/inscripciones",
        json={"atleta_id": atleta_id, "torneo_id": torneo_id, "disciplinas": ["STA"]},
    )
    assert resp.status_code == 201


@given("inscripcion ACTIVA y fecha inicio del torneo es maniana")
def given_inscripcion_activa_maniana(context: dict[str, Any], client: TestClient) -> None:
    atleta_id = str(uuid4())
    torneo_id = str(uuid4())
    maniana = (date.today() + timedelta(days=1)).isoformat()
    context["atleta_id"] = atleta_id
    context["torneo_id"] = torneo_id
    _seed_torneo(context["torneo_db_path"], torneo_id, "INSCRIPCION_ABIERTA", maniana)
    client.post(
        "/registro/atletas",
        json={
            "atleta_id": atleta_id,
            "nombre": "Pedro",
            "apellido": "Mora",
            "email": "pedro@test.com",
            "fecha_nacimiento": "1992-03-15",
            "categoria": "SENIOR_MASCULINO",
        },
    )
    resp = client.post(
        "/registro/inscripciones",
        json={"atleta_id": atleta_id, "torneo_id": torneo_id, "disciplinas": ["STA"]},
    )
    assert resp.status_code == 201
    context["inscripcion_id"] = resp.json()["inscripcion_id"]


@given("inscripcion ACTIVA y fecha inicio del torneo es hoy")
def given_inscripcion_activa_hoy(context: dict[str, Any], client: TestClient) -> None:
    atleta_id = str(uuid4())
    torneo_id = str(uuid4())
    hoy = date.today().isoformat()
    context["atleta_id"] = atleta_id
    context["torneo_id"] = torneo_id
    _seed_torneo(context["torneo_db_path"], torneo_id, "INSCRIPCION_ABIERTA", hoy)
    client.post(
        "/registro/atletas",
        json={
            "atleta_id": atleta_id,
            "nombre": "Laura",
            "apellido": "Vega",
            "email": "laura@test.com",
            "fecha_nacimiento": "1995-07-10",
            "categoria": "SENIOR_FEMENINO",
        },
    )
    resp = client.post(
        "/registro/inscripciones",
        json={"atleta_id": atleta_id, "torneo_id": torneo_id, "disciplinas": ["STA"]},
    )
    assert resp.status_code == 201
    context["inscripcion_id"] = resp.json()["inscripcion_id"]


@given("3 atletas inscriptos en un torneo")
def given_tres_inscriptos(context: dict[str, Any], client: TestClient) -> None:
    torneo_id = str(uuid4())
    context["torneo_id"] = torneo_id
    _seed_torneo(context["torneo_db_path"], torneo_id, "INSCRIPCION_ABIERTA", "2026-12-01")
    for i in range(3):
        atleta_id = str(uuid4())
        client.post(
            "/registro/atletas",
            json={
                "atleta_id": atleta_id,
                "nombre": f"Atleta{i}",
                "apellido": "Test",
                "email": f"atleta{i}@test.com",
                "fecha_nacimiento": "1990-01-01",
                "categoria": "SENIOR_MASCULINO",
            },
        )
        resp = client.post(
            "/registro/inscripciones",
            json={"atleta_id": atleta_id, "torneo_id": torneo_id, "disciplinas": ["STA"]},
        )
        assert resp.status_code == 201


# ── When ──────────────────────────────────────────────────────────────────────


@when("POST /registro/inscripciones con atleta_id, torneo_id y disciplinas STA")
def when_inscribir_atleta(context: dict[str, Any], client: TestClient) -> None:
    resp = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": context["atleta_id"],
            "torneo_id": context["torneo_id"],
            "disciplinas": ["STA"],
        },
    )
    context["response"] = resp


@when("POST /registro/inscripciones con atleta_id y torneo_id")
def when_inscribir_torneo_no_disponible(context: dict[str, Any], client: TestClient) -> None:
    resp = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": context["atleta_id"],
            "torneo_id": context["torneo_id"],
            "disciplinas": ["STA"],
        },
    )
    context["response"] = resp


@when("POST /registro/inscripciones con disciplinas DYN")
def when_inscribir_disciplina_no_disponible(context: dict[str, Any], client: TestClient) -> None:
    from registro.infrastructure.acl.sqlite_torneo_consulta import SQLiteTorneoConsulta
    from shared.domain.value_objects.disciplina import Disciplina

    # Mockear obtener_disciplinas para simular torneo con solo STA/DNF
    original = SQLiteTorneoConsulta.obtener_disciplinas

    async def _mock_disciplinas(self, torneo_id):
        return frozenset({Disciplina.STA, Disciplina.DNF})

    SQLiteTorneoConsulta.obtener_disciplinas = _mock_disciplinas
    resp = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": context["atleta_id"],
            "torneo_id": context["torneo_id"],
            "disciplinas": ["DYN"],
        },
    )
    SQLiteTorneoConsulta.obtener_disciplinas = original
    context["response"] = resp


@when("POST /registro/inscripciones con mismo atleta_id y torneo_id")
def when_inscribir_duplicado(context: dict[str, Any], client: TestClient) -> None:
    resp = client.post(
        "/registro/inscripciones",
        json={
            "atleta_id": context["atleta_id"],
            "torneo_id": context["torneo_id"],
            "disciplinas": ["STA"],
        },
    )
    context["response"] = resp


@when("DELETE /registro/inscripciones/{inscripcion_id}")
def when_cancelar_inscripcion(context: dict[str, Any], client: TestClient) -> None:
    resp = client.delete(f"/registro/inscripciones/{context['inscripcion_id']}")
    context["response"] = resp


@when("GET /registro/torneos/{torneo_id}/inscriptos")
def when_listar_inscriptos(context: dict[str, Any], client: TestClient) -> None:
    resp = client.get(f"/registro/torneos/{context['torneo_id']}/inscriptos")
    context["response"] = resp


# ── Then ──────────────────────────────────────────────────────────────────────


@then("201 con inscripcion_id")
def then_201_con_inscripcion_id(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 201
    assert "inscripcion_id" in context["response"].json()
    context["inscripcion_id"] = context["response"].json()["inscripcion_id"]


@then("GET /registro/torneos/{torneo_id}/inscriptos incluye al atleta")
def then_inscriptos_incluye_atleta(context: dict[str, Any], client: TestClient) -> None:
    resp = client.get(f"/registro/torneos/{context['torneo_id']}/inscriptos")
    assert resp.status_code == 200
    atletas = [i["atleta_id"] for i in resp.json()]
    assert context["atleta_id"] in atletas


@then("409 Conflict con detalle TorneoNoDisponible")
def then_409_torneo_no_disponible(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 409
    assert (
        "TorneoNoDisponible" in context["response"].json()["detail"]
        or "inscripción" in context["response"].json()["detail"]
    )


@then("409 Conflict con detalle DisciplinaNoDisponible")
def then_409_disciplina_no_disponible(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 409
    assert (
        "DisciplinaNoDisponible" in context["response"].json()["detail"]
        or "no disponibles" in context["response"].json()["detail"]
    )


@then("409 Conflict con detalle AtletaYaInscripto")
def then_409_atleta_ya_inscripto(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 409
    assert "inscripto" in context["response"].json()["detail"].lower()


@then("200 y la inscripcion queda en estado CANCELADA")
def then_200_cancelada(context: dict[str, Any], client: TestClient) -> None:
    assert context["response"].status_code == 200
    resp = client.get(f"/registro/torneos/{context['torneo_id']}/inscriptos")
    inscripciones = resp.json()
    match = next(
        (i for i in inscripciones if i["inscripcion_id"] == context["inscripcion_id"]), None
    )
    assert match is not None
    assert match["estado"] == "CANCELADA"


@then("409 Conflict con detalle PlazoCancelacionVencido")
def then_409_plazo_vencido(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 409
    assert "cancelar" in context["response"].json()["detail"].lower()


@then("200 con lista de 3 inscripciones ACTIVAS")
def then_200_lista_3_activas(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 200
    inscripciones = context["response"].json()
    assert len(inscripciones) == 3
    assert all(i["estado"] == "ACTIVA" for i in inscripciones)
