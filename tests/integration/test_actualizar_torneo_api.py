"""Integración HTTP — PUT /torneos/{id} (US-ADJ-10.1)."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user
from torneo.api.router import router
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.grupo_etario import GrupoEtario
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


def _organizador() -> dict:
    return {"sub": "org-1", "email": "org@test.com", "rol": "ORGANIZADOR"}


def _seed_torneo(repo: SQLiteTorneoRepository, estado: str = "CREADO") -> Torneo:
    import asyncio
    from torneo.domain.value_objects.estado_torneo import EstadoTorneo

    torneo = Torneo(
        torneo_id=uuid4(),
        nombre="Torneo Original",
        descripcion="desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede(nombre="Piscina", ciudad="Buenos Aires", pais="AR"),
        entidad_organizadora=EntidadOrganizadora(nombre="AIDA", tipo="FEDERACION"),
        grupos_etarios=frozenset({GrupoEtario.SENIOR}),
    )
    if estado != "CREADO":
        torneo.estado = EstadoTorneo(estado)
    asyncio.run(repo.save(torneo))
    return torneo


@pytest.fixture
def ctx(tmp_path, monkeypatch: pytest.MonkeyPatch):
    import sys

    monkeypatch.setenv("TORNEO_DB_PATH", str(tmp_path / "torneo.db"))
    torneo_router_mod = sys.modules["torneo.api.router"]
    monkeypatch.setattr(torneo_router_mod, "_cierre_inscripcion_precondition", None)
    monkeypatch.setattr(torneo_router_mod, "_ejecucion_precondition", None)
    monkeypatch.setattr(torneo_router_mod, "_ejecucion_post_action", None)

    app = FastAPI()
    app.include_router(router)
    register_torneo_exception_handlers(app)
    app.dependency_overrides[get_current_user] = _organizador

    repo = SQLiteTorneoRepository(str(tmp_path / "torneo.db"))
    client = TestClient(app)
    return {"client": client, "repo": repo}


def _payload(nombre: str = "Torneo Editado", ciudad: str = "Cordoba") -> dict:
    return {
        "nombre": nombre,
        "descripcion": "desc editada",
        "fecha_inicio": "2026-07-01",
        "fecha_fin": "2026-07-03",
        "sede": {"nombre": "Club", "ciudad": ciudad, "pais": "AR"},
        "grupos_etarios": ["SENIOR", "JUNIOR"],
    }


def test_put_torneo_en_creado_retorna_200(ctx):
    torneo = _seed_torneo(ctx["repo"], "CREADO")
    response = ctx["client"].put(f"/torneos/{torneo.torneo_id}", json=_payload())
    assert response.status_code == 200
    assert response.json()["ok"] is True


def test_put_torneo_persiste_cambios(ctx):
    import asyncio

    torneo = _seed_torneo(ctx["repo"], "CREADO")
    ctx["client"].put(f"/torneos/{torneo.torneo_id}", json=_payload("Nuevo Nombre", "Rosario"))

    actualizado = asyncio.run(ctx["repo"].find_by_id(torneo.torneo_id))
    assert actualizado is not None
    assert actualizado.nombre == "Nuevo Nombre"
    assert actualizado.sede.ciudad == "Rosario"
    assert GrupoEtario.JUNIOR in actualizado.grupos_etarios


def test_put_torneo_en_inscripcion_abierta_retorna_200(ctx):
    torneo = _seed_torneo(ctx["repo"], "INSCRIPCION_ABIERTA")
    response = ctx["client"].put(f"/torneos/{torneo.torneo_id}", json=_payload())
    assert response.status_code == 200


def test_put_torneo_en_ejecucion_retorna_409(ctx):
    torneo = _seed_torneo(ctx["repo"], "EJECUCION")
    response = ctx["client"].put(f"/torneos/{torneo.torneo_id}", json=_payload())
    assert response.status_code == 409
    assert "estado" in response.json()["detail"].lower()


def test_put_torneo_no_encontrado_retorna_404(ctx):
    response = ctx["client"].put(f"/torneos/{uuid4()}", json=_payload())
    assert response.status_code == 404


def test_put_torneo_no_afecta_disciplinas(ctx):
    import asyncio
    from shared.domain.value_objects.disciplina import Disciplina

    torneo = _seed_torneo(ctx["repo"], "CREADO")
    torneo.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF}))
    asyncio.run(ctx["repo"].save(torneo))

    ctx["client"].put(f"/torneos/{torneo.torneo_id}", json=_payload())

    actualizado = asyncio.run(ctx["repo"].find_by_id(torneo.torneo_id))
    assert actualizado is not None
    disciplinas = {dt.disciplina for dt in actualizado.disciplinas_torneo}
    assert Disciplina.STA in disciplinas
    assert Disciplina.DNF in disciplinas
