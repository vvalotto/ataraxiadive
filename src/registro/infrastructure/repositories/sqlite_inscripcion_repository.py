from __future__ import annotations

import json
import os
from uuid import UUID

import aiosqlite

from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS inscripciones (
    inscripcion_id    TEXT PRIMARY KEY,
    atleta_id         TEXT NOT NULL,
    torneo_id         TEXT NOT NULL,
    disciplinas       TEXT NOT NULL,
    ap_por_disciplina TEXT NOT NULL DEFAULT '{}',
    estado            TEXT NOT NULL,
    fecha_inscripcion TEXT NOT NULL,
    apto_medico_path  TEXT,
    constancia_pago_path TEXT
)
"""


class SQLiteInscripcionRepository(InscripcionRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await _ensure_table(conn)

    async def _ensure_schema(self, conn: aiosqlite.Connection) -> None:
        await _ensure_schema(conn)

    async def save(self, inscripcion: Inscripcion) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            await conn.execute(
                _UPSERT_INSCRIPCION,
                _inscripcion_to_values(inscripcion),
            )
            await conn.commit()

    async def find_by_id(self, inscripcion_id: UUID) -> Inscripcion | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM inscripciones WHERE inscripcion_id = ?",
                (str(inscripcion_id),),
            ) as cursor:
                row = await cursor.fetchone()
                return self._row_to_inscripcion(row) if row else None

    async def find_by_atleta_y_torneo(self, atleta_id: UUID, torneo_id: UUID) -> Inscripcion | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM inscripciones WHERE atleta_id = ? AND torneo_id = ?",
                (str(atleta_id), str(torneo_id)),
            ) as cursor:
                row = await cursor.fetchone()
                return self._row_to_inscripcion(row) if row else None

    async def find_by_torneo(self, torneo_id: UUID) -> list[Inscripcion]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM inscripciones WHERE torneo_id = ?", (str(torneo_id),)
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_inscripcion(row) for row in rows]

    async def find_active_by_torneo(self, torneo_id: UUID) -> list[Inscripcion]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                """
                SELECT * FROM inscripciones
                WHERE torneo_id = ? AND estado != ?
                ORDER BY fecha_inscripcion ASC
                """,
                (str(torneo_id), EstadoInscripcion.CANCELADA.value),
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_inscripcion(row) for row in rows]

    async def find_by_atleta(self, atleta_id: UUID) -> list[Inscripcion]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_schema(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                """
                SELECT * FROM inscripciones
                WHERE atleta_id = ?
                ORDER BY fecha_inscripcion DESC
                """,
                (str(atleta_id),),
            ) as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_inscripcion(row) for row in rows]

    def _row_to_inscripcion(self, row: aiosqlite.Row) -> Inscripcion:
        return Inscripcion.from_row(_row_to_dict(row))


def _row_to_dict(row: aiosqlite.Row) -> dict[str, object]:
    return {key: row[key] for key in row.keys()}


_UPSERT_INSCRIPCION = """
INSERT OR REPLACE INTO inscripciones
    (
        inscripcion_id,
        atleta_id,
        torneo_id,
        disciplinas,
        ap_por_disciplina,
        estado,
        fecha_inscripcion,
        apto_medico_path,
        constancia_pago_path
    )
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""


async def _ensure_table(conn: aiosqlite.Connection) -> None:
    await conn.execute(_CREATE_TABLE)
    await conn.commit()


async def _ensure_schema(conn: aiosqlite.Connection) -> None:
    await conn.execute(_CREATE_TABLE)
    conn.row_factory = aiosqlite.Row
    async with conn.execute("PRAGMA table_info(inscripciones)") as cursor:
        columns = [row["name"] for row in await cursor.fetchall()]
    if "ap_por_disciplina" not in columns:
        await conn.execute(
            "ALTER TABLE inscripciones ADD COLUMN ap_por_disciplina TEXT NOT NULL DEFAULT '{}'"
        )
    if "apto_medico_path" not in columns:
        await conn.execute("ALTER TABLE inscripciones ADD COLUMN apto_medico_path TEXT")
    if "constancia_pago_path" not in columns:
        await conn.execute("ALTER TABLE inscripciones ADD COLUMN constancia_pago_path TEXT")
    await conn.commit()


def _inscripcion_to_values(inscripcion: Inscripcion) -> tuple[object, ...]:
    return (
        str(inscripcion.inscripcion_id),
        str(inscripcion.atleta_id),
        str(inscripcion.torneo_id),
        json.dumps([d.value for d in inscripcion.disciplinas]),
        json.dumps(
            {
                disciplina.value: {
                    "valor": str(ap.valor),
                    "unidad": ap.unidad.value,
                }
                for disciplina, ap in inscripcion.ap_por_disciplina.items()
            }
        ),
        inscripcion.estado.value,
        inscripcion.fecha_inscripcion.isoformat(),
        inscripcion.apto_medico_path,
        inscripcion.constancia_pago_path,
    )
