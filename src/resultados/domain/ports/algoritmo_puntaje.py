"""Puerto AlgoritmoPuntaje — contrato para calcular puntos por disciplina."""

from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal
from uuid import UUID

from shared.domain.value_objects.disciplina import Disciplina

from resultados.domain.ports.resultados_competencia_port import ResultadoFinal


class AlgoritmoPuntaje(ABC):
    """Contrato para calcular el puntaje de cada atleta en una disciplina.

    Invariantes:
        - El dict retornado tiene exactamente un entry por atleta del input.
        - Los valores están en [0.00, 100.00] con precisión de 2 decimales.
        - Atletas con tarjeta roja o DNS siempre reciben 0.00.
    """

    @abstractmethod
    def calcular(
        self,
        resultados: list[ResultadoFinal],
        disciplina: Disciplina,
    ) -> dict[UUID, Decimal]:
        """Calcula el puntaje de cada atleta en la disciplina.

        Args:
            resultados: Resultados finales de todos los atletas de la disciplina.
            disciplina: Disciplina para determinar si es tiempo o distancia.

        Returns:
            Mapa atleta_id → puntos (Decimal con 2 decimales, en [0, 100]).
            Retorna dict vacío si resultados está vacío.
        """
