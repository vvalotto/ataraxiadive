"""Query y Handler para ObtenerProximasPerformances — US-1.3.1."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.estado_performance import EstadoPerformance


@dataclass
class ProximoAtletaDTO:
    """Read model de un atleta próximo a competir."""

    nombre_atleta: str
    ap_declarado: str
    unidad: str
    posicion: int


@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class ObtenerProximasPerformancesQuery:
    """Query para obtener los próximos atletas a competir."""

    competencia_id: UUID
    limit: int = 3


class ObtenerProximasPerformancesHandler:  # pylint: disable=too-few-public-methods
    """Proyecta el read model ProximosAtletas desde el Event Store.

    Retorna las performances en estado AnunciadaAP ordenadas por
    occurred_at del primer evento (proxy de orden de grilla en SP1).
    En SP2, el orden será por posicion_grilla de la grilla oficial.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerProximasPerformancesQuery) -> list[ProximoAtletaDTO]:
        """Ejecuta la query y retorna los próximos atletas."""
        prefix = f"performance-{query.competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        candidatos: list[tuple[str, Performance]] = []
        for stream in all_streams:
            performance = Performance.reconstitute(stream)
            if performance.estado == EstadoPerformance.AnunciadaAP:
                occurred_at = stream[0].get("occurred_at", "") if stream else ""
                candidatos.append((occurred_at, performance))

        candidatos.sort(key=lambda x: x[0])

        result = []
        for posicion, (_, performance) in enumerate(candidatos[: query.limit], start=1):
            ap = performance.ap
            participante_id = str(performance.participante_id)
            result.append(
                ProximoAtletaDTO(
                    nombre_atleta=f"Atleta-{participante_id[:8]}",
                    ap_declarado=str(ap.valor) if ap else "",
                    unidad=ap.unidad.value if ap else "",
                    posicion=posicion,
                )
            )
        return result
