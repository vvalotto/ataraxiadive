"""Tests API para POST /auth/cambiar-password."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_current_user, get_password_hasher, get_usuario_repository
from identidad.api.router import router
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher


class FakeUsuarioRepository:
    def __init__(self, password_hasher: PasswordHashingPort) -> None:
        self.usuario = Usuario(
            usuario_id=uuid4(),
            nombre="Julia",
            apellido="Segura",
            email="juez1@email.com",
            password_hash=password_hasher.hash("Apnea12345"),
            roles=[Rol.JUEZ],
        )

    async def save(self, usuario: Usuario) -> None:
        self.usuario = usuario

    async def find_by_id(self, usuario_id):  # type: ignore[no-untyped-def]
        if usuario_id == self.usuario.usuario_id:
            return self.usuario
        return None

    async def find_by_email(self, email: str) -> Usuario | None:
        if email == self.usuario.email:
            return self.usuario
        return None

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        return [self.usuario] if rol in self.usuario.roles else []

    async def list_all(self) -> list[Usuario]:
        return [self.usuario]


def _client(repo: FakeUsuarioRepository, password_hasher: PasswordHashingPort) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_usuario_repository] = lambda: repo
    app.dependency_overrides[get_password_hasher] = lambda: password_hasher
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": str(repo.usuario.usuario_id),
        "email": repo.usuario.email,
        "rol": "JUEZ",
    }
    return TestClient(app)


def test_cambiar_password_exitoso() -> None:
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher)
    client = _client(repo, password_hasher)

    response = client.post(
        "/auth/cambiar-password",
        json={"password_actual": "Apnea12345", "password_nueva": "NuevaPass456"},
    )

    assert response.status_code == 204
    assert password_hasher.verify("NuevaPass456", repo.usuario.password_hash)


def test_cambiar_password_rechaza_password_actual_incorrecta() -> None:
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher)
    client = _client(repo, password_hasher)

    response = client.post(
        "/auth/cambiar-password",
        json={"password_actual": "wrongpass", "password_nueva": "nuevapass456"},
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "La contraseña actual es incorrecta"


def test_cambiar_password_rechaza_password_nueva_corta() -> None:
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher)
    client = _client(repo, password_hasher)

    response = client.post(
        "/auth/cambiar-password",
        json={"password_actual": "Apnea12345", "password_nueva": "abc"},
    )

    assert response.status_code == 422


def test_cambiar_password_requiere_autenticacion() -> None:
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher)
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_usuario_repository] = lambda: repo
    app.dependency_overrides[get_password_hasher] = lambda: password_hasher
    client = TestClient(app, raise_server_exceptions=False)

    response = client.post(
        "/auth/cambiar-password",
        json={"password_actual": "Apnea12345", "password_nueva": "NuevaPass456"},
    )

    assert response.status_code == 401
