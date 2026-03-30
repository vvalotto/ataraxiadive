"""Tests unitarios — RegistrarUsuarioHandler + AutenticarUsuarioHandler (mocks)."""
from __future__ import annotations

import os
import uuid
from typing import Generator
from unittest.mock import AsyncMock, MagicMock, patch

import bcrypt
import pytest

from identidad.application.commands.autenticar_usuario import (
    AutenticarUsuarioCommand,
    AutenticarUsuarioHandler,
    TokenResponse,
)
from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import (
    CredencialesInvalidas,
    EmailYaRegistrado,
    PasswordDemasiadoCorto,
    UsuarioInactivo,
)
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.jwt_service import JWTService


@pytest.fixture
def mock_repo() -> AsyncMock:
    repo = AsyncMock()
    repo.find_by_email = AsyncMock(return_value=None)
    repo.find_by_id = AsyncMock(return_value=None)
    repo.save = AsyncMock()
    return repo


@pytest.fixture
def jwt_service(monkeypatch: pytest.MonkeyPatch) -> JWTService:
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-1234")
    return JWTService()


# ── RegistrarUsuarioHandler ───────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_registrar_usuario_exitoso(mock_repo: AsyncMock) -> None:
    handler = RegistrarUsuarioHandler(mock_repo)
    cmd = RegistrarUsuarioCommand(email="nuevo@test.com", password="seguro12", rol=Rol.ORGANIZADOR)
    usuario_id = await handler.handle(cmd)
    assert usuario_id is not None
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_registrar_guarda_hash_no_plain(mock_repo: AsyncMock) -> None:
    handler = RegistrarUsuarioHandler(mock_repo)
    cmd = RegistrarUsuarioCommand(email="t@t.com", password="password1", rol=Rol.ATLETA)
    await handler.handle(cmd)
    saved_usuario: Usuario = mock_repo.save.call_args[0][0]
    assert saved_usuario.password_hash != "password1"
    assert saved_usuario.password_hash.startswith("$2b$")


@pytest.mark.asyncio
async def test_registrar_email_duplicado_lanza_excepcion(mock_repo: AsyncMock) -> None:
    existente = Usuario(uuid.uuid4(), "dup@test.com", "$2b$hash", Rol.JUEZ)
    mock_repo.find_by_email.return_value = existente
    handler = RegistrarUsuarioHandler(mock_repo)
    cmd = RegistrarUsuarioCommand(email="dup@test.com", password="password1", rol=Rol.JUEZ)
    with pytest.raises(EmailYaRegistrado):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_registrar_password_corto_lanza_excepcion(mock_repo: AsyncMock) -> None:
    handler = RegistrarUsuarioHandler(mock_repo)
    cmd = RegistrarUsuarioCommand(email="t@t.com", password="corto", rol=Rol.ATLETA)
    with pytest.raises(PasswordDemasiadoCorto):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_registrar_password_exactamente_8_es_valido(mock_repo: AsyncMock) -> None:
    handler = RegistrarUsuarioHandler(mock_repo)
    cmd = RegistrarUsuarioCommand(email="t@t.com", password="12345678", rol=Rol.ATLETA)
    usuario_id = await handler.handle(cmd)
    assert usuario_id is not None


# ── AutenticarUsuarioHandler ──────────────────────────────────────────────────

def _make_usuario(email: str, password: str, rol: Rol = Rol.JUEZ, activo: bool = True) -> Usuario:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return Usuario(uuid.uuid4(), email, hashed, rol, activo)


@pytest.mark.asyncio
async def test_autenticar_exitoso_retorna_token(mock_repo: AsyncMock, jwt_service: JWTService) -> None:
    u = _make_usuario("juez@test.com", "clave1234", Rol.JUEZ)
    mock_repo.find_by_email.return_value = u
    handler = AutenticarUsuarioHandler(mock_repo, jwt_service)
    cmd = AutenticarUsuarioCommand(email="juez@test.com", password="clave1234")
    result = await handler.handle(cmd)
    assert isinstance(result, TokenResponse)
    assert result.token_type == "bearer"
    assert len(result.access_token) > 0


@pytest.mark.asyncio
async def test_autenticar_password_incorrecto_lanza_excepcion(
    mock_repo: AsyncMock, jwt_service: JWTService
) -> None:
    u = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_email.return_value = u
    handler = AutenticarUsuarioHandler(mock_repo, jwt_service)
    cmd = AutenticarUsuarioCommand(email="juez@test.com", password="wrongpass")
    with pytest.raises(CredencialesInvalidas):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_autenticar_email_inexistente_lanza_excepcion(
    mock_repo: AsyncMock, jwt_service: JWTService
) -> None:
    mock_repo.find_by_email.return_value = None
    handler = AutenticarUsuarioHandler(mock_repo, jwt_service)
    cmd = AutenticarUsuarioCommand(email="nope@test.com", password="cualquier1")
    with pytest.raises(CredencialesInvalidas):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_autenticar_usuario_inactivo_lanza_excepcion(
    mock_repo: AsyncMock, jwt_service: JWTService
) -> None:
    u = _make_usuario("juez@test.com", "clave1234", activo=False)
    mock_repo.find_by_email.return_value = u
    handler = AutenticarUsuarioHandler(mock_repo, jwt_service)
    cmd = AutenticarUsuarioCommand(email="juez@test.com", password="clave1234")
    with pytest.raises(UsuarioInactivo):
        await handler.handle(cmd)


# ── JWTService ────────────────────────────────────────────────────────────────

def test_jwt_generate_y_verify_payload(jwt_service: JWTService) -> None:
    u = _make_usuario("admin@test.com", "pass1234", Rol.ADMIN)
    token = jwt_service.generate(u)
    payload = jwt_service.verify(token)
    assert payload["sub"] == str(u.usuario_id)
    assert payload["email"] == "admin@test.com"
    assert payload["rol"] == "ADMIN"


def test_jwt_token_invalido_lanza_excepcion(jwt_service: JWTService) -> None:
    from identidad.domain.exceptions import TokenInvalido
    with pytest.raises(TokenInvalido):
        jwt_service.verify("token.invalido.xxx")


def test_jwt_sin_secret_lanza_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IDENTIDAD_JWT_SECRET", raising=False)
    with pytest.raises(ValueError, match="IDENTIDAD_JWT_SECRET"):
        JWTService()
