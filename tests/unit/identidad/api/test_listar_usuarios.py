"""Tests API para listar usuarios por rol."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user, get_usuario_repository
from identidad.api.router import router
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.value_objects.rol import Rol


class FakeUsuarioRepository:
    def __init__(self) -> None:
        self.usuarios = [
            Usuario(uuid4(), "Julia", "Segura", "juez2@ataraxia.com", "$2b$hash", [Rol.JUEZ]),
            Usuario(uuid4(), "Olga", "Rios", "org@ataraxia.com", "$2b$hash", [Rol.ORGANIZADOR]),
            Usuario(uuid4(), "Juan", "Acuna", "juez1@ataraxia.com", "$2b$hash", [Rol.JUEZ]),
            Usuario(uuid4(), "Ana", "Lopez", "atleta@ataraxia.com", "$2b$hash", [Rol.ATLETA]),
        ]

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        return sorted(
            [usuario for usuario in self.usuarios if rol in usuario.roles],
            key=lambda usuario: usuario.email,
        )

    async def list_all(self) -> list[Usuario]:
        return sorted(self.usuarios, key=lambda usuario: usuario.email)


def _mock_user(rol: str) -> dict:  # type: ignore[type-arg]
    return {"sub": "uid-1", "email": "test@test.com", "rol": rol}


def test_listar_usuarios_filtra_rol_juez() -> None:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _mock_user("ORGANIZADOR")
    app.dependency_overrides[get_usuario_repository] = lambda: FakeUsuarioRepository()
    client = TestClient(app)

    response = client.get("/auth/usuarios?rol=JUEZ")

    assert response.status_code == 200
    data = response.json()
    assert [usuario["email"] for usuario in data] == [
        "juez1@ataraxia.com",
        "juez2@ataraxia.com",
    ]
    assert all("JUEZ" in usuario["roles"] for usuario in data)
    assert [usuario["nombre"] for usuario in data] == ["Juan", "Julia"]


def test_listar_usuarios_sin_rol_devuelve_todos_ordenados() -> None:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _mock_user("ORGANIZADOR")
    app.dependency_overrides[get_usuario_repository] = lambda: FakeUsuarioRepository()
    client = TestClient(app)

    response = client.get("/auth/usuarios")

    assert response.status_code == 200
    data = response.json()
    emails = [usuario["email"] for usuario in data]
    assert "atleta@ataraxia.com" in emails
    assert "juez1@ataraxia.com" in emails
    assert "juez2@ataraxia.com" in emails
    assert "org@ataraxia.com" in emails
    assert data[0]["apellido"] == "Lopez"  # atleta@ataraxia.com viene primero (orden alfabético)


def test_listar_usuarios_requiere_organizador() -> None:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
    app.dependency_overrides[get_usuario_repository] = lambda: FakeUsuarioRepository()
    client = TestClient(app)

    response = client.get("/auth/usuarios?rol=JUEZ")

    assert response.status_code == 403
