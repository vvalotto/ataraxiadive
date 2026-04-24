"""Tests de integración — SQLiteUsuarioRepository con aiosqlite real."""

from __future__ import annotations

import tempfile
import uuid
from pathlib import Path

import aiosqlite

import pytest

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.repositories.sqlite_usuario_repository import SQLiteUsuarioRepository


@pytest.fixture
def repo() -> SQLiteUsuarioRepository:
    db = tempfile.mktemp(suffix=".db")
    return SQLiteUsuarioRepository(db_path=db)


def _usuario(
    email: str = "test@test.com",
    rol: Rol = Rol.ORGANIZADOR,
    activo: bool = True,
    nombre: str = "Ana",
    apellido: str = "Garcia",
) -> Usuario:
    return Usuario(
        usuario_id=uuid.uuid4(),
        nombre=nombre,
        apellido=apellido,
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
    assert resultado.nombre == u.nombre
    assert resultado.apellido == u.apellido
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
    u_inactivo = Usuario(
        u.usuario_id,
        u.nombre,
        u.apellido,
        u.email,
        u.password_hash,
        u.rol,
        activo=False,
    )
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


@pytest.mark.asyncio
async def test_list_by_rol_filtra_y_ordena_por_email(repo: SQLiteUsuarioRepository) -> None:
    await repo.save(_usuario(email="z-juez@test.com", rol=Rol.JUEZ))
    await repo.save(_usuario(email="a-juez@test.com", rol=Rol.JUEZ))
    await repo.save(_usuario(email="org@test.com", rol=Rol.ORGANIZADOR))

    jueces = await repo.list_by_rol(Rol.JUEZ)

    assert [usuario.email for usuario in jueces] == ["a-juez@test.com", "z-juez@test.com"]


@pytest.mark.asyncio
async def test_list_all_devuelve_todos_ordenados_por_rol_y_email(
    repo: SQLiteUsuarioRepository,
) -> None:
    await repo.save(_usuario(email="z-juez@test.com", rol=Rol.JUEZ))
    await repo.save(_usuario(email="org@test.com", rol=Rol.ORGANIZADOR))
    await repo.save(_usuario(email="atleta@test.com", rol=Rol.ATLETA))
    await repo.save(_usuario(email="a-juez@test.com", rol=Rol.JUEZ))

    usuarios = await repo.list_all()

    assert [(usuario.rol, usuario.email) for usuario in usuarios] == [
        (Rol.ATLETA, "atleta@test.com"),
        (Rol.JUEZ, "a-juez@test.com"),
        (Rol.JUEZ, "z-juez@test.com"),
        (Rol.ORGANIZADOR, "org@test.com"),
    ]


@pytest.mark.asyncio
async def test_ensure_table_migra_columnas_nombre_y_apellido() -> None:
    db_path = Path(tempfile.mktemp(suffix=".db"))
    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(
            """
            CREATE TABLE usuarios (
                usuario_id TEXT PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1
            )
            """
        )
        await conn.commit()

    repo = SQLiteUsuarioRepository(db_path=str(db_path))
    usuario = _usuario(email="migrado@test.com")
    await repo.save(usuario)

    resultado = await repo.find_by_email("migrado@test.com")

    assert resultado is not None
    assert resultado.nombre == "Ana"
    assert resultado.apellido == "Garcia"
