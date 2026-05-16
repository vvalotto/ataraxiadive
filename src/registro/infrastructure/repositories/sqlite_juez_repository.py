from __future__ import annotations

import os
from uuid import UUID

import aiosqlite

from registro.domain.aggregates.juez import Juez
from registro.domain.ports.juez_repository_port import JuezRepositoryPort

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS jueces (
    juez_id          TEXT PRIMARY KEY,
    email            TEXT NOT NULL UNIQUE,
    numero_licencia  TEXT,
    federacion       TEXT
)
"""

_SELECT_COLS = "juez_id, email, numero_licencia, federacion"


class SQLiteJuezRepository(JuezRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await conn.commit()

    async def save(self, juez: Juez) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO jueces
                    (juez_id, email, numero_licencia, federacion)
                VALUES (?, ?, ?, ?)
                """,
                (
                    str(juez.juez_id),
                    juez.email,
                    juez.numero_licencia,
                    juez.federacion,
                ),
            )
            await conn.commit()

    async def find_by_id(self, juez_id: UUID) -> Juez | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                f"SELECT {_SELECT_COLS} FROM jueces WHERE juez_id = ?",
                (str(juez_id),),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_juez(row) if row else None

    async def find_by_email(self, email: str) -> Juez | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                f"SELECT {_SELECT_COLS} FROM jueces WHERE email = ?",
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_juez(row) if row else None

    @staticmethod
    def _row_to_juez(row: tuple) -> Juez:
        # 0:juez_id 1:email 2:numero_licencia 3:federacion
        return Juez(
            juez_id=UUID(row[0]),
            email=row[1],
            numero_licencia=row[2],
            federacion=row[3],
        )
