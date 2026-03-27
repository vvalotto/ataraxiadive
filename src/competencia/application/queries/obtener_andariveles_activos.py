"""Query y Handler para ObtenerAndarivelesActivos — US-2.3.1."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.ports.andariveles_activos_port import (
    AndarivelesActivosData,
    AndarivelesActivosPort,
)
from competencia.domain.value_objects.disciplina import Disciplina


# ── Query ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ObtenerAndarivelesActivosQuery:
    """Consulta para obtener el estado de los andariveles de una competencia.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina en ejecución.
        andariveles: Número total de andariveles configurados en la grilla.
    """

    competencia_id: UUID
    disciplina: Disciplina
    andariveles: int


# ── Handler ───────────────────────────────────────────────────────────────────


class ObtenerAndarivelesActivosHandler:
    """Handler para ObtenerAndarivelesActivosQuery.

    Retorna el estado de cada andarivel (ocupado/libre) en el instante actual.

    Args:
        andariveles_activos: Puerto que proyecta el estado de los andariveles.
    """

    def __init__(self, andariveles_activos: AndarivelesActivosPort) -> None:
        self._andariveles_activos = andariveles_activos

    async def handle(
        self, query: ObtenerAndarivelesActivosQuery
    ) -> list[AndarivelesActivosData]:
        """Ejecuta la consulta de andariveles activos.

        Args:
            query: Datos de la consulta.

        Returns:
            Lista de AndarivelesActivosData con un elemento por andarivel (1..N).
        """
        return await self._andariveles_activos.get_andariveles_activos(
            competencia_id=query.competencia_id,
            disciplina=query.disciplina,
            andariveles=query.andariveles,
        )
