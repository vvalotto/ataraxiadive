from __future__ import annotations

import os
from uuid import UUID

import aiosqlite

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS usuarios (
    usuario_id    TEXT PRIMARY KEY,
    email         TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    rol           TEXT NOT NULL,
    activo        INTEGER NOT NULL DEFAULT 1
)
"""


class SQLiteUsuarioRepository(UsuarioRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("IDENTIDAD_DB_PATH", "data/identidad.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await conn.commit()

    async def save(self, usuario: Usuario) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO usuarios
                    (usuario_id, email, password_hash, rol, activo)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    str(usuario.usuario_id),
                    usuario.email,
                    usuario.password_hash,
                    usuario.rol.value,
                    1 if usuario.activo else 0,
                ),
            )
            await conn.commit()

    async def find_by_id(self, usuario_id: UUID) -> Usuario | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                "SELECT usuario_id, email, password_hash, rol, activo FROM usuarios WHERE usuario_id = ?",
                (str(usuario_id),),
            ) as cursor:
                row = await cursor.fetchone()
        return _row_to_usuario(row) if row else None

    async def find_by_email(self, email: str) -> Usuario | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                "SELECT usuario_id, email, password_hash, rol, activo FROM usuarios WHERE email = ?",
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
        return _row_to_usuario(row) if row else None


def _row_to_usuario(row: tuple) -> Usuario:  # type: ignore[type-arg]
    usuario_id, email, password_hash, rol, activo = row
    return Usuario(
        usuario_id=UUID(usuario_id),
        email=email,
        password_hash=password_hash,
        rol=Rol(rol),
        activo=bool(activo),
    )
