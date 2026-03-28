"""Puerto PerformancesAPPort — consulta de performances con AP registrado."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from competencia.domain.value_objects.unidad_medida import UnidadMedida


@dataclass(frozen=True)
class PerformancesAPData:
    """DTO con los datos de una Performance que tiene AP registrado.

    Attributes:
        performance_id: Identificador de la Performance.
        atleta_id: Identificador del atleta (participante_id).
        valor_ap: Marca declarada.
        unidad: Unidad de medida del AP (Metros | Segundos).
    """

    performance_id: UUID
    atleta_id: UUID
    valor_ap: Decimal
    unidad: UnidadMedida


class PerformancesAPPort(ABC):
    """Puerto para obtener las performances con AP registrado de una competencia.

    La implementación concreta (PerformancesAPAdapter) lee los streams
    performance-{competencia_id}-* del Event Store y reconstruye el estado
    de cada Performance para identificar las que están en estado AnunciadaAP.

    Requerido por:
        GenerarGrillaHandler: necesita los APs para ordenar y calcular OTs.
    """

    @abstractmethod
    async def get_performances_con_ap(
        self, competencia_id: UUID
    ) -> list[PerformancesAPData]:
        """Retorna todas las performances en estado AnunciadaAP para la competencia.

        Solo se incluyen performances que tienen un APRegistrado y no han
        avanzado a estados posteriores (Llamada, DNS, etc.).

        Args:
            competencia_id: Identificador de la competencia.

        Returns:
            Lista de PerformancesAPData — puede estar vacía si ningún atleta
            registró AP.
        """
