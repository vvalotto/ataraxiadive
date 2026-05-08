"""Tests API para recuperación de password."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
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
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.jwt_service import JWTService


class FakeUsuarioRepository:
    def __init__(self, password_hash: str) -> None:
        self.usuario = Usuario(
            usuario_id=uuid4(),
            nombre="Julia",
            apellido="Segura",
            email="juez1@email.com",
            password_hash=password_hash,
            rol=Rol.JUEZ,
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
        return [self.usuario] if self.usuario.rol == rol else []

    async def list_all(self) -> list[Usuario]:
        return [self.usuario]


class FakeEmailSender:
    def __init__(self) -> None:
        self.enviados: list[str] = []

    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        self.enviados.append(contenido.cuerpo_texto)
        return "fake-provider-id"


def _client(
    repo: FakeUsuarioRepository, token_service: JWTService, email_sender: FakeEmailSender
) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_usuario_repository] = lambda: repo
    app.dependency_overrides[get_token_service] = lambda: token_service
    app.dependency_overrides[get_password_hasher] = lambda: BcryptPasswordHasher()
    app.dependency_overrides[get_email_sender] = lambda: email_sender
    return TestClient(app)


def test_solicitar_reset_password_retorna_200_y_envia_email_si_usuario_existe(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-1234")
    monkeypatch.setenv("FRONTEND_BASE_URL", "http://localhost:5173")
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher.hash("apnea123"))
    email_sender = FakeEmailSender()
    client = _client(repo, JWTService(), email_sender)

    response = client.post("/auth/solicitar-reset", json={"email": repo.usuario.email})

    assert response.status_code == 200
    assert "Si el email existe" in response.json()["detail"]
    assert len(email_sender.enviados) == 1
    assert "/reset-password?token=" in email_sender.enviados[0]


def test_solicitar_reset_password_retorna_200_sin_filtrar_email_inexistente(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-1234")
    monkeypatch.setenv("FRONTEND_BASE_URL", "http://localhost:5173")
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher.hash("apnea123"))
    email_sender = FakeEmailSender()
    client = _client(repo, JWTService(), email_sender)

    response = client.post("/auth/solicitar-reset", json={"email": "nadie@email.com"})

    assert response.status_code == 200
    assert response.json()["detail"].startswith("Si el email existe")
    assert email_sender.enviados == []


def test_reset_password_exitoso(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-1234")
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher.hash("apnea123"))
    token_service = JWTService()
    email_sender = FakeEmailSender()
    client = _client(repo, token_service, email_sender)
    token = token_service.generate_reset_token(repo.usuario.email)

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "password_nueva": "NuevaPass456"},
    )

    assert response.status_code == 204
    assert password_hasher.verify("NuevaPass456", repo.usuario.password_hash)


def test_reset_password_rechaza_token_de_sesion(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-1234")
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher.hash("apnea123"))
    token_service = JWTService()
    email_sender = FakeEmailSender()
    client = _client(repo, token_service, email_sender)

    response = client.post(
        "/auth/reset-password",
        json={
            "token": token_service.generate(repo.usuario),
            "password_nueva": "NuevaPass456",
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Token de recuperación inválido o expirado"


def test_reset_password_rechaza_token_expirado(monkeypatch) -> None:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-1234")
    password_hasher = BcryptPasswordHasher()
    repo = FakeUsuarioRepository(password_hasher.hash("apnea123"))
    token_service = JWTService()
    email_sender = FakeEmailSender()
    client = _client(repo, token_service, email_sender)
    token = jwt.encode(
        {
            "sub": repo.usuario.email,
            "type": "password_reset",
            "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=1),
        },
        "test-secret-1234",
        algorithm="HS256",
    )

    response = client.post(
        "/auth/reset-password",
        json={"token": token, "password_nueva": "NuevaPass456"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Token de recuperación inválido o expirado"
