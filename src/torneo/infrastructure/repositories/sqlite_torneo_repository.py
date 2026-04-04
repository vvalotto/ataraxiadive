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
                (
                    str(torneo.torneo_id),
                    torneo.nombre,
                    torneo.descripcion,
                    torneo.fecha_inicio.isoformat(),
                    torneo.fecha_fin.isoformat(),
                    json.dumps(
                        {
                            "nombre": torneo.sede.nombre,
                            "ciudad": torneo.sede.ciudad,
                            "pais": torneo.sede.pais,
                        }
                    ),
                    json.dumps(
                        {
                            "nombre": torneo.entidad_organizadora.nombre,
                            "tipo": torneo.entidad_organizadora.tipo,
                        }
                    ),
                    torneo.estado.value,
                    json.dumps([dt.to_dict() for dt in torneo.disciplinas_torneo]),
                ),
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
        sede_data = json.loads(row["sede"])
        entidad_data = json.loads(row["entidad"])
        disciplinas_raw = json.loads(row["disciplinas_torneo"]) if row["disciplinas_torneo"] else []
        return Torneo(
            torneo_id=UUID(row["torneo_id"]),
            nombre=row["nombre"],
            descripcion=row["descripcion"],
            fecha_inicio=date.fromisoformat(row["fecha_inicio"]),
            fecha_fin=date.fromisoformat(row["fecha_fin"]),
            sede=Sede(**sede_data),
            entidad_organizadora=EntidadOrganizadora(**entidad_data),
            estado=EstadoTorneo(row["estado"]),
            disciplinas_torneo=[DisciplinaTorneo.from_dict(d) for d in disciplinas_raw],
        )
