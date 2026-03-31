from __future__ import annotations

import os
from datetime import date
from uuid import UUID

import aiosqlite

from registro.domain.exceptions import TorneoNoDisponible
from registro.domain.ports.torneo_consulta_port import TorneoConsultaPort
from shared.domain.value_objects.disciplina import Disciplina

_ESTADO_INSCRIPCION_ABIERTA = "INSCRIPCION_ABIERTA"


class SQLiteTorneoConsulta(TorneoConsultaPort):
    """ACL read-only: lee torneo.db del BC Torneo sin imports cross-BC en domain."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("TORNEO_DB_PATH", "data/torneo.db")

    async def esta_abierto_para_inscripcion(self, torneo_id: UUID) -> bool:
        async with aiosqlite.connect(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT estado FROM torneos WHERE torneo_id = ?", (str(torneo_id),)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    return False
                return row["estado"] == _ESTADO_INSCRIPCION_ABIERTA

    async def obtener_fecha_inicio(self, torneo_id: UUID) -> date:
        async with aiosqlite.connect(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT fecha_inicio FROM torneos WHERE torneo_id = ?", (str(torneo_id),)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise TorneoNoDisponible(f"Torneo {torneo_id} no encontrado")
                return date.fromisoformat(row["fecha_inicio"])

    async def obtener_disciplinas(self, torneo_id: UUID) -> frozenset[Disciplina]:
        # TODO US-3.4.1: Torneo aún no tiene campo disciplinas — se agrega en INC-3.4.
        # Hasta entonces retornamos todas las disciplinas disponibles (sin restricción).
        async with aiosqlite.connect(self._db_path) as conn:
            conn.row_factory = aiosqlite.Row
            async with conn.execute(
                "SELECT torneo_id FROM torneos WHERE torneo_id = ?", (str(torneo_id),)
            ) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise TorneoNoDisponible(f"Torneo {torneo_id} no encontrado")
        return frozenset(Disciplina)
