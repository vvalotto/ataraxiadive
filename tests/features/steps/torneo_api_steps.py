"""Step definitions BDD — US-3.1.2: API REST Torneo — CRUD + transiciones de fase."""

from __future__ import annotations

import tempfile
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../US-3.1.2-api-rest-torneo.feature")


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "torneo_test.db")
    monkeypatch.setenv("TORNEO_DB_PATH", db_path)
    return {"db_path": db_path}


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
        "rol": "ORGANIZADOR",
    }
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


def _payload(**overrides: Any) -> dict[str, Any]:
    base: dict[str, Any] = {
        "nombre": "Open Nacional 2026",
        "descripcion": "Torneo de apnea nacional",
        "fecha_inicio": "2026-06-01",
        "fecha_fin": "2026-06-03",
        "sede": {"nombre": "Piscina Municipal", "ciudad": "Buenos Aires", "pais": "Argentina"},
        "entidad_organizadora": {"nombre": "AIDA Argentina", "tipo": "FEDERACION"},
    }
    base.update(overrides)
    return base


# ── Background ────────────────────────────────────────────────────────────────


@given("la base de datos de torneos está limpia")
def base_datos_limpia(context: dict[str, Any]) -> None:
    pass  # tmp_path garantiza DB nueva por test


# ── Scenario: crear torneo exitosamente ──────────────────────────────────────


@given("un payload válido con nombre, fechas, sede y entidad organizadora")
def payload_valido(context: dict[str, Any]) -> None:
    context["payload"] = _payload()


@when("POST /torneos con el payload")
def post_torneos(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.post("/torneos", json=context["payload"])


@then("la respuesta es 201 con torneo_id")
def respuesta_201(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 201
    assert "torneo_id" in context["response"].json()
    context["torneo_id"] = context["response"].json()["torneo_id"]


@then("GET /torneos/{torneo_id} retorna el torneo con estado CREADO")
def get_torneo_estado_creado(client: TestClient, context: dict[str, Any]) -> None:
    r = client.get(f"/torneos/{context['torneo_id']}")
    assert r.status_code == 200
    assert r.json()["estado"] == "CREADO"


# ── Scenario: crear torneo con fecha_fin anterior a fecha_inicio ──────────────


@given("un payload con fecha_fin anterior a fecha_inicio")
def payload_fechas_invalidas(context: dict[str, Any]) -> None:
    context["payload"] = _payload(fecha_inicio="2026-06-10", fecha_fin="2026-06-01")


@then("la respuesta es 422 Unprocessable Entity")
def respuesta_422(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 422


# ── Scenario: crear torneo con nombre vacío ───────────────────────────────────


@given("un payload con nombre vacío")
def payload_nombre_vacio(context: dict[str, Any]) -> None:
    context["payload"] = _payload(nombre="")


# ── Scenario: ciclo completo de transiciones ─────────────────────────────────


@given("un torneo creado con estado CREADO")
def torneo_creado(client: TestClient, context: dict[str, Any]) -> None:
    r = client.post("/torneos", json=_payload())
    assert r.status_code == 201
    context["torneo_id"] = r.json()["torneo_id"]
    context["transicion_responses"] = []


@when(parsers.parse("se ejecutan secuencialmente las transiciones {transiciones}"))
def ejecutar_transiciones(client: TestClient, context: dict[str, Any], transiciones: str) -> None:
    nombres = [t.strip() for t in transiciones.split(",")]
    for nombre in nombres:
        r = client.put(f"/torneos/{context['torneo_id']}/{nombre}")
        context["transicion_responses"].append(r)


@then("cada transición retorna 200")
def cada_200(context: dict[str, Any]) -> None:
    for r in context["transicion_responses"]:
        assert r.status_code == 200, f"Esperado 200, obtenido {r.status_code}: {r.text}"


@then(parsers.parse("el estado final del torneo es {estado}"))
def estado_final(client: TestClient, context: dict[str, Any], estado: str) -> None:
    r = client.get(f"/torneos/{context['torneo_id']}")
    assert r.json()["estado"] == estado


# ── Scenario: retroceso ejecución → preparación ───────────────────────────────


@given("un torneo en estado EJECUCION")
def torneo_en_ejecucion(client: TestClient, context: dict[str, Any]) -> None:
    r = client.post("/torneos", json=_payload())
    tid = r.json()["torneo_id"]
    context["torneo_id"] = tid
    for endpoint in ("abrir-inscripcion", "cerrar-inscripcion", "iniciar-ejecucion"):
        client.put(f"/torneos/{tid}/{endpoint}")


@when("PUT /torneos/{torneo_id}/volver-preparacion")
def put_volver_preparacion(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.put(f"/torneos/{context['torneo_id']}/volver-preparacion")


@then("la respuesta es 200")
def respuesta_200(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 200


@then(parsers.parse("el estado del torneo es {estado}"))
def estado_del_torneo(client: TestClient, context: dict[str, Any], estado: str) -> None:
    r = client.get(f"/torneos/{context['torneo_id']}")
    assert r.json()["estado"] == estado


# ── Scenario: transición inválida ─────────────────────────────────────────────


@when("PUT /torneos/{torneo_id}/iniciar-ejecucion")
def put_iniciar_ejecucion(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.put(f"/torneos/{context['torneo_id']}/iniciar-ejecucion")


@then("la respuesta es 409 Conflict")
def respuesta_409(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 409


@then("el mensaje de error describe la transición inválida")
def mensaje_transicion(context: dict[str, Any]) -> None:
    body = context["response"].json()
    assert "detail" in body
    assert len(body["detail"]) > 0


# ── Scenario: cancelar torneo ─────────────────────────────────────────────────


@given("un torneo en estado INSCRIPCION_ABIERTA")
def torneo_inscripcion_abierta(client: TestClient, context: dict[str, Any]) -> None:
    r = client.post("/torneos", json=_payload())
    tid = r.json()["torneo_id"]
    context["torneo_id"] = tid
    client.put(f"/torneos/{tid}/abrir-inscripcion")


@when("PUT /torneos/{torneo_id}/cancelar")
def put_cancelar(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.put(f"/torneos/{context['torneo_id']}/cancelar")


# ── Scenario: torneo inexistente ──────────────────────────────────────────────


@given("un UUID que no existe en la base de datos")
def uuid_inexistente(context: dict[str, Any]) -> None:
    context["uuid"] = str(uuid4())


@when("GET /torneos/{uuid}")
def get_torneo_inexistente(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.get(f"/torneos/{context['uuid']}")


@then("la respuesta es 404 Not Found")
def respuesta_404(context: dict[str, Any]) -> None:
    assert context["response"].status_code == 404


# ── Scenario: listar torneos ──────────────────────────────────────────────────


@given("3 torneos creados")
def tres_torneos_creados(client: TestClient, context: dict[str, Any]) -> None:
    for i in range(3):
        r = client.post("/torneos", json=_payload(nombre=f"Torneo {i + 1}"))
        assert r.status_code == 201


@when("GET /torneos")
def get_torneos(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.get("/torneos")


@then(parsers.parse("la respuesta es 200 con lista de {n:d} torneos"))
def respuesta_lista(context: dict[str, Any], n: int) -> None:
    assert context["response"].status_code == 200
    assert len(context["response"].json()) == n


# ── Scenario: respuesta completa ──────────────────────────────────────────────


@given("un torneo creado con todos sus campos")
def torneo_campos_completos(client: TestClient, context: dict[str, Any]) -> None:
    r = client.post("/torneos", json=_payload())
    assert r.status_code == 201
    context["torneo_id"] = r.json()["torneo_id"]


@when("GET /torneos/{torneo_id}")
def get_torneo_campos(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.get(f"/torneos/{context['torneo_id']}")


@then(
    "la respuesta contiene torneo_id, nombre, descripcion, fechas, sede, entidad_organizadora y estado"
)
def respuesta_campos_completos(context: dict[str, Any]) -> None:
    data = context["response"].json()
    assert context["response"].status_code == 200
    for field in (
        "torneo_id",
        "nombre",
        "descripcion",
        "fecha_inicio",
        "fecha_fin",
        "sede",
        "entidad_organizadora",
        "estado",
    ):
        assert field in data, f"Falta campo: {field}"
    assert "ciudad" in data["sede"]
    assert "tipo" in data["entidad_organizadora"]
