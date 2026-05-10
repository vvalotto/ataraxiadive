"""Tests API para POST /auth/registro."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import get_password_hasher, get_usuario_repository
from identidad.api.router import router
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher


class FakeUsuarioRepository:
    def __init__(self) -> None:
        self.usuarios: list[Usuario] = []

    async def save(self, usuario: Usuario) -> None:
        self.usuarios = [u for u in self.usuarios if u.usuario_id != usuario.usuario_id]
        self.usuarios.append(usuario)

    async def find_by_id(self, usuario_id):  # type: ignore[no-untyped-def]
        for usuario in self.usuarios:
            if usuario.usuario_id == usuario_id:
                return usuario
        return None

    async def find_by_email(self, email: str) -> Usuario | None:
        for usuario in self.usuarios:
            if usuario.email == email:
                return usuario
        return None

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        return [usuario for usuario in self.usuarios if usuario.rol == rol]

    async def list_all(self) -> list[Usuario]:
        return list(self.usuarios)


def _app(repo: FakeUsuarioRepository, password_hasher: PasswordHashingPort) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_usuario_repository] = lambda: repo
    app.dependency_overrides[get_password_hasher] = lambda: password_hasher
    return TestClient(app)


def test_registro_exitoso_persiste_nombre_apellido_y_rol() -> None:
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Ana",
            "apellido": "Garcia",
            "email": "ana@email.com",
            "password": "Apnea12345",
            "rol": "ATLETA",
        },
    )

    assert response.status_code == 201
    assert len(repo.usuarios) == 1
    usuario = repo.usuarios[0]
    assert usuario.nombre == "Ana"
    assert usuario.apellido == "Garcia"
    assert usuario.rol == Rol.ATLETA


def test_registro_rechaza_email_duplicado() -> None:
    repo = FakeUsuarioRepository()
    repo.usuarios.append(
        Usuario(
            usuario_id=uuid4(),
            nombre="Julia",
            apellido="Segura",
            email="juez1@email.com",
            password_hash="$2b$hash",
            rol=Rol.JUEZ,
        )
    )
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Otro",
            "apellido": "Usuario",
            "email": "juez1@email.com",
            "password": "Apnea12345",
            "rol": "ATLETA",
        },
    )

    assert response.status_code == 409


def test_registro_rechaza_password_corta() -> None:
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Ana",
            "apellido": "Garcia",
            "email": "ana@email.com",
            "password": "corta",
            "rol": "ATLETA",
        },
    )

    assert response.status_code == 422


def test_registro_rechaza_rol_admin() -> None:
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Admin",
            "apellido": "Prohibido",
            "email": "admin@email.com",
            "password": "Apnea12345",
            "rol": "ADMIN",
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "El rol ADMIN no está permitido en el auto-registro"
