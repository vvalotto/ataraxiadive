"""Puerto ResultadosCompetenciaPort — ACL hacia BC Competencia."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from competencia.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class ResultadoFinal:
    """DTO con los datos de una performance al cierre de la disciplina.

    Producido por ResultadosCompetenciaAdapter a partir de los streams del
    BC Competencia. Es la única fuente de datos que ve BC Resultados.

    Attributes:
        atleta_id: Identificador del participante.
        rp: Marca efectiva registrada. None para DNS.
        unidad: Unidad de medida del RP. None para DNS.
        tarjeta: Tipo de tarjeta ("Blanca", "Amarilla", "Roja"). None para DNS.
        es_dns: True si el atleta no se presentó.
    """

    atleta_id: UUID
    rp: Decimal | None
    unidad: str | None
    tarjeta: str | None
    es_dns: bool


class ResultadosCompetenciaPort(ABC):
    """ACL: consulta los resultados finales de BC Competencia.

    La implementación concreta (ResultadosCompetenciaAdapter) lee los streams
    performance-{competencia_id}-* del Event Store de BC Competencia y extrae
    el estado final de cada Performance.

    Requerido por:
        CalcularRankingHandler: obtiene los datos para calcular el ranking.
    """

    @abstractmethod
    async def get_resultados_finales(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> list[ResultadoFinal]:
        """Retorna los resultados finales de todas las performances de la disciplina.

        Solo incluye performances en estado Ejecutada o DNS.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a consultar.

        Returns:
            Lista de ResultadoFinal para todas las performances finalizadas.
        """
