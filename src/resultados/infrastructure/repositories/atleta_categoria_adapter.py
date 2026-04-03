"""ACL a BC Registro para obtener categoria de atletas."""

from __future__ import annotations

import os
from uuid import UUID

import aiosqlite

from registro.domain.value_objects.categoria import Categoria
from resultados.domain.ports.resultados_competencia_port import AtletaCategoriaPort


class AtletaCategoriaAdapter(AtletaCategoriaPort):
    """Consulta SQLite de Registro para resolver categoria por atleta_id."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def get_categoria(self, atleta_id: UUID) -> Categoria:
        async with aiosqlite.connect(self._db_path) as conn:
            async with conn.execute(
                "SELECT categoria FROM atletas WHERE atleta_id = ?",
                (str(atleta_id),),
            ) as cursor:
                row = await cursor.fetchone()
        if row is None:
            raise ValueError(f"Atleta {atleta_id} no encontrado en Registro")
        return Categoria(row[0])
