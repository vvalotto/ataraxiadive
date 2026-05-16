"""Tests API para POST /auth/registro."""

from __future__ import annotations

from unittest.mock import MagicMock
from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from identidad.api.dependencies import (
    get_email_sender,
    get_password_hasher,
    get_token_service,
    get_usuario_repository,
)
from identidad.api.router import router
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.jwt_service import JWTService


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
        return [usuario for usuario in self.usuarios if rol in usuario.roles]

    async def list_all(self) -> list[Usuario]:
        return list(self.usuarios)


class SpyEmailSender:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        self.calls.append(destinatario.email)
        return "fake-id"


def _app(
    repo: FakeUsuarioRepository,
    password_hasher: PasswordHashingPort,
    token_service=None,
    email_sender: SpyEmailSender | None = None,
    monkeypatch=None,
) -> TestClient:
    spy = email_sender or SpyEmailSender()
    if token_service is None:
        if monkeypatch:
            monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
        import os

        os.environ.setdefault("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
        token_service = JWTService()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_usuario_repository] = lambda: repo
    app.dependency_overrides[get_password_hasher] = lambda: password_hasher
    app.dependency_overrides[get_token_service] = lambda: token_service
    app.dependency_overrides[get_email_sender] = lambda: spy
    return TestClient(app)


def test_registro_exitoso_persiste_nombre_apellido_y_rol(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Ana",
            "apellido": "Garcia",
            "email": "ana@email.com",
            "password": "Apnea12345",
            "roles": ["ATLETA"],
        },
    )

    assert response.status_code == 201
    assert len(repo.usuarios) == 1
    usuario = repo.usuarios[0]
    assert usuario.nombre == "Ana"
    assert usuario.apellido == "Garcia"
    assert Rol.ATLETA in usuario.roles


def test_registro_un_rol_devuelve_token(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Ana",
            "apellido": "Garcia",
            "email": "ana@email.com",
            "password": "Apnea12345",
            "roles": ["ATLETA"],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert "access_token" in body
    assert "requires_role_selection" not in body


def test_registro_multi_rol_devuelve_role_selection(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Pedro",
            "apellido": "Lopez",
            "email": "pedro@email.com",
            "password": "Apnea12345",
            "roles": ["JUEZ", "ATLETA"],
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body.get("requires_role_selection") is True
    assert "access_token" not in body


def test_registro_email_existente_agrega_rol_devuelve_200(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    hasher = BcryptPasswordHasher()
    repo.usuarios.append(
        Usuario(
            usuario_id=uuid4(),
            nombre="Julia",
            apellido="Segura",
            email="juez1@email.com",
            password_hash=hasher.hash("Apnea12345"),
            roles=[Rol.JUEZ],
        )
    )
    client = _app(repo, hasher)

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Julia",
            "apellido": "Segura",
            "email": "juez1@email.com",
            "password": "Apnea12345",
            "roles": ["ATLETA"],
        },
    )

    assert response.status_code == 200
    assert response.json().get("requires_role_selection") is True


def test_registro_email_existente_mismo_rol_retorna_409(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    hasher = BcryptPasswordHasher()
    repo.usuarios.append(
        Usuario(
            usuario_id=uuid4(),
            nombre="Julia",
            apellido="Segura",
            email="juez1@email.com",
            password_hash=hasher.hash("Apnea12345"),
            roles=[Rol.JUEZ],
        )
    )
    client = _app(repo, hasher)

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Julia",
            "apellido": "Segura",
            "email": "juez1@email.com",
            "password": "Apnea12345",
            "roles": ["JUEZ"],
        },
    )

    assert response.status_code == 409


def test_registro_rechaza_password_corta(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Ana",
            "apellido": "Garcia",
            "email": "ana@email.com",
            "password": "corta",
            "roles": ["ATLETA"],
        },
    )

    assert response.status_code == 422


def test_registro_rechaza_rol_admin(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    client = _app(repo, BcryptPasswordHasher())

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Admin",
            "apellido": "Prohibido",
            "email": "admin@email.com",
            "password": "Apnea12345",
            "roles": ["ADMIN"],
        },
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "El rol ADMIN no está permitido en el auto-registro"


def test_registro_invoca_email_sender_al_crear_usuario(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-registro-32chars!!")
    repo = FakeUsuarioRepository()
    spy = SpyEmailSender()
    client = _app(repo, BcryptPasswordHasher(), email_sender=spy)

    response = client.post(
        "/auth/registro",
        json={
            "nombre": "Marco",
            "apellido": "Polo",
            "email": "marco@email.com",
            "password": "Apnea12345",
            "roles": ["ATLETA"],
        },
    )

    assert response.status_code == 201
    assert spy.calls == ["marco@email.com"]
