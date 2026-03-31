"""Step definitions BDD — US-3.3.1: torneo_id en Competencia."""

from __future__ import annotations

import importlib
import sqlite3
from typing import Any
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, scenario, then, when

FEATURE = "../US-3.3.1-torneo-id-competencia.feature"

_CREATE_EVENTS = """
    CREATE TABLE IF NOT EXISTS events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def context(tmp_path: Any, monkeypatch: Any) -> dict[str, Any]:
    db_path = str(tmp_path / "competencia_bdd.db")
    # Crear tabla events antes de que TestClient use el DB
    conn = sqlite3.connect(db_path)
    conn.execute(_CREATE_EVENTS)
    conn.commit()
    conn.close()
    monkeypatch.setenv("COMPETENCIA_DB_PATH", db_path)
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    monkeypatch.setenv("REGISTRO_DB_PATH", str(tmp_path / "registro.db"))
    monkeypatch.setenv("IDENTIDAD_DB_PATH", str(tmp_path / "identidad.db"))
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-bdd-32-chars-minimum!!")
    monkeypatch.setenv("RESULTADOS_DB_PATH", str(tmp_path / "resultados.db"))
    return {}


@pytest.fixture
def client(context: dict[str, Any]) -> TestClient:
    import app as app_module

    importlib.reload(app_module)
    from app import app as fastapi_app

    return TestClient(fastapi_app)


# ── Scenario 1: configurar competencia con torneo_id ─────────────────────────


@scenario(FEATURE, "configurar competencia con torneo_id")
def test_configurar_con_torneo_id() -> None:
    pass


@given("un torneo_id valido", target_fixture="context")
def given_torneo_id_valido(context: dict[str, Any]) -> dict[str, Any]:
    context["torneo_id"] = str(uuid4())
    context["competencia_id"] = str(uuid4())
    return context


@when("se configura el intervalo OT con torneo_id")
def when_configura_con_torneo_id(context: dict[str, Any], client: TestClient) -> None:
    resp = client.post(
        "/competencia",
        json={
            "competencia_id": context["competencia_id"],
            "disciplina": "STA",
            "intervalo_minutos": 9,
            "configurado_por": "org-01",
            "torneo_id": context["torneo_id"],
        },
    )
    assert resp.status_code == 201, resp.text
    context["post_resp"] = resp.json()


@then("la competencia almacena el torneo_id")
def then_almacena_torneo_id(context: dict[str, Any], client: TestClient) -> None:
    resp = client.get(
        f"/competencia/{context['competencia_id']}/estado",
        params={"disciplina": "STA"},
    )
    assert resp.status_code == 200
    context["estado"] = resp.json()
    assert context["estado"]["torneo_id"] == context["torneo_id"]


@then("GET estado retorna el torneo_id")
def then_estado_retorna_torneo_id(context: dict[str, Any]) -> None:
    assert context["estado"]["torneo_id"] is not None


# ── Scenario 2: backward compat sin torneo_id ────────────────────────────────


@scenario(FEATURE, "configurar competencia sin torneo_id (backward compat)")
def test_configurar_sin_torneo_id() -> None:
    pass


@given("payload sin campo torneo_id", target_fixture="context")
def given_sin_torneo_id(context: dict[str, Any]) -> dict[str, Any]:
    context["competencia_id"] = str(uuid4())
    return context


@when("se configura el intervalo OT sin torneo_id")
def when_configura_sin_torneo_id(context: dict[str, Any], client: TestClient) -> None:
    resp = client.post(
        "/competencia",
        json={
            "competencia_id": context["competencia_id"],
            "disciplina": "STA",
            "intervalo_minutos": 9,
            "configurado_por": "org-01",
        },
    )
    assert resp.status_code == 201, resp.text


@then("la competencia se crea con torneo_id nulo")
def then_torneo_id_nulo(context: dict[str, Any], client: TestClient) -> None:
    resp = client.get(
        f"/competencia/{context['competencia_id']}/estado",
        params={"disciplina": "STA"},
    )
    assert resp.status_code == 200
    assert resp.json()["torneo_id"] is None


@then("los tests existentes siguen pasando")
def then_tests_existentes_pasan(context: dict[str, Any], client: TestClient) -> None:
    resp = client.get(
        f"/competencia/{context['competencia_id']}/estado",
        params={"disciplina": "STA"},
    )
    assert resp.json()["intervalo_minutos"] == 9


# ── Scenario 3: listar 3 competencias del mismo torneo ───────────────────────


@scenario(FEATURE, "listar competencias de un torneo")
def test_listar_competencias_torneo() -> None:
    pass


@given("3 competencias configuradas con el mismo torneo_id", target_fixture="context")
def given_3_competencias(context: dict[str, Any]) -> dict[str, Any]:
    context["torneo_id"] = str(uuid4())
    context["ids"] = [str(uuid4()) for _ in range(3)]
    return context


@when("se consultan competencias por torneo_id")
def when_consultan_por_torneo(context: dict[str, Any], client: TestClient) -> None:
    disciplinas = ["STA", "DNF", "DYN"]
    for i, cid in enumerate(context["ids"]):
        client.post(
            "/competencia",
            json={
                "competencia_id": cid,
                "disciplina": disciplinas[i],
                "intervalo_minutos": 9,
                "configurado_por": "org-01",
                "torneo_id": context["torneo_id"],
            },
        )
    resp = client.get("/competencia", params={"torneo_id": context["torneo_id"]})
    assert resp.status_code == 200
    context["resultado"] = resp.json()


@then("se retornan 3 competencias")
def then_retornan_3(context: dict[str, Any]) -> None:
    assert len(context["resultado"]) == 3


# ── Scenario 4: filtro correcto por torneo_id ────────────────────────────────


@scenario(FEATURE, "listar competencias filtra por torneo_id correcto")
def test_filtro_por_torneo() -> None:
    pass


@given("2 competencias de torneo A y 1 de torneo B", target_fixture="context")
def given_dos_torneos(context: dict[str, Any]) -> dict[str, Any]:
    context["torneo_a"] = str(uuid4())
    context["torneo_b"] = str(uuid4())
    context["ids_a"] = [str(uuid4()), str(uuid4())]
    context["id_b"] = str(uuid4())
    return context


@when("se consultan competencias por torneo A")
def when_consultan_torneo_a(context: dict[str, Any], client: TestClient) -> None:
    for cid in context["ids_a"]:
        client.post(
            "/competencia",
            json={
                "competencia_id": cid,
                "disciplina": "STA",
                "intervalo_minutos": 9,
                "configurado_por": "org-01",
                "torneo_id": context["torneo_a"],
            },
        )
    client.post(
        "/competencia",
        json={
            "competencia_id": context["id_b"],
            "disciplina": "DNF",
            "intervalo_minutos": 9,
            "configurado_por": "org-01",
            "torneo_id": context["torneo_b"],
        },
    )
    resp = client.get("/competencia", params={"torneo_id": context["torneo_a"]})
    assert resp.status_code == 200
    context["resultado"] = resp.json()


@then("se retornan solo 2 competencias")
def then_retornan_2(context: dict[str, Any]) -> None:
    assert len(context["resultado"]) == 2
    ids = {r["competencia_id"] for r in context["resultado"]}
    assert context["id_b"] not in ids
