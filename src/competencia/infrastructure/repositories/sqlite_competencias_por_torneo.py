"""Proyeccion SQLite para competencias asociadas a un torneo."""

from __future__ import annotations

import os
from uuid import UUID

import aiosqlite

from competencia.domain.ports.competencias_por_torneo_port import (
    CompetenciaPorTorneoRecord,
    CompetenciasPorTorneoPort,
)

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS competencias_por_torneo (
    competencia_id TEXT PRIMARY KEY,
    torneo_id      TEXT NOT NULL,
    disciplina     TEXT NOT NULL
)
"""

_CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_competencias_por_torneo_torneo_id
ON competencias_por_torneo(torneo_id)
"""


class SQLiteCompetenciasPorTorneo(CompetenciasPorTorneoPort):
    """Implementacion SQLite de la proyeccion competencias por torneo."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        await conn.execute(_CREATE_INDEX)
        await conn.commit()

    async def guardar(
        self,
        competencia_id: UUID,
        disciplina: str,
        torneo_id: UUID,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT INTO competencias_por_torneo (competencia_id, torneo_id, disciplina)
                VALUES (?, ?, ?)
                ON CONFLICT(competencia_id) DO UPDATE SET
                    torneo_id = excluded.torneo_id,
                    disciplina = excluded.disciplina
                """,
                (str(competencia_id), str(torneo_id), disciplina),
            )
            await conn.commit()

    async def listar_por_torneo(self, torneo_id: UUID) -> list[CompetenciaPorTorneoRecord]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                """
                SELECT competencia_id, disciplina, torneo_id
                FROM competencias_por_torneo
                WHERE torneo_id = ?
                ORDER BY disciplina
                """,
                (str(torneo_id),),
            ) as cursor:
                rows = await cursor.fetchall()
        return [
            CompetenciaPorTorneoRecord(
                competencia_id=UUID(row["competencia_id"]),
                disciplina=row["disciplina"],
                torneo_id=UUID(row["torneo_id"]),
            )
            for row in rows
        ]
