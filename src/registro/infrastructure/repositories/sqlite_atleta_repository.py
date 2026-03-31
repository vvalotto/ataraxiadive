from __future__ import annotations

import os
from datetime import date
from uuid import UUID

import aiosqlite

from registro.domain.aggregates.atleta import Atleta
from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.value_objects.categoria import Categoria

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS atletas (
    atleta_id        TEXT PRIMARY KEY,
    nombre           TEXT NOT NULL,
    apellido         TEXT NOT NULL,
    email            TEXT NOT NULL,
    fecha_nacimiento TEXT NOT NULL,
    categoria        TEXT NOT NULL,
    brevet           TEXT
)
"""


class SQLiteAtletaRepository(AtletaRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await conn.commit()

    async def save(self, atleta: Atleta) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO atletas
                    (atleta_id, nombre, apellido, email, fecha_nacimiento, categoria, brevet)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(atleta.atleta_id),
                    atleta.nombre,
                    atleta.apellido,
                    atleta.email,
                    atleta.fecha_nacimiento.isoformat(),
                    str(atleta.categoria),
                    atleta.brevet,
                ),
            )
            await conn.commit()

    async def find_by_id(self, atleta_id: UUID) -> Atleta | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                "SELECT atleta_id, nombre, apellido, email, fecha_nacimiento, categoria, brevet "
                "FROM atletas WHERE atleta_id = ?",
                (str(atleta_id),),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_atleta(row) if row else None

    async def find_by_email(self, email: str) -> Atleta | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                "SELECT atleta_id, nombre, apellido, email, fecha_nacimiento, categoria, brevet "
                "FROM atletas WHERE email = ?",
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_atleta(row) if row else None

    @staticmethod
    def _row_to_atleta(row: tuple) -> Atleta:
        return Atleta(
            atleta_id=UUID(row[0]),
            nombre=row[1],
            apellido=row[2],
            email=row[3],
            fecha_nacimiento=date.fromisoformat(row[4]),
            categoria=Categoria(row[5]),
            brevet=row[6],
        )
