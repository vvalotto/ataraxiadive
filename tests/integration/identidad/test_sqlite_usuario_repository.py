"""Tests de integración — SQLiteUsuarioRepository con aiosqlite real."""

from __future__ import annotations

import tempfile
import uuid

import pytest

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.repositories.sqlite_usuario_repository import SQLiteUsuarioRepository


@pytest.fixture
def repo() -> SQLiteUsuarioRepository:
    db = tempfile.mktemp(suffix=".db")
    return SQLiteUsuarioRepository(db_path=db)


def _usuario(
    email: str = "test@test.com", rol: Rol = Rol.ORGANIZADOR, activo: bool = True
) -> Usuario:
    return Usuario(
        usuario_id=uuid.uuid4(),
        email=email,
        password_hash="$2b$12$fakehash",
        rol=rol,
        activo=activo,
    )


@pytest.mark.asyncio
async def test_save_y_find_by_id(repo: SQLiteUsuarioRepository) -> None:
    u = _usuario()
    await repo.save(u)
    resultado = await repo.find_by_id(u.usuario_id)
    assert resultado is not None
    assert resultado.usuario_id == u.usuario_id
    assert resultado.email == u.email
    assert resultado.rol == Rol.ORGANIZADOR
    assert resultado.activo is True


@pytest.mark.asyncio
async def test_find_by_email(repo: SQLiteUsuarioRepository) -> None:
    u = _usuario(email="buscar@test.com")
    await repo.save(u)
    resultado = await repo.find_by_email("buscar@test.com")
    assert resultado is not None
    assert resultado.email == "buscar@test.com"


@pytest.mark.asyncio
async def test_find_by_email_inexistente_retorna_none(repo: SQLiteUsuarioRepository) -> None:
    resultado = await repo.find_by_email("nope@test.com")
    assert resultado is None


@pytest.mark.asyncio
async def test_find_by_id_inexistente_retorna_none(repo: SQLiteUsuarioRepository) -> None:
    resultado = await repo.find_by_id(uuid.uuid4())
    assert resultado is None


@pytest.mark.asyncio
async def test_save_upsert_actualiza_registro(repo: SQLiteUsuarioRepository) -> None:
    u = _usuario()
    await repo.save(u)
    u_inactivo = Usuario(u.usuario_id, u.email, u.password_hash, u.rol, activo=False)
    await repo.save(u_inactivo)
    resultado = await repo.find_by_id(u.usuario_id)
    assert resultado is not None
    assert resultado.activo is False


@pytest.mark.asyncio
async def test_save_persiste_rol_correctamente(repo: SQLiteUsuarioRepository) -> None:
    u = _usuario(rol=Rol.ADMIN)
    await repo.save(u)
    resultado = await repo.find_by_id(u.usuario_id)
    assert resultado is not None
    assert resultado.rol == Rol.ADMIN
