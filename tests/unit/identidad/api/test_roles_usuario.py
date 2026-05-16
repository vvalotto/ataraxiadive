"""Tests API — POST/DELETE /auth/usuarios/me/roles."""

from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user, get_usuario_repository
from identidad.api.router import router
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.jwt_service import JWTService


class FakeRepo:
    def __init__(self, usuario: Usuario) -> None:
        self._usuario = usuario
        self.saved: Usuario | None = None

    async def find_by_id(self, usuario_id):  # type: ignore[no-untyped-def]
        return self._usuario if str(self._usuario.usuario_id) == str(usuario_id) else None

    async def save(self, usuario: Usuario) -> None:
        self._usuario = usuario
        self.saved = usuario

    async def find_by_email(self, email: str) -> Usuario | None:
        return None

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        return []

    async def list_all(self) -> list[Usuario]:
        return []


def _app_with_user(usuario: Usuario) -> TestClient:
    os.environ.setdefault("IDENTIDAD_JWT_SECRET", "test-secret-roles-32chars!!")
    jwt = JWTService()
    token_payload = {
        "sub": str(usuario.usuario_id),
        "email": usuario.email,
        "nombre": usuario.nombre,
        "apellido": usuario.apellido,
        "rol": usuario.roles[0].value,
    }
    repo = FakeRepo(usuario)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_usuario_repository] = lambda: repo
    app.dependency_overrides[get_current_user] = lambda: token_payload
    return TestClient(app)


def _usuario(roles: list[Rol]) -> Usuario:
    return Usuario(
        usuario_id=uuid4(),
        nombre="Test",
        apellido="User",
        email="test@email.com",
        password_hash="hash",
        roles=roles,
    )


# ── POST /auth/usuarios/me/roles ──────────────────────────────────────────────


def test_agregar_rol_exitoso() -> None:
    u = _usuario([Rol.ATLETA])
    client = _app_with_user(u)
    resp = client.post("/auth/usuarios/me/roles", json={"rol": "JUEZ"})
    assert resp.status_code == 200
    roles = resp.json()["roles"]
    assert "ATLETA" in roles
    assert "JUEZ" in roles


def test_agregar_rol_ya_asignado_retorna_409() -> None:
    u = _usuario([Rol.ATLETA, Rol.JUEZ])
    client = _app_with_user(u)
    resp = client.post("/auth/usuarios/me/roles", json={"rol": "JUEZ"})
    assert resp.status_code == 409


def test_agregar_rol_admin_retorna_403() -> None:
    u = _usuario([Rol.ATLETA])
    client = _app_with_user(u)
    resp = client.post("/auth/usuarios/me/roles", json={"rol": "ADMIN"})
    assert resp.status_code == 403


def test_agregar_rol_invalido_retorna_422() -> None:
    u = _usuario([Rol.ATLETA])
    client = _app_with_user(u)
    resp = client.post("/auth/usuarios/me/roles", json={"rol": "SUPERHEROE"})
    assert resp.status_code == 422


# ── DELETE /auth/usuarios/me/roles/{rol} ──────────────────────────────────────


def test_quitar_rol_exitoso() -> None:
    u = _usuario([Rol.JUEZ, Rol.ATLETA])
    client = _app_with_user(u)
    resp = client.delete("/auth/usuarios/me/roles/JUEZ")
    assert resp.status_code == 200
    roles = resp.json()["roles"]
    assert "JUEZ" not in roles
    assert "ATLETA" in roles


def test_quitar_rol_atleta_retorna_409() -> None:
    u = _usuario([Rol.ATLETA, Rol.JUEZ])
    client = _app_with_user(u)
    resp = client.delete("/auth/usuarios/me/roles/ATLETA")
    assert resp.status_code == 409


def test_quitar_rol_no_poseido_retorna_404() -> None:
    u = _usuario([Rol.ATLETA])
    client = _app_with_user(u)
    resp = client.delete("/auth/usuarios/me/roles/JUEZ")
    assert resp.status_code == 404


def test_quitar_unico_rol_retorna_409() -> None:
    u = _usuario([Rol.JUEZ])
    client = _app_with_user(u)
    resp = client.delete("/auth/usuarios/me/roles/JUEZ")
    assert resp.status_code == 409


def test_quitar_rol_invalido_retorna_422() -> None:
    u = _usuario([Rol.ATLETA])
    client = _app_with_user(u)
    resp = client.delete("/auth/usuarios/me/roles/SUPERHEROE")
    assert resp.status_code == 422
