from __future__ import annotations

import os
from uuid import UUID

import aiosqlite

from registro.domain.aggregates.organizador import Organizador
from registro.domain.ports.organizador_repository_port import OrganizadorRepositoryPort

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS organizadores (
    organizador_id      TEXT PRIMARY KEY,
    email               TEXT NOT NULL UNIQUE,
    nombre_organizacion TEXT
)
"""

_SELECT_COLS = "organizador_id, email, nombre_organizacion"


class SQLiteOrganizadorRepository(OrganizadorRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await conn.commit()

    async def save(self, organizador: Organizador) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO organizadores
                    (organizador_id, email, nombre_organizacion)
                VALUES (?, ?, ?)
                """,
                (
                    str(organizador.organizador_id),
                    organizador.email,
                    organizador.nombre_organizacion,
                ),
            )
            await conn.commit()

    async def find_by_id(self, organizador_id: UUID) -> Organizador | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                f"SELECT {_SELECT_COLS} FROM organizadores WHERE organizador_id = ?",
                (str(organizador_id),),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_organizador(row) if row else None

    async def find_by_email(self, email: str) -> Organizador | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                f"SELECT {_SELECT_COLS} FROM organizadores WHERE email = ?",
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_organizador(row) if row else None

    @staticmethod
    def _row_to_organizador(row: tuple) -> Organizador:
        # 0:organizador_id 1:email 2:nombre_organizacion
        return Organizador(
            organizador_id=UUID(row[0]),
            email=row[1],
            nombre_organizacion=row[2],
        )
