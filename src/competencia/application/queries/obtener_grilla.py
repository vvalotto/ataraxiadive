"""Query y Handler para ObtenerGrilla — US-2.1.4."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


@dataclass
class EntradaGrillaDTO:
    """Read model de una entrada de la Grilla de Salida."""

    performance_id: str
    atleta_id: str
    nombre_atleta: str
    posicion: int
    andarivel: int
    ot_programado: str
    ap_declarado: str
    unidad: str
    estado: str


@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class ObtenerGrillaQuery:
    """Query para obtener la Grilla de Salida de una competencia."""

    competencia_id: UUID
    disciplina: Disciplina


class ObtenerGrillaHandler:
    """Proyecta el read model de la Grilla de Salida desde el Event Store.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerGrillaQuery) -> list[EntradaGrillaDTO]:
        """Ejecuta la query y retorna la grilla ordenada por posición."""
        stream_id = f"competencia-{query.competencia_id}"
        events = await self._event_store.load(stream_id)
        competencia = Competencia.reconstitute(
            competencia_id=query.competencia_id,
            disciplina=query.disciplina,
            events=events,
        )
        return [
            EntradaGrillaDTO(
                performance_id=str(e.performance_id),
                atleta_id=str(e.atleta_id),
                nombre_atleta=performance.nombre_atleta,
                posicion=e.posicion,
                andarivel=e.andarivel,
                ot_programado=e.ot_programado.isoformat(),
                ap_declarado=performance.ap_declarado,
                unidad=performance.unidad,
                estado=performance.estado,
            )
            for e in competencia.grilla
            for performance in [await self._load_performance(query.competencia_id, e.atleta_id, query.disciplina)]
        ]

    async def _load_performance(
        self,
        competencia_id: UUID,
        atleta_id: UUID,
        disciplina: Disciplina,
    ) -> "_PerformanceProjection":
        stream_id = f"performance-{competencia_id}-{atleta_id}-{disciplina.value}"
        events = await self._event_store.load(stream_id)
        if not events:
            return _PerformanceProjection(
                nombre_atleta=f"Atleta-{str(atleta_id)[:8]}",
                ap_declarado="",
                unidad="",
                estado="AnunciadaAP",
            )
        performance = Performance.reconstitute(events)
        ap = performance.ap
        return _PerformanceProjection(
            nombre_atleta=f"Atleta-{str(atleta_id)[:8]}",
            ap_declarado=str(ap.valor) if ap else "",
            unidad=ap.unidad.value if ap else "",
            estado=performance.estado.value if performance.estado else "",
        )


@dataclass(frozen=True)
class _PerformanceProjection:
    nombre_atleta: str
    ap_declarado: str
    unidad: str
    estado: str
