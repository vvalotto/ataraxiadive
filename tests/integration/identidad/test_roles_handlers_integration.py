"""Tests de integración — AgregarRol/QuitarRol con SQLite real."""

from __future__ import annotations

import pytest

from identidad.application.commands.agregar_rol_usuario import (
    AgregarRolUsuarioCommand,
    AgregarRolUsuarioHandler,
)
from identidad.application.commands.quitar_rol_usuario import (
    QuitarRolUsuarioCommand,
    QuitarRolUsuarioHandler,
)
from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.domain.exceptions import (
    RolNoEncontrado,
    RolNoRemovible,
    RolYaAsignado,
    UltimoRolNoRemovible,
)
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.jwt_service import JWTService
from identidad.infrastructure.repositories.sqlite_usuario_repository import (
    SQLiteUsuarioRepository,
)


class _NoopEmailSender:
    async def enviar(self, destinatario, contenido):  # type: ignore[no-untyped-def]
        return "noop"


@pytest.fixture
def repo(tmp_path, monkeypatch):  # type: ignore[no-untyped-def]
    db_path = str(tmp_path / "test_roles.db")
    monkeypatch.setenv("IDENTIDAD_DB_PATH", db_path)
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-roles-32chars-ok!!")
    return SQLiteUsuarioRepository(db_path=db_path)


@pytest.fixture
def token_service(monkeypatch):  # type: ignore[no-untyped-def]
    monkeypatch.setenv("IDENTIDAD_JWT_SECRET", "test-secret-roles-32chars-ok!!")
    return JWTService()


async def _registrar(repo, token_service, email: str, roles: list[Rol]) -> None:
    handler = RegistrarUsuarioHandler(
        repo, BcryptPasswordHasher(), token_service, _NoopEmailSender()
    )
    await handler.handle(
        RegistrarUsuarioCommand(
            nombre="Test",
            apellido="User",
            email=email,
            password="Apnea12345",
            roles=roles,
        )
    )


@pytest.mark.asyncio
async def test_agregar_rol_persiste_en_db(repo, token_service) -> None:  # type: ignore[no-untyped-def]
    await _registrar(repo, token_service, "atleta@email.com", [Rol.ATLETA])
    usuario = await repo.find_by_email("atleta@email.com")
    assert usuario is not None

    handler = AgregarRolUsuarioHandler(repo)
    roles = await handler.handle(
        AgregarRolUsuarioCommand(usuario_id=usuario.usuario_id, nuevo_rol=Rol.JUEZ)
    )
    assert Rol.JUEZ in roles

    recargado = await repo.find_by_id(usuario.usuario_id)
    assert recargado is not None
    assert Rol.JUEZ in recargado.roles
    assert Rol.ATLETA in recargado.roles


@pytest.mark.asyncio
async def test_quitar_rol_persiste_en_db(repo, token_service) -> None:  # type: ignore[no-untyped-def]
    await _registrar(repo, token_service, "multijuez@email.com", [Rol.JUEZ, Rol.ATLETA])
    usuario = await repo.find_by_email("multijuez@email.com")
    assert usuario is not None

    handler = QuitarRolUsuarioHandler(repo)
    roles = await handler.handle(
        QuitarRolUsuarioCommand(usuario_id=usuario.usuario_id, rol=Rol.JUEZ)
    )
    assert Rol.JUEZ not in roles

    recargado = await repo.find_by_id(usuario.usuario_id)
    assert recargado is not None
    assert Rol.JUEZ not in recargado.roles
    assert Rol.ATLETA in recargado.roles


@pytest.mark.asyncio
async def test_agregar_rol_duplicado_lanza_excepcion(repo, token_service) -> None:  # type: ignore[no-untyped-def]
    await _registrar(repo, token_service, "dup@email.com", [Rol.ATLETA])
    usuario = await repo.find_by_email("dup@email.com")
    assert usuario is not None

    handler = AgregarRolUsuarioHandler(repo)
    with pytest.raises(RolYaAsignado):
        await handler.handle(
            AgregarRolUsuarioCommand(usuario_id=usuario.usuario_id, nuevo_rol=Rol.ATLETA)
        )


@pytest.mark.asyncio
async def test_quitar_atleta_lanza_excepcion(repo, token_service) -> None:  # type: ignore[no-untyped-def]
    await _registrar(repo, token_service, "noqattr@email.com", [Rol.ATLETA, Rol.JUEZ])
    usuario = await repo.find_by_email("noqattr@email.com")
    assert usuario is not None

    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(RolNoRemovible):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=usuario.usuario_id, rol=Rol.ATLETA))


@pytest.mark.asyncio
async def test_quitar_rol_no_poseido_lanza_excepcion(repo, token_service) -> None:  # type: ignore[no-untyped-def]
    await _registrar(repo, token_service, "noposeido@email.com", [Rol.ATLETA])
    usuario = await repo.find_by_email("noposeido@email.com")
    assert usuario is not None

    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(RolNoEncontrado):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=usuario.usuario_id, rol=Rol.JUEZ))


@pytest.mark.asyncio
async def test_quitar_unico_rol_lanza_excepcion(repo, token_service) -> None:  # type: ignore[no-untyped-def]
    await _registrar(repo, token_service, "solojuez@email.com", [Rol.JUEZ])
    usuario = await repo.find_by_email("solojuez@email.com")
    assert usuario is not None

    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(UltimoRolNoRemovible):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=usuario.usuario_id, rol=Rol.JUEZ))
