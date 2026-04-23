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
            Usuario(uuid4(), "juez2@ataraxia.com", "$2b$hash", Rol.JUEZ),
            Usuario(uuid4(), "org@ataraxia.com", "$2b$hash", Rol.ORGANIZADOR),
            Usuario(uuid4(), "juez1@ataraxia.com", "$2b$hash", Rol.JUEZ),
            Usuario(uuid4(), "atleta@ataraxia.com", "$2b$hash", Rol.ATLETA),
        ]

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        return sorted(
            [usuario for usuario in self.usuarios if usuario.rol == rol],
            key=lambda usuario: usuario.email,
        )

    async def list_all(self) -> list[Usuario]:
        return sorted(self.usuarios, key=lambda usuario: (usuario.rol.value, usuario.email))


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
    assert all(usuario["rol"] == "JUEZ" for usuario in data)


def test_listar_usuarios_sin_rol_devuelve_todos_ordenados() -> None:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _mock_user("ORGANIZADOR")
    app.dependency_overrides[get_usuario_repository] = lambda: FakeUsuarioRepository()
    client = TestClient(app)

    response = client.get("/auth/usuarios")

    assert response.status_code == 200
    data = response.json()
    assert [(usuario["rol"], usuario["email"]) for usuario in data] == [
        ("ATLETA", "atleta@ataraxia.com"),
        ("JUEZ", "juez1@ataraxia.com"),
        ("JUEZ", "juez2@ataraxia.com"),
        ("ORGANIZADOR", "org@ataraxia.com"),
    ]


def test_listar_usuarios_requiere_organizador() -> None:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_current_user] = lambda: _mock_user("ATLETA")
    app.dependency_overrides[get_usuario_repository] = lambda: FakeUsuarioRepository()
    client = TestClient(app)

    response = client.get("/auth/usuarios?rol=JUEZ")

    assert response.status_code == 403
