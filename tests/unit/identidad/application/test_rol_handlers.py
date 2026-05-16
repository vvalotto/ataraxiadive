"""Tests unitarios — AgregarRolUsuarioHandler y QuitarRolUsuarioHandler."""

from __future__ import annotations

import uuid

import pytest

from identidad.application.commands.agregar_rol_usuario import (
    AgregarRolUsuarioCommand,
    AgregarRolUsuarioHandler,
)
from identidad.application.commands.quitar_rol_usuario import (
    QuitarRolUsuarioCommand,
    QuitarRolUsuarioHandler,
)
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import (
    RolNoEncontrado,
    RolNoPermitido,
    RolNoRemovible,
    RolYaAsignado,
    UltimoRolNoRemovible,
    UsuarioNoEncontrado,
)
from identidad.domain.value_objects.rol import Rol


class FakeRepo:
    def __init__(self, usuario: Usuario | None = None) -> None:
        self._usuario = usuario
        self.saved: Usuario | None = None

    async def find_by_id(self, usuario_id: uuid.UUID) -> Usuario | None:
        return self._usuario

    async def save(self, usuario: Usuario) -> None:
        self.saved = usuario

    async def find_by_email(self, email: str) -> Usuario | None:
        return None

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        return []

    async def list_all(self) -> list[Usuario]:
        return []


def _usuario(roles: list[Rol]) -> Usuario:
    return Usuario(
        usuario_id=uuid.uuid4(),
        nombre="Test",
        apellido="User",
        email="test@email.com",
        password_hash="hash",
        roles=roles,
    )


# ── AgregarRolUsuarioHandler ──────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_agregar_rol_exitoso() -> None:
    u = _usuario([Rol.ATLETA])
    repo = FakeRepo(u)
    handler = AgregarRolUsuarioHandler(repo)
    roles = await handler.handle(
        AgregarRolUsuarioCommand(usuario_id=u.usuario_id, nuevo_rol=Rol.JUEZ)
    )
    assert Rol.JUEZ in roles
    assert Rol.ATLETA in roles
    assert repo.saved is not None


@pytest.mark.asyncio
async def test_agregar_rol_ya_asignado_lanza_excepcion() -> None:
    u = _usuario([Rol.ATLETA, Rol.JUEZ])
    repo = FakeRepo(u)
    handler = AgregarRolUsuarioHandler(repo)
    with pytest.raises(RolYaAsignado):
        await handler.handle(AgregarRolUsuarioCommand(usuario_id=u.usuario_id, nuevo_rol=Rol.JUEZ))


@pytest.mark.asyncio
async def test_agregar_rol_admin_lanza_excepcion() -> None:
    u = _usuario([Rol.ATLETA])
    repo = FakeRepo(u)
    handler = AgregarRolUsuarioHandler(repo)
    with pytest.raises(RolNoPermitido):
        await handler.handle(AgregarRolUsuarioCommand(usuario_id=u.usuario_id, nuevo_rol=Rol.ADMIN))


@pytest.mark.asyncio
async def test_agregar_rol_usuario_no_encontrado() -> None:
    repo = FakeRepo(None)
    handler = AgregarRolUsuarioHandler(repo)
    with pytest.raises(UsuarioNoEncontrado):
        await handler.handle(AgregarRolUsuarioCommand(usuario_id=uuid.uuid4(), nuevo_rol=Rol.JUEZ))


# ── QuitarRolUsuarioHandler ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_quitar_rol_exitoso() -> None:
    u = _usuario([Rol.JUEZ, Rol.ATLETA])
    repo = FakeRepo(u)
    handler = QuitarRolUsuarioHandler(repo)
    roles = await handler.handle(QuitarRolUsuarioCommand(usuario_id=u.usuario_id, rol=Rol.JUEZ))
    assert Rol.JUEZ not in roles
    assert Rol.ATLETA in roles
    assert repo.saved is not None


@pytest.mark.asyncio
async def test_quitar_rol_atleta_lanza_excepcion() -> None:
    u = _usuario([Rol.ATLETA, Rol.JUEZ])
    repo = FakeRepo(u)
    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(RolNoRemovible):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=u.usuario_id, rol=Rol.ATLETA))


@pytest.mark.asyncio
async def test_quitar_rol_no_poseido_lanza_excepcion() -> None:
    u = _usuario([Rol.ATLETA])
    repo = FakeRepo(u)
    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(RolNoEncontrado):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=u.usuario_id, rol=Rol.JUEZ))


@pytest.mark.asyncio
async def test_quitar_unico_rol_lanza_excepcion() -> None:
    u = _usuario([Rol.JUEZ])
    repo = FakeRepo(u)
    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(UltimoRolNoRemovible):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=u.usuario_id, rol=Rol.JUEZ))


@pytest.mark.asyncio
async def test_quitar_rol_usuario_no_encontrado() -> None:
    repo = FakeRepo(None)
    handler = QuitarRolUsuarioHandler(repo)
    with pytest.raises(UsuarioNoEncontrado):
        await handler.handle(QuitarRolUsuarioCommand(usuario_id=uuid.uuid4(), rol=Rol.JUEZ))
