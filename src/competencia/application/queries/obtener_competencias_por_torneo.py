"""Query y Handler para ObtenerCompetenciasPorTorneo — US-3.3.1."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.ports.competencias_por_torneo_port import CompetenciasPorTorneoPort


@dataclass
class CompetenciaSummaryDTO:
    """Resumen de una competencia asociada a un torneo."""

    competencia_id: UUID
    disciplina: str
    torneo_id: UUID


@dataclass(frozen=True)
class ObtenerCompetenciasPorTorneoQuery:
    """Query para listar competencias de un torneo."""

    torneo_id: UUID


class ObtenerCompetenciasPorTorneoHandler:
    """Consulta la proyeccion materializada y retorna las competencias de un torneo."""

    def __init__(self, proyeccion: CompetenciasPorTorneoPort) -> None:
        self._proyeccion = proyeccion

    async def handle(self, query: ObtenerCompetenciasPorTorneoQuery) -> list[CompetenciaSummaryDTO]:
        """Retorna la lista de competencias pertenecientes al torneo."""
        records = await self._proyeccion.listar_por_torneo(query.torneo_id)
        return [
            CompetenciaSummaryDTO(
                competencia_id=record.competencia_id,
                disciplina=record.disciplina,
                torneo_id=record.torneo_id,
            )
            for record in records
        ]
