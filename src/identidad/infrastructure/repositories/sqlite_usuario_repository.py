from __future__ import annotations

import json
import os
from uuid import UUID

import aiosqlite

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id    TEXT PRIMARY KEY,
    nombre        TEXT NOT NULL DEFAULT '',
    apellido      TEXT NOT NULL DEFAULT '',
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol           TEXT NOT NULL DEFAULT 'ATLETA',
    activo        INTEGER NOT NULL DEFAULT 1,
    roles         TEXT NOT NULL DEFAULT '["ATLETA"]'
)
"""


class SQLiteUsuarioRepository(UsuarioRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("IDENTIDAD_DB_PATH", "data/identidad.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await _ensure_column(conn, "nombre", "TEXT NOT NULL DEFAULT ''")
        await _ensure_column(conn, "apellido", "TEXT NOT NULL DEFAULT ''")
        await _ensure_column(conn, "roles", "TEXT NOT NULL DEFAULT '[\"ATLETA\"]'")
        await _migrate_rol_to_roles(conn)
        await conn.commit()

    async def save(self, usuario: Usuario) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO usuarios
                    (usuario_id, nombre, apellido, email, password_hash, rol, activo, roles)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(usuario.usuario_id),
                    usuario.nombre,
                    usuario.apellido,
                    usuario.email,
                    usuario.password_hash,
                    usuario.roles[0].value,
                    1 if usuario.activo else 0,
                    _serialize_roles(usuario.roles),
                ),
            )
            await conn.commit()

    async def find_by_id(self, usuario_id: UUID) -> Usuario | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                """
                SELECT usuario_id, nombre, apellido, email, password_hash, activo, roles
                FROM usuarios
                WHERE usuario_id = ?
                """,
                (str(usuario_id),),
            ) as cursor:
                row = await cursor.fetchone()
        return _row_to_usuario(row) if row else None

    async def find_by_email(self, email: str) -> Usuario | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                """
                SELECT usuario_id, nombre, apellido, email, password_hash, activo, roles
                FROM usuarios
                WHERE email = ?
                """,
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
        return _row_to_usuario(row) if row else None

    async def list_by_rol(self, rol: Rol) -> list[Usuario]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                """
                SELECT usuario_id, nombre, apellido, email, password_hash, activo, roles
                FROM usuarios
                WHERE roles LIKE ?
                ORDER BY email
                """,
                (f'%"{rol.value}"%',),
            ) as cursor:
                rows = await cursor.fetchall()
        return [_row_to_usuario(row) for row in rows]

    async def list_all(self) -> list[Usuario]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute("""
                SELECT usuario_id, nombre, apellido, email, password_hash, activo, roles
                FROM usuarios
                ORDER BY email
                """) as cursor:
                rows = await cursor.fetchall()
        return [_row_to_usuario(row) for row in rows]


def _serialize_roles(roles: list[Rol]) -> str:
    return json.dumps([r.value for r in roles])


def _deserialize_roles(roles_str: str) -> list[Rol]:
    return [Rol(r) for r in json.loads(roles_str)]


def _row_to_usuario(row: tuple) -> Usuario:  # type: ignore[type-arg]
    usuario_id, nombre, apellido, email, password_hash, activo, roles_str = row
    return Usuario(
        usuario_id=UUID(usuario_id),
        nombre=nombre,
        apellido=apellido,
        email=email,
        password_hash=password_hash,
        roles=_deserialize_roles(roles_str),
        activo=bool(activo),
    )


async def _ensure_column(conn: aiosqlite.Connection, column: str, definition: str) -> None:
    async with conn.execute("PRAGMA table_info(usuarios)") as cursor:
        rows = await cursor.fetchall()
    if any(row[1] == column for row in rows):
        return
    await conn.execute(f"ALTER TABLE usuarios ADD COLUMN {column} {definition}")


async def _migrate_rol_to_roles(conn: aiosqlite.Connection) -> None:
    """Convierte columna legacy 'rol' a 'roles' JSON para filas sin migrar."""
    async with conn.execute("PRAGMA table_info(usuarios)") as cursor:
        cols = {row[1] for row in await cursor.fetchall()}
    if "rol" not in cols or "roles" not in cols:
        return
    # Solo actualiza filas donde roles está en el valor default vacío o mal formado
    await conn.execute("""
        UPDATE usuarios
        SET roles = json_array(rol)
        WHERE roles = '["ATLETA"]' AND rol != 'ATLETA'
        """)
    await conn.execute("""
        UPDATE usuarios
        SET roles = json_array(rol)
        WHERE json_valid(roles) = 0
        """)
