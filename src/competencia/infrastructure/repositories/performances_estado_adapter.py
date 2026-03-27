"""Adaptador PerformancesEstadoAdapter — implementación de PerformancesEstadoPort."""
from __future__ import annotations

from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_estado_port import (
    PerformancesEstadoData,
    PerformancesEstadoPort,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance


class PerformancesEstadoAdapter(PerformancesEstadoPort):
    """Implementación de PerformancesEstadoPort que proyecta el estado desde el Event Store.

    Carga todos los streams `performance-{competencia_id}-*`, reconstituye cada
    Performance, filtra por disciplina y computa el snapshot de estado.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

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
        prefix = f"performance-{competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        total = 0
        ejecutadas = 0
        dns_count = 0

        for stream_events in all_streams:
            if not stream_events:
                continue

            performance = Performance.reconstitute(stream_events)
            if performance.disciplina != disciplina:
                continue

            total += 1
            if performance.estado == EstadoPerformance.Ejecutada:
                ejecutadas += 1
            elif performance.estado == EstadoPerformance.DNS:
                dns_count += 1

        return PerformancesEstadoData(
            total=total,
            ejecutadas=ejecutadas,
            dns_count=dns_count,
        )
