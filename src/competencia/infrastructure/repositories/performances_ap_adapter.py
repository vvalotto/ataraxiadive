"""Adaptador PerformancesAPAdapter — implementación de PerformancesAPPort sobre Event Store."""
from __future__ import annotations

from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_ap_port import (
    PerformancesAPData,
    PerformancesAPPort,
)
from competencia.domain.value_objects.estado_performance import EstadoPerformance


class PerformancesAPAdapter(PerformancesAPPort):
    """Implementación de PerformancesAPPort que lee del Event Store.

    Carga todos los streams `performance-{competencia_id}-*`, reconstruye
    cada Performance y retorna las que están en estado AnunciadaAP.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def get_performances_con_ap(
        self, competencia_id: UUID
    ) -> list[PerformancesAPData]:
        """Retorna las performances en estado AnunciadaAP para la competencia.

        Args:
            competencia_id: Identificador de la competencia.

        Returns:
            Lista de PerformancesAPData ordenada por registro de inserción
            (orden natural del Event Store).
        """
        prefix = f"performance-{competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        result: list[PerformancesAPData] = []
        for stream_events in all_streams:
            if not stream_events:
                continue

            performance = Performance.reconstitute(stream_events)
            if performance.estado != EstadoPerformance.AnunciadaAP:
                continue
            if performance.ap is None:
                continue

            result.append(
                PerformancesAPData(
                    performance_id=performance.performance_id,
                    atleta_id=performance.participante_id,
                    valor_ap=performance.ap.valor,
                    unidad=performance.ap.unidad,
                )
            )

        return result
