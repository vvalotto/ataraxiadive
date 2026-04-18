"""Adaptador AtletaNombreAdapter — implementación del puerto usando el BC Registro."""

from __future__ import annotations

import os
from uuid import UUID

import aiosqlite

from competencia.domain.ports.atleta_nombre_port import AtletaNombrePort


class AtletaNombreAdapter(AtletaNombrePort):
    """Resuelve el nombre completo de un atleta consultando registro.db directamente.

    Args:
        db_path: Ruta al archivo SQLite del BC Registro.
                 Si no se provee, usa la variable de entorno REGISTRO_DB_PATH.
    """

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path: str = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def get_nombre(self, atleta_id: UUID) -> str:
        async with aiosqlite.connect(self._db_path) as conn:
            async with conn.execute(
                "SELECT nombre, apellido FROM atletas WHERE atleta_id = ?",
                (str(atleta_id),),
            ) as cursor:
                row = await cursor.fetchone()
        if row:
            return f"{row[0]} {row[1]}"
        return f"Atleta-{str(atleta_id)[:8]}"
