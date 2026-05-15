"""Step definitions BDD — US-ADJ-10.1: Edicion completa del torneo."""

from __future__ import annotations

import asyncio
import sys
from datetime import date
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from identidad.api.dependencies import get_current_user
from shared.domain.value_objects.disciplina import Disciplina
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.grupo_etario import GrupoEtario
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

_torneo_router_mod = sys.modules["torneo.api.router"]

scenarios("../US-ADJ-10.1-edicion-torneo.feature")


@pytest.fixture
def context(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    monkeypatch.setattr(_torneo_router_mod, "_cierre_inscripcion_precondition", None)
    monkeypatch.setattr(_torneo_router_mod, "_ejecucion_precondition", None)
    monkeypatch.setattr(_torneo_router_mod, "_ejecucion_post_action", None)
    return {
        "repo": SQLiteTorneoRepository(str(tmp_path / "torneo.db")),
        "torneo_id": None,
        "response": None,
    }


@pytest.fixture
def client(context: dict) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "org-1",
        "email": "org@test.com",
        "rol": "ORGANIZADOR",
    }
    return TestClient(app)


def _seed(repo, nombre: str, estado: str, disciplinas: set | None = None) -> str:
    from torneo.domain.value_objects.estado_torneo import EstadoTorneo

    torneo = Torneo(
        torneo_id=uuid4(),
        nombre=nombre,
        descripcion="desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede(nombre="Piscina", ciudad="Buenos Aires", pais="AR"),
        entidad_organizadora=EntidadOrganizadora(nombre="AIDA", tipo="FEDERACION"),
        grupos_etarios=frozenset({GrupoEtario.SENIOR}),
    )
    if estado != "CREADO":
        torneo.estado = EstadoTorneo(estado)
    if disciplinas:
        torneo.asignar_disciplinas(frozenset(disciplinas))
    asyncio.run(repo.save(torneo))
    return str(torneo.torneo_id)


def _update_payload(nombre: str = "Torneo Editado", ciudad: str = "Cordoba") -> dict:
    return {
        "nombre": nombre,
        "descripcion": "desc editada",
        "fecha_inicio": "2026-07-01",
        "fecha_fin": "2026-07-03",
        "sede": {"nombre": "Club", "ciudad": ciudad, "pais": "AR"},
        "grupos_etarios": ["SENIOR"],
    }


@given("el sistema tiene una base de datos limpia de torneos")
def base_limpia(context: dict) -> None:
    pass


@given(parsers.parse('existe un torneo "{nombre}" en estado {estado}'))
def existe_torneo(client: TestClient, context: dict, nombre: str, estado: str) -> None:
    context["torneo_id"] = _seed(context["repo"], nombre, estado)


@given(parsers.parse('existe un torneo "{nombre}" en estado {estado} con disciplinas STA y DNF'))
def existe_torneo_con_disciplinas(
    client: TestClient, context: dict, nombre: str, estado: str
) -> None:
    context["torneo_id"] = _seed(context["repo"], nombre, estado, {Disciplina.STA, Disciplina.DNF})


@when(parsers.parse('el organizador actualiza el torneo con nombre "{nombre}" y ciudad "{ciudad}"'))
def actualiza_torneo(client: TestClient, context: dict, nombre: str, ciudad: str) -> None:
    context["response"] = client.put(
        f"/torneos/{context['torneo_id']}",
        json=_update_payload(nombre, ciudad),
    )


@when(parsers.parse('el organizador intenta actualizar el torneo con nombre "{nombre}"'))
def intenta_actualizar(client: TestClient, context: dict, nombre: str) -> None:
    context["response"] = client.put(
        f"/torneos/{context['torneo_id']}",
        json=_update_payload(nombre),
    )


@when(parsers.parse("el organizador edita el nombre del torneo"))
def edita_nombre(client: TestClient, context: dict) -> None:
    context["response"] = client.put(
        f"/torneos/{context['torneo_id']}",
        json=_update_payload("Torneo Renombrado", "Cordoba"),
    )


@then(parsers.parse('el torneo tiene nombre "{nombre}"'))
def torneo_tiene_nombre(context: dict, nombre: str) -> None:
    torneo_id_uuid = __import__("uuid").UUID(context["torneo_id"])
    torneo = asyncio.run(context["repo"].find_by_id(torneo_id_uuid))
    assert torneo is not None
    assert torneo.nombre == nombre


@then(parsers.parse('la sede del torneo tiene ciudad "{ciudad}"'))
def sede_tiene_ciudad(context: dict, ciudad: str) -> None:
    torneo_id_uuid = __import__("uuid").UUID(context["torneo_id"])
    torneo = asyncio.run(context["repo"].find_by_id(torneo_id_uuid))
    assert torneo is not None
    assert torneo.sede.ciudad == ciudad


@then("la respuesta es 409 con detalle sobre estado invalido")
def respuesta_409(context: dict) -> None:
    assert context["response"].status_code == 409
    assert "estado" in context["response"].json()["detail"].lower()


@then("las disciplinas STA y DNF permanecen sin cambios")
def disciplinas_sin_cambios(context: dict) -> None:
    torneo_id_uuid = __import__("uuid").UUID(context["torneo_id"])
    torneo = asyncio.run(context["repo"].find_by_id(torneo_id_uuid))
    assert torneo is not None
    disciplinas = {dt.disciplina for dt in torneo.disciplinas_torneo}
    assert Disciplina.STA in disciplinas
    assert Disciplina.DNF in disciplinas
