"""ACL a BC Registro para obtener datos exportables de un atleta."""

from __future__ import annotations

import os
from dataclasses import dataclass
from uuid import UUID

import aiosqlite

from registro.domain.value_objects.categoria import Categoria


@dataclass(frozen=True)
class AtletaInfo:
    """Datos exportables del atleta resueltos desde Registro."""

    atleta_id: UUID
    nombre_completo: str
    categoria: Categoria
    club: str


class AtletaInfoAdapter:
    """Consulta SQLite de Registro para nombre, categoria y club."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("REGISTRO_DB_PATH", "data/registro.db")

    async def get_atleta_info(self, atleta_id: UUID) -> AtletaInfo:
        async with aiosqlite.connect(self._db_path) as conn:
            async with conn.execute(
                """
                SELECT nombre, apellido, categoria, club
                FROM atletas
                WHERE atleta_id = ?
                """,
                (str(atleta_id),),
            ) as cursor:
                row = await cursor.fetchone()

        if row is None:
            raise ValueError(f"Atleta {atleta_id} no encontrado en Registro")

        nombre = f"{row[0]} {row[1]}".strip()
        return AtletaInfo(
            atleta_id=atleta_id,
            nombre_completo=nombre,
            categoria=Categoria(row[2]),
            club=row[3],
        )
