"""Puerto PerformancesEstadoPort — consulta el estado agregado de performances."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from uuid import UUID

from competencia.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class PerformancesEstadoData:
    """Snapshot del estado agregado de performances para una competencia y disciplina.

    Attributes:
        total: Total de performances registradas en la disciplina.
        ejecutadas: Cantidad en estado Ejecutada (tarjeta asignada).
        dns_count: Cantidad en estado DNS.
    """

    total: int
    ejecutadas: int
    dns_count: int

    @property
    def todas_finalizadas(self) -> bool:
        """True si todas las performances están en estado Ejecutada o DNS."""
        return self.total > 0 and (self.ejecutadas + self.dns_count) == self.total


class PerformancesEstadoPort(ABC):
    """Puerto para consultar el estado agregado de performances de una disciplina.

    La implementación concreta lee los streams performance-{competencia_id}-*
    del Event Store, reconstituye cada Performance y computa las métricas.

    Requerido por:
        AsignarTarjetaHandler: verificación P-08 post-TarjetaAsignada.
        RegistrarDNSHandler: verificación P-08 post-DNSRegistrado.
    """

    @abstractmethod
    async def get_estado(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> PerformancesEstadoData:
        """Retorna el snapshot del estado de performances para la disciplina.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a consultar.

        Returns:
            PerformancesEstadoData con total, ejecutadas y dns_count.
        """
