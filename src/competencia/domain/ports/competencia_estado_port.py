"""Puerto CompetenciaEstadoPort — consulta de estado del aggregate Competencia."""
from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from competencia.domain.value_objects.disciplina import Disciplina


class CompetenciaEstadoPort(ABC):
    """Puerto para consultar el estado del aggregate Competencia.

    En SP1 se implementa con un stub que retorna valores fijos.
    En SP2 la implementación real lee el stream del aggregate Competencia.

    Requerido por:
        RegistrarAPHandler: INV-P-03 (plazo) e INV-P-04 (grilla)
        LlamarAtletaHandler: INV-P-05 (en ejecución)
    """

    @abstractmethod
    async def is_plazo_vencido(
        self, competencia_id: UUID, disciplina: Disciplina
    ) -> bool:
        """Verifica si el plazo de registro de AP venció (INV-P-03).

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a verificar.

        Returns:
            True si PlazoAPVencido fue emitido para esta combinación.
        """

    @abstractmethod
    async def is_grilla_confirmada(
        self, competencia_id: UUID, disciplina: Disciplina
    ) -> bool:
        """Verifica si la grilla fue confirmada (INV-P-04).

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a verificar.

        Returns:
            True si GrillaConfirmada fue emitido para esta competencia.
        """

    @abstractmethod
    async def is_en_ejecucion(self, competencia_id: UUID) -> bool:
        """Verifica si la Competencia está en estado EnEjecucion (INV-P-05).

        Args:
            competencia_id: Identificador de la competencia.

        Returns:
            True si CompetenciaIniciada fue emitida y CompetenciaFinalizada no.
        """
