"""Query y Handler para ObtenerProximasPerformances — US-1.3.1 / US-2.2.2."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
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
    disciplina: Disciplina
    limit: int = field(default=3)


class ObtenerProximasPerformancesHandler:  # pylint: disable=too-few-public-methods
    """Proyecta el read model ProximosAtletas desde el Event Store.

    Retorna las performances en estado AnunciadaAP ordenadas por
    posicion_grilla de la grilla oficial (SP2). La posición se obtiene
    del aggregate Competencia, única fuente de verdad del orden de grilla.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerProximasPerformancesQuery) -> list[ProximoAtletaDTO]:
        """Ejecuta la query y retorna los próximos atletas ordenados por posicion_grilla."""
        grilla_map = await self._build_grilla_map(query.competencia_id, query.disciplina)

        prefix = f"performance-{query.competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        candidatos: list[tuple[int, Performance]] = []
        for stream in all_streams:
            performance = Performance.reconstitute(stream)
            if performance.estado == EstadoPerformance.AnunciadaAP:
                posicion = grilla_map.get(performance.performance_id, 999999)
                candidatos.append((posicion, performance))

        candidatos.sort(key=lambda x: x[0])

        result = []
        for posicion_grilla, performance in candidatos[: query.limit]:
            ap = performance.ap
            participante_id = str(performance.participante_id)
            result.append(
                ProximoAtletaDTO(
                    nombre_atleta=f"Atleta-{participante_id[:8]}",
                    ap_declarado=str(ap.valor) if ap else "",
                    unidad=ap.unidad.value if ap else "",
                    posicion=posicion_grilla,
                )
            )
        return result

    async def _build_grilla_map(
        self, competencia_id: UUID, disciplina: Disciplina
    ) -> dict[UUID, int]:
        """Construye un mapa {performance_id: posicion} desde la grilla de la Competencia."""
        stream_id = f"competencia-{competencia_id}"
        events = await self._event_store.load(stream_id)
        if not events:
            return {}
        competencia = Competencia.reconstitute(
            competencia_id=competencia_id,
            disciplina=disciplina,
            events=events,
        )
        return {entrada.performance_id: entrada.posicion for entrada in competencia.grilla}
