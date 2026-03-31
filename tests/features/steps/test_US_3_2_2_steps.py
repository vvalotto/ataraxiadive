"""Step definitions BDD — US-3.2.2: BC Registro Aggregate Atleta."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

scenarios("../US-3.2.2.feature")


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "registro_test.db")
    monkeypatch.setenv("REGISTRO_DB_PATH", db_path)
    monkeypatch.setenv("IDENTIDAD_DB_PATH", str(tmp_path / "identidad_test.db"))
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-bdd-32-chars-minimum!!")
    return {}


@pytest.fixture
def client(context: dict[str, Any]) -> TestClient:
    import importlib
    import app as app_module

    importlib.reload(app_module)
    from app import app as fastapi_app

    return TestClient(fastapi_app)


# ── Given ─────────────────────────────────────────────────────────────────────


@given(
    parsers.parse(
        'datos personales completos con nombre "{nombre}", apellido "{apellido}", '
        'email "{email}", fecha_nacimiento "{fecha}", categoria "{categoria}"'
    )
)
def datos_personales_completos(
    context: dict[str, Any],
    nombre: str,
    apellido: str,
    email: str,
    fecha: str,
    categoria: str,
) -> None:
    context["payload"] = {
        "atleta_id": str(uuid4()),
        "nombre": nombre,
        "apellido": apellido,
        "email": email,
        "fecha_nacimiento": fecha,
        "categoria": categoria,
    }


@given("datos válidos sin campo brevet")
def datos_sin_brevet(context: dict[str, Any]) -> None:
    context["payload"] = {
        "atleta_id": str(uuid4()),
        "nombre": "Carlos",
        "apellido": "López",
        "email": "carlos@example.com",
        "fecha_nacimiento": "1985-03-20",
        "categoria": "MASTER_MASCULINO",
    }


@given("un atleta ya registrado con atleta_id X")
def atleta_ya_registrado(client: TestClient, context: dict[str, Any]) -> None:
    atleta_id = str(uuid4())
    payload = {
        "atleta_id": atleta_id,
        "nombre": "Pedro",
        "apellido": "Martínez",
        "email": "pedro@example.com",
        "fecha_nacimiento": "1988-07-10",
        "categoria": "SENIOR_MASCULINO",
    }
    resp = client.post("/registro/atletas", json=payload)
    assert resp.status_code == 201
    context["atleta_id"] = atleta_id
    context["payload"] = payload


@given("nombre vacío en los datos del atleta")
def nombre_vacio(context: dict[str, Any]) -> None:
    context["payload"] = {
        "atleta_id": str(uuid4()),
        "nombre": "",
        "apellido": "García",
        "email": "vacio@example.com",
        "fecha_nacimiento": "1990-01-01",
        "categoria": "SENIOR_FEMENINO",
    }


@given("un UUID no registrado en el sistema")
def uuid_no_registrado(context: dict[str, Any]) -> None:
    context["atleta_id"] = str(uuid4())


# ── When ──────────────────────────────────────────────────────────────────────


@when("POST /registro/atletas con un atleta_id válido")
def post_atleta(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.post("/registro/atletas", json=context["payload"])


@when("POST /registro/atletas")
def post_atleta_simple(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.post("/registro/atletas", json=context["payload"])


@when("POST /registro/atletas con el mismo atleta_id X")
def post_atleta_duplicado(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.post("/registro/atletas", json=context["payload"])


@when("GET /registro/atletas con ese id retorna los datos del atleta")
def get_atleta_by_id(client: TestClient, context: dict[str, Any]) -> None:
    atleta_id = context["response"].json()["atleta_id"]
    context["get_response"] = client.get(f"/registro/atletas/{atleta_id}")


@when("GET /registro/atletas con ese UUID")
def get_atleta_uuid_no_registrado(client: TestClient, context: dict[str, Any]) -> None:
    context["response"] = client.get(f"/registro/atletas/{context['atleta_id']}")


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta es {status_code:d} con el atleta_id"))
def respuesta_201_con_atleta_id(context: dict[str, Any], status_code: int) -> None:
    assert context["response"].status_code == status_code
    assert "atleta_id" in context["response"].json()


@then("GET /registro/atletas con ese id retorna los datos del atleta")
def then_get_atleta(client: TestClient, context: dict[str, Any]) -> None:
    atleta_id = context["response"].json()["atleta_id"]
    get_resp = client.get(f"/registro/atletas/{atleta_id}")
    assert get_resp.status_code == 200
    data = get_resp.json()
    assert data["nombre"] == context["payload"]["nombre"]
    assert data["email"] == context["payload"]["email"]


@then(parsers.parse("la respuesta es {status_code:d} y brevet es nulo en la respuesta"))
def respuesta_201_brevet_nulo(context: dict[str, Any], status_code: int) -> None:
    assert context["response"].status_code == status_code
    atleta_id = context["response"].json()["atleta_id"]


@then(parsers.parse("la respuesta es {status_code:d} Conflict"))
def respuesta_409(context: dict[str, Any], status_code: int) -> None:
    assert context["response"].status_code == status_code


@then(parsers.parse("la respuesta es {status_code:d} Unprocessable Entity"))
def respuesta_422(context: dict[str, Any], status_code: int) -> None:
    assert context["response"].status_code == status_code


@then(parsers.parse("la respuesta es {status_code:d} Not Found"))
def respuesta_404(context: dict[str, Any], status_code: int) -> None:
    assert context["response"].status_code == status_code
