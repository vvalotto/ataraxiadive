from __future__ import annotations

import json
import os
from datetime import date
from uuid import UUID

import aiosqlite

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort
from torneo.domain.value_objects.disciplina_torneo import DisciplinaTorneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS torneos (
    torneo_id          TEXT PRIMARY KEY,
    nombre             TEXT NOT NULL,
    descripcion        TEXT NOT NULL,
    fecha_inicio       TEXT NOT NULL,
    fecha_fin          TEXT NOT NULL,
    sede               TEXT NOT NULL,
    entidad            TEXT NOT NULL,
    estado             TEXT NOT NULL,
    disciplinas_torneo TEXT NOT NULL DEFAULT '[]'
)
"""

_ADD_DISCIPLINAS_COLUMN = """
ALTER TABLE torneos ADD COLUMN disciplinas_torneo TEXT NOT NULL DEFAULT '[]'
"""


class SQLiteTorneoRepository(TorneoRepositoryPort):
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("TORNEO_DB_PATH", "data/torneo.db")

    async def _ensure_table(self, conn: aiosqlite.Connection) -> None:
        await conn.execute(_CREATE_TABLE)
        # Migración: agregar columna si existe la tabla sin ella
        try:
            await conn.execute(_ADD_DISCIPLINAS_COLUMN)
        except Exception:
            pass  # La columna ya existe
        await conn.commit()

    async def save(self, torneo: Torneo) -> None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            await conn.execute(
                """
                INSERT OR REPLACE INTO torneos
                    (torneo_id, nombre, descripcion, fecha_inicio, fecha_fin,
                     sede, entidad, estado, disciplinas_torneo)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._torneo_to_row(torneo),
            )
            await conn.commit()

    async def find_by_id(self, torneo_id: UUID) -> Torneo | None:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT * FROM torneos WHERE torneo_id = ?", (str(torneo_id),)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return None
                return self._row_to_torneo(row)

    async def find_all(self) -> list[Torneo]:
        async with aiosqlite.connect(self._db_path) as conn:
            await self._ensure_table(conn)
            conn.row_factory = aiosqlite.Row
            async with conn.execute("SELECT * FROM torneos") as cursor:
                rows = await cursor.fetchall()
                return [self._row_to_torneo(row) for row in rows]

    def _row_to_torneo(self, row: aiosqlite.Row) -> Torneo:
        return Torneo(
            torneo_id=UUID(row["torneo_id"]),
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            fecha_inicio=date.fromisoformat(row["fecha_inicio"]),
            fecha_fin=date.fromisoformat(row["fecha_fin"]),
            sede=self._deserialize_sede(row["sede"]),
            entidad_organizadora=self._deserialize_entidad(row["entidad"]),
            estado=EstadoTorneo(row["estado"]),
            disciplinas_torneo=self._deserialize_disciplinas(row["disciplinas_torneo"]),
        )

    def _torneo_to_row(self, torneo: Torneo) -> tuple[str, str, str, str, str, str, str, str, str]:
        return (
            str(torneo.torneo_id),
            torneo.nombre,
            torneo.descripcion,
            torneo.fecha_inicio.isoformat(),
            torneo.fecha_fin.isoformat(),
            self._serialize_sede(torneo.sede),
            self._serialize_entidad(torneo.entidad_organizadora),
            torneo.estado.value,
            self._serialize_disciplinas(torneo.disciplinas_torneo),
        )

    @staticmethod
    def _serialize_sede(sede: Sede) -> str:
        return json.dumps(
            {
                "nombre": sede.nombre,
                "ciudad": sede.ciudad,
                "pais": sede.pais,
            }
        )

    @staticmethod
    def _serialize_entidad(entidad: EntidadOrganizadora) -> str:
        return json.dumps(
            {
                "nombre": entidad.nombre,
                "tipo": entidad.tipo,
            }
        )

    @staticmethod
    def _serialize_disciplinas(disciplinas: list[DisciplinaTorneo]) -> str:
        return json.dumps([disciplina.to_dict() for disciplina in disciplinas])

    @staticmethod
    def _deserialize_sede(raw: str) -> Sede:
        return Sede(**json.loads(raw))

    @staticmethod
    def _deserialize_entidad(raw: str) -> EntidadOrganizadora:
        return EntidadOrganizadora(**json.loads(raw))

    @staticmethod
    def _deserialize_disciplinas(raw: str) -> list[DisciplinaTorneo]:
        disciplinas_raw = json.loads(raw) if raw else []
        return [DisciplinaTorneo.from_dict(disciplina) for disciplina in disciplinas_raw]
