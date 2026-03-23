"""Query y Handler para ObtenerEventos — US-1.4.2."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from competencia.domain.ports.event_store_port import EventStorePort


@dataclass(frozen=True)
class EventoDTO:
    """DTO que representa un evento del Event Store aplanado para el audit log."""

    sequence: int
    event_type: str
    performance_id: str
    occurred_at: str
    data: dict[str, Any]


@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class ObtenerEventosQuery:
    """Query para obtener todos los eventos de una competencia en orden de inserción."""

    competencia_id: UUID


class ObtenerEventosHandler:  # pylint: disable=too-few-public-methods
    """Proyecta la traza completa del Event Store para una competencia.

    Retorna todos los eventos de todos los streams de la competencia en el
    orden real de inserción (por id autoincrement), exponiendo el Event Store
    como audit log de solo lectura.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerEventosQuery) -> list[EventoDTO]:
        """Ejecuta la query y retorna la lista de EventoDTO en orden de secuencia."""
        prefix = f"performance-{query.competencia_id}-"
        raw_events = await self._event_store.load_all_events_ordered(prefix)
        return [self._to_dto(event, prefix) for event in raw_events]

    @staticmethod
    def _to_dto(event: dict[str, Any], prefix: str) -> EventoDTO:
        stream_id: str = event["stream_id"]
        # stream_id tiene forma "performance-{competencia_id}-{performance_id}"
        # Se stripea el prefijo para obtener solo el performance_id
        performance_id = stream_id.removeprefix(prefix) if stream_id.startswith(prefix) else stream_id
        return EventoDTO(
            sequence=event["sequence"],
            event_type=event["event_type"],
            performance_id=performance_id,
            occurred_at=event["occurred_at"] or "",
            data=event["payload"],
        )
