"""Tests unitarios — RegistrarUsuarioHandler + AutenticarUsuarioHandler (mocks)."""

from __future__ import annotations

import os
import uuid
from unittest.mock import AsyncMock

import bcrypt
import pytest

from identidad.application.commands.autenticar_usuario import (
    AutenticarUsuarioCommand,
    AutenticarUsuarioHandler,
    TokenResponse,
)
from identidad.application.commands.cambiar_password import (
    CambiarPasswordCommand,
    CambiarPasswordHandler,
)
from identidad.application.commands.reset_password import ResetPasswordCommand, ResetPasswordHandler
from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.application.commands.solicitar_reset_password import (
    SolicitarResetPasswordCommand,
    SolicitarResetPasswordHandler,
)
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import (
    CredencialesInvalidas,
    EmailYaRegistrado,
    PasswordActualIncorrecto,
    PasswordDemasiadoCorto,
    RolNoPermitido,
    TokenResetInvalido,
    UsuarioNoEncontrado,
    UsuarioInactivo,
)
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
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


@pytest.fixture
def password_hasher() -> PasswordHashingPort:
    return BcryptPasswordHasher()


@pytest.fixture
def token_service(jwt_service: JWTService) -> TokenServicePort:
    return jwt_service


# ── RegistrarUsuarioHandler ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_registrar_usuario_exitoso(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    handler = RegistrarUsuarioHandler(mock_repo, password_hasher)
    cmd = RegistrarUsuarioCommand(
        nombre="Nuevo",
        apellido="Usuario",
        email="nuevo@test.com",
        password="Seguro1234",
        rol=Rol.ORGANIZADOR,
    )
    usuario_id = await handler.handle(cmd)
    assert usuario_id is not None
    mock_repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_registrar_guarda_hash_no_plain(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    handler = RegistrarUsuarioHandler(mock_repo, password_hasher)
    cmd = RegistrarUsuarioCommand(
        nombre="Ana",
        apellido="Garcia",
        email="t@t.com",
        password="Password10",
        rol=Rol.ATLETA,
    )
    await handler.handle(cmd)
    saved_usuario: Usuario = mock_repo.save.call_args[0][0]
    assert saved_usuario.nombre == "Ana"
    assert saved_usuario.apellido == "Garcia"
    assert saved_usuario.password_hash != "Password10"
    assert saved_usuario.password_hash.startswith("$2b$")


@pytest.mark.asyncio
async def test_registrar_email_duplicado_lanza_excepcion(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    existente = Usuario(uuid.uuid4(), "Dup", "Existente", "dup@test.com", "$2b$hash", Rol.JUEZ)
    mock_repo.find_by_email.return_value = existente
    handler = RegistrarUsuarioHandler(mock_repo, password_hasher)
    cmd = RegistrarUsuarioCommand(
        nombre="Dup",
        apellido="Nuevo",
        email="dup@test.com",
        password="Password10",
        rol=Rol.JUEZ,
    )
    with pytest.raises(EmailYaRegistrado):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_registrar_password_corto_lanza_excepcion(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    handler = RegistrarUsuarioHandler(mock_repo, password_hasher)
    cmd = RegistrarUsuarioCommand(
        nombre="Ana",
        apellido="Garcia",
        email="t@t.com",
        password="corto",
        rol=Rol.ATLETA,
    )
    with pytest.raises(PasswordDemasiadoCorto):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_registrar_password_exactamente_10_es_valido(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    handler = RegistrarUsuarioHandler(mock_repo, password_hasher)
    cmd = RegistrarUsuarioCommand(
        nombre="Ana",
        apellido="Garcia",
        email="t@t.com",
        password="Valida1234",
        rol=Rol.ATLETA,
    )
    usuario_id = await handler.handle(cmd)
    assert usuario_id is not None


@pytest.mark.asyncio
async def test_registrar_admin_lanza_excepcion(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    handler = RegistrarUsuarioHandler(mock_repo, password_hasher)
    cmd = RegistrarUsuarioCommand(
        nombre="Admin",
        apellido="Prohibido",
        email="admin@test.com",
        password="Valida1234",
        rol=Rol.ADMIN,
    )
    with pytest.raises(RolNoPermitido):
        await handler.handle(cmd)


# ── CambiarPasswordHandler ────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_cambiar_password_exitoso(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    usuario = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_id.return_value = usuario
    handler = CambiarPasswordHandler(mock_repo, password_hasher)

    await handler.handle(
        CambiarPasswordCommand(
            usuario_id=usuario.usuario_id,
            password_actual="clave1234",
            password_nueva="NuevaPass456",
        )
    )

    assert password_hasher.verify("NuevaPass456", usuario.password_hash)
    mock_repo.save.assert_called_once_with(usuario)


@pytest.mark.asyncio
async def test_cambiar_password_rechaza_password_actual_incorrecta(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    usuario = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_id.return_value = usuario
    handler = CambiarPasswordHandler(mock_repo, password_hasher)

    with pytest.raises(PasswordActualIncorrecto):
        await handler.handle(
            CambiarPasswordCommand(
                usuario_id=usuario.usuario_id,
                password_actual="wrongpass",
                password_nueva="NuevaPass456",
            )
        )


@pytest.mark.asyncio
async def test_cambiar_password_rechaza_password_nueva_corta(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    usuario = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_id.return_value = usuario
    handler = CambiarPasswordHandler(mock_repo, password_hasher)

    with pytest.raises(PasswordDemasiadoCorto):
        await handler.handle(
            CambiarPasswordCommand(
                usuario_id=usuario.usuario_id,
                password_actual="clave1234",
                password_nueva="abc",
            )
        )


@pytest.mark.asyncio
async def test_cambiar_password_rechaza_usuario_inexistente(
    mock_repo: AsyncMock, password_hasher: PasswordHashingPort
) -> None:
    mock_repo.find_by_id.return_value = None
    handler = CambiarPasswordHandler(mock_repo, password_hasher)

    with pytest.raises(UsuarioNoEncontrado):
        await handler.handle(
            CambiarPasswordCommand(
                usuario_id=uuid.uuid4(),
                password_actual="clave1234",
                password_nueva="NuevaPass456",
            )
        )


class FakeEmailSender:
    def __init__(self) -> None:
        self.enviados: list[tuple[str, str, str]] = []

    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        self.enviados.append((destinatario.email, contenido.asunto, contenido.cuerpo_texto))
        return "fake-provider-id"


@pytest.mark.asyncio
async def test_solicitar_reset_password_envia_email_si_usuario_existe(
    mock_repo: AsyncMock, token_service: TokenServicePort
) -> None:
    usuario = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_email.return_value = usuario
    email_sender = FakeEmailSender()
    handler = SolicitarResetPasswordHandler(
        repo=mock_repo,
        token_service=token_service,
        email_sender=email_sender,
        frontend_base_url="http://localhost:5173",
    )

    await handler.handle(SolicitarResetPasswordCommand(email=usuario.email))

    assert len(email_sender.enviados) == 1
    destinatario, asunto, cuerpo = email_sender.enviados[0]
    assert destinatario == usuario.email
    assert asunto == "Recuperar contraseña de AtaraxiaDive"
    assert "/reset-password?token=" in cuerpo


@pytest.mark.asyncio
async def test_solicitar_reset_password_no_filtra_usuario_inexistente(
    mock_repo: AsyncMock, token_service: TokenServicePort
) -> None:
    mock_repo.find_by_email.return_value = None
    email_sender = FakeEmailSender()
    handler = SolicitarResetPasswordHandler(
        repo=mock_repo,
        token_service=token_service,
        email_sender=email_sender,
        frontend_base_url="http://localhost:5173",
    )

    await handler.handle(SolicitarResetPasswordCommand(email="nadie@test.com"))

    assert email_sender.enviados == []


@pytest.mark.asyncio
async def test_reset_password_exitoso(
    mock_repo: AsyncMock, token_service: TokenServicePort, password_hasher: PasswordHashingPort
) -> None:
    usuario = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_email.return_value = usuario
    handler = ResetPasswordHandler(mock_repo, token_service, password_hasher)
    token = token_service.generate_reset_token(usuario.email)

    await handler.handle(ResetPasswordCommand(token=token, password_nueva="NuevaPass456"))

    assert password_hasher.verify("NuevaPass456", usuario.password_hash)
    mock_repo.save.assert_called_once_with(usuario)


@pytest.mark.asyncio
async def test_reset_password_rechaza_token_de_sesion(
    mock_repo: AsyncMock, token_service: TokenServicePort, password_hasher: PasswordHashingPort
) -> None:
    usuario = _make_usuario("juez@test.com", "clave1234")
    handler = ResetPasswordHandler(mock_repo, token_service, password_hasher)
    token = token_service.generate(usuario)

    with pytest.raises(TokenResetInvalido):
        await handler.handle(ResetPasswordCommand(token=token, password_nueva="NuevaPass456"))


@pytest.mark.asyncio
async def test_reset_password_rechaza_password_corta(
    mock_repo: AsyncMock, token_service: TokenServicePort, password_hasher: PasswordHashingPort
) -> None:
    handler = ResetPasswordHandler(mock_repo, token_service, password_hasher)

    with pytest.raises(PasswordDemasiadoCorto):
        await handler.handle(ResetPasswordCommand(token="fake", password_nueva="short"))


# ── AutenticarUsuarioHandler ──────────────────────────────────────────────────


def _make_usuario(email: str, password: str, rol: Rol = Rol.JUEZ, activo: bool = True) -> Usuario:
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    return Usuario(uuid.uuid4(), "Test", "Usuario", email, hashed, rol, activo)


@pytest.mark.asyncio
async def test_autenticar_exitoso_retorna_token(
    mock_repo: AsyncMock,
    token_service: TokenServicePort,
    password_hasher: PasswordHashingPort,
) -> None:
    u = _make_usuario("juez@test.com", "clave1234", Rol.JUEZ)
    mock_repo.find_by_email.return_value = u
    handler = AutenticarUsuarioHandler(mock_repo, token_service, password_hasher)
    cmd = AutenticarUsuarioCommand(email="juez@test.com", password="clave1234")
    result = await handler.handle(cmd)
    assert isinstance(result, TokenResponse)
    assert result.token_type == "bearer"
    assert len(result.access_token) > 0


@pytest.mark.asyncio
async def test_autenticar_password_incorrecto_lanza_excepcion(
    mock_repo: AsyncMock,
    token_service: TokenServicePort,
    password_hasher: PasswordHashingPort,
) -> None:
    u = _make_usuario("juez@test.com", "clave1234")
    mock_repo.find_by_email.return_value = u
    handler = AutenticarUsuarioHandler(mock_repo, token_service, password_hasher)
    cmd = AutenticarUsuarioCommand(email="juez@test.com", password="wrongpass")
    with pytest.raises(CredencialesInvalidas):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_autenticar_email_inexistente_lanza_excepcion(
    mock_repo: AsyncMock,
    token_service: TokenServicePort,
    password_hasher: PasswordHashingPort,
) -> None:
    mock_repo.find_by_email.return_value = None
    handler = AutenticarUsuarioHandler(mock_repo, token_service, password_hasher)
    cmd = AutenticarUsuarioCommand(email="nope@test.com", password="cualquier1")
    with pytest.raises(CredencialesInvalidas):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_autenticar_usuario_inactivo_lanza_excepcion(
    mock_repo: AsyncMock,
    token_service: TokenServicePort,
    password_hasher: PasswordHashingPort,
) -> None:
    u = _make_usuario("juez@test.com", "clave1234", activo=False)
    mock_repo.find_by_email.return_value = u
    handler = AutenticarUsuarioHandler(mock_repo, token_service, password_hasher)
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
    assert payload["nombre"] == "Test"
    assert payload["apellido"] == "Usuario"
    assert payload["rol"] == "ADMIN"


def test_jwt_token_invalido_lanza_excepcion(jwt_service: JWTService) -> None:
    from identidad.domain.exceptions import TokenInvalido

    with pytest.raises(TokenInvalido):
        jwt_service.verify("token.invalido.xxx")


def test_jwt_sin_secret_lanza_value_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("IDENTIDAD_JWT_SECRET", raising=False)
    with pytest.raises(ValueError, match="IDENTIDAD_JWT_SECRET"):
        JWTService()
