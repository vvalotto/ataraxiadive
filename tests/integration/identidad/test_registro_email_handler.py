"""Tests de integración — RegistrarUsuarioHandler con EmailPort y DB real."""

from __future__ import annotations

import os
import tempfile

import pytest

from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.jwt_service import JWTService
from identidad.infrastructure.repositories.sqlite_usuario_repository import SQLiteUsuarioRepository


class SpyEmailSender:
    def __init__(self) -> None:
        self.calls: list[str] = []

    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        self.calls.append(destinatario.email)
        return "spy-id"


class FailingEmailSender:
    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        raise RuntimeError("SMTP no disponible")


@pytest.fixture
def db_path(tmp_path) -> str:  # type: ignore[no-untyped-def]
    return str(tmp_path / "identidad_int.db")


@pytest.fixture
def token_service(monkeypatch) -> JWTService:  # type: ignore[no-untyped-def]
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-integration-32-chars!!")
    return JWTService()


@pytest.mark.asyncio
async def test_registro_envia_email_de_bienvenida(db_path: str, token_service: JWTService) -> None:
    repo = SQLiteUsuarioRepository(db_path=db_path)
    spy = SpyEmailSender()
    handler = RegistrarUsuarioHandler(repo, BcryptPasswordHasher(), token_service, spy)

    cmd = RegistrarUsuarioCommand(
        nombre="Ana",
        apellido="Garcia",
        email="ana@int.com",
        password="Apnea12345",
        roles=[Rol.ATLETA],
    )
    resultado = await handler.handle(cmd)

    assert resultado.usuario_id is not None
    assert spy.calls == ["ana@int.com"]
    usuario = await repo.find_by_id(resultado.usuario_id)
    assert usuario is not None
    assert usuario.email == "ana@int.com"


@pytest.mark.asyncio
async def test_registro_no_falla_si_email_no_disponible(
    db_path: str, token_service: JWTService
) -> None:
    repo = SQLiteUsuarioRepository(db_path=db_path)
    handler = RegistrarUsuarioHandler(
        repo, BcryptPasswordHasher(), token_service, FailingEmailSender()
    )

    cmd = RegistrarUsuarioCommand(
        nombre="Luis",
        apellido="Perez",
        email="luis@int.com",
        password="Apnea12345",
        roles=[Rol.JUEZ],
    )
    resultado = await handler.handle(cmd)

    assert resultado.usuario_id is not None
    usuario = await repo.find_by_id(resultado.usuario_id)
    assert usuario is not None
    assert usuario.email == "luis@int.com"


@pytest.mark.asyncio
async def test_registro_y_login_con_mismas_credenciales(
    db_path: str, token_service: JWTService
) -> None:
    repo = SQLiteUsuarioRepository(db_path=db_path)
    handler = RegistrarUsuarioHandler(repo, BcryptPasswordHasher(), token_service, SpyEmailSender())

    cmd = RegistrarUsuarioCommand(
        nombre="Marco",
        apellido="Polo",
        email="marco@int.com",
        password="Apnea12345",
        roles=[Rol.ORGANIZADOR],
    )
    await handler.handle(cmd)

    usuario = await repo.find_by_email("marco@int.com")
    assert usuario is not None
    assert Rol.ORGANIZADOR in usuario.roles

    from identidad.application.commands.autenticar_usuario import (
        AutenticarUsuarioCommand,
        AutenticarUsuarioHandler,
        TokenResponse,
    )

    auth_handler = AutenticarUsuarioHandler(repo, token_service, BcryptPasswordHasher())
    result = await auth_handler.handle(
        AutenticarUsuarioCommand(email="marco@int.com", password="Apnea12345")
    )
    assert isinstance(result, TokenResponse)
    assert result.access_token
    payload = token_service.verify(result.access_token)
    assert payload["rol"] == "ORGANIZADOR"
