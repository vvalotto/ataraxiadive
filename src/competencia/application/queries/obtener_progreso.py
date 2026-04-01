"""Query y Handler para ObtenerProgreso — US-1.3.1."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.estado_performance import EstadoPerformance


@dataclass
class ProgresoCompetenciaDTO:
    """Read model del progreso de ejecución de una competencia."""

    total: int
    ejecutadas: int
    dns_count: int
    completadas: int


@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class ObtenerProgresoQuery:
    """Query para obtener el progreso de una competencia."""

    competencia_id: UUID


class ObtenerProgresoHandler:
    """Proyecta el read model ProgresoCompetencia desde el Event Store.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerProgresoQuery) -> ProgresoCompetenciaDTO:
        """Ejecuta la query y retorna el progreso de la competencia."""
        prefix = f"performance-{query.competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        total = len(all_streams)
        ejecutadas = 0
        dns_count = 0

        for stream in all_streams:
            performance = Performance.reconstitute(stream)
            if performance.estado == EstadoPerformance.Ejecutada:
                ejecutadas += 1
            elif performance.estado == EstadoPerformance.DNS:
                dns_count += 1

        return ProgresoCompetenciaDTO(
            total=total,
            ejecutadas=ejecutadas,
            dns_count=dns_count,
            completadas=ejecutadas + dns_count,
        )
