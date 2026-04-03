"""Puerto de lectura/escritura para la proyeccion competencias por torneo."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CompetenciaPorTorneoRecord:
    """Registro interno de la proyeccion materializada por torneo."""

    competencia_id: UUID
    disciplina: str
    torneo_id: UUID


class CompetenciasPorTorneoPort(ABC):
    """Puerto para persistir y consultar la proyeccion competencias por torneo."""

    @abstractmethod
    async def guardar(
        self,
        competencia_id: UUID,
        disciplina: str,
        torneo_id: UUID,
    ) -> None:
        """Persiste o actualiza una entrada de la proyeccion."""

    @abstractmethod
    async def listar_por_torneo(self, torneo_id: UUID) -> list[CompetenciaPorTorneoRecord]:
        """Retorna los registros materializados para el torneo indicado."""
