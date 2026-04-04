"""Query y Handler para ObtenerEstadoCompetencia — US-2.1.4."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


@dataclass
class EstadoCompetenciaDTO:
    """Read model del estado actual de una Competencia."""

    estado: str
    intervalo_minutos: int | None
    grilla_confirmada: bool
    torneo_id: UUID | None = None


@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class ObtenerEstadoCompetenciaQuery:
    """Query para obtener el estado actual de una competencia."""

    competencia_id: UUID
    disciplina: Disciplina


class ObtenerEstadoCompetenciaHandler:
    """Proyecta el read model de estado desde el Event Store.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerEstadoCompetenciaQuery) -> EstadoCompetenciaDTO:
        """Ejecuta la query y retorna el estado actual de la competencia."""
        stream_id = f"competencia-{query.competencia_id}"
        events = await self._event_store.load(stream_id)
        competencia = Competencia.reconstitute(
            competencia_id=query.competencia_id,
            disciplina=query.disciplina,
            events=events,
        )
        return EstadoCompetenciaDTO(
            estado=competencia.estado.value,
            intervalo_minutos=(
                competencia.intervalo.minutos if competencia.intervalo is not None else None
            ),
            grilla_confirmada=competencia.grilla_confirmada,
            torneo_id=competencia.torneo_id,
        )
