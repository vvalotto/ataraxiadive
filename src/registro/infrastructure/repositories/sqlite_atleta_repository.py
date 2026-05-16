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
    email            TEXT NOT NULL UNIQUE,
    fecha_nacimiento TEXT,
    categoria        TEXT,
    club             TEXT,
    brevet           TEXT,
    dni              TEXT,
    telefono         TEXT
)
"""

_SELECT_COLS = (
    "atleta_id, nombre, apellido, email, fecha_nacimiento, "
    "categoria, club, brevet, dni, telefono"
)


class SQLiteAtletaRepository(AtletaRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await self._ensure_columns(conn)
        await conn.commit()

    async def _ensure_columns(self, conn: aiosqlite.Connection) -> None:
        for col in ("dni TEXT", "telefono TEXT"):
            try:
                await conn.execute(f"ALTER TABLE atletas ADD COLUMN {col}")
            except Exception:
                pass
        await self._migrate_fecha_nacimiento_nullable(conn)

    @staticmethod
    async def _migrate_fecha_nacimiento_nullable(conn: aiosqlite.Connection) -> None:
        """Elimina el NOT NULL de fecha_nacimiento si la tabla legacy lo tiene."""
        async with conn.execute("PRAGMA table_info(atletas)") as cur:
            cols = await cur.fetchall()
        # col[1]=name, col[3]=notnull
        fn_col = next((c for c in cols if c[1] == "fecha_nacimiento"), None)
        if fn_col is None or fn_col[3] == 0:
            return  # ya es nullable o no existe — nada que hacer
        await conn.executescript("""
            CREATE TABLE IF NOT EXISTS atletas_new (
                atleta_id        TEXT PRIMARY KEY,
                nombre           TEXT NOT NULL,
                apellido         TEXT NOT NULL,
                email            TEXT NOT NULL UNIQUE,
                fecha_nacimiento TEXT,
                categoria        TEXT,
                club             TEXT,
                brevet           TEXT,
                dni              TEXT,
                telefono         TEXT
            );
            INSERT OR IGNORE INTO atletas_new
                SELECT atleta_id, nombre, apellido, email, fecha_nacimiento,
                       categoria, club, brevet, dni, telefono
                FROM atletas;
            DROP TABLE atletas;
            ALTER TABLE atletas_new RENAME TO atletas;
        """)

    async def save(self, atleta: Atleta) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO atletas
                    (atleta_id, nombre, apellido, email, fecha_nacimiento,
                     categoria, club, brevet, dni, telefono)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(atleta.atleta_id),
                    atleta.nombre,
                    atleta.apellido,
                    atleta.email,
                    atleta.fecha_nacimiento.isoformat() if atleta.fecha_nacimiento else None,
                    str(atleta.categoria) if atleta.categoria is not None else None,
                    atleta.club,
                    atleta.brevet,
                    atleta.dni,
                    atleta.telefono,
                ),
            )
            await conn.commit()

    async def find_by_id(self, atleta_id: UUID) -> Atleta | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                f"SELECT {_SELECT_COLS} FROM atletas WHERE atleta_id = ?",
                (str(atleta_id),),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_atleta(row) if row else None

    async def find_by_email(self, email: str) -> Atleta | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            async with conn.execute(
                f"SELECT {_SELECT_COLS} FROM atletas WHERE email = ?",
                (email,),
            ) as cursor:
                row = await cursor.fetchone()
        return self._row_to_atleta(row) if row else None

    @staticmethod
    def _row_to_atleta(row: tuple) -> Atleta:
        # 0:atleta_id 1:nombre 2:apellido 3:email 4:fecha_nacimiento
        # 5:categoria 6:club 7:brevet 8:dni 9:telefono
        return Atleta(
            atleta_id=UUID(row[0]),
            nombre=row[1],
            apellido=row[2],
            email=row[3],
            fecha_nacimiento=date.fromisoformat(row[4]) if row[4] else None,
            categoria=Categoria(row[5]) if row[5] is not None else None,
            club=row[6],
            brevet=row[7],
            dni=row[8],
            telefono=row[9],
        )
