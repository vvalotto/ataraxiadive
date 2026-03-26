"""Query y Handler para ObtenerGrilla — US-2.1.4."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


@dataclass
class EntradaGrillaDTO:
    """Read model de una entrada de la Grilla de Salida."""

    performance_id: str
    atleta_id: str
    posicion: int
    andarivel: int
    ot_programado: str


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
                posicion=e.posicion,
                andarivel=e.andarivel,
                ot_programado=e.ot_programado.isoformat(),
            )
            for e in competencia.grilla
        ]
