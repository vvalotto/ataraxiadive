"""Query y Handler para ObtenerAuditLog - US-4.6.1."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import UUID

from competencia.domain.ports.atleta_nombre_port import AtletaNombrePort
from competencia.domain.ports.event_store_port import EventStorePort


class PerformanceNoEncontrada(Exception):
    """Se lanza cuando no existe la performance consultada."""


@dataclass(frozen=True)
class AuditLogEventoDTO:
    """DTO de un evento individual del audit log."""

    sequence: int
    tipo: str
    timestamp: str
    datos: dict[str, Any]


@dataclass(frozen=True)
class AuditLogDTO:
    """DTO del audit log completo de una performance."""

    competencia_id: str
    atleta_id: str
    atleta_nombre: str
    disciplina: str
    eventos: list[AuditLogEventoDTO]


@dataclass(frozen=True)
class ObtenerAuditLogQuery:
    """Query para obtener el audit log de una performance puntual."""

    competencia_id: UUID
    atleta_id: UUID


class ObtenerAuditLogHandler:  # pylint: disable=too-few-public-methods
    """Recupera el audit log puntual de una performance desde el event store."""

    def __init__(
        self,
        event_store: EventStorePort,
        atleta_nombre_port: AtletaNombrePort,
    ) -> None:
        self._event_store = event_store
        self._atleta_nombre_port = atleta_nombre_port

    async def handle(self, query: ObtenerAuditLogQuery) -> AuditLogDTO:
        """Retorna el audit log completo de la performance consultada."""
        prefix = f"performance-{query.competencia_id}-{query.atleta_id}-"
        raw_events = await self._event_store.load_all_events_ordered(prefix)
        if not raw_events:
            raise PerformanceNoEncontrada(
                "No existe una performance para el atleta en la competencia indicada"
            )

        stream_id = raw_events[0]["stream_id"]
        eventos = [
            self._to_evento_dto(event) for event in raw_events if event["stream_id"] == stream_id
        ]
        atleta_nombre = await self._atleta_nombre_port.get_nombre(query.atleta_id)

        return AuditLogDTO(
            competencia_id=str(query.competencia_id),
            atleta_id=str(query.atleta_id),
            atleta_nombre=atleta_nombre,
            disciplina=self._extract_disciplina(stream_id, prefix),
            eventos=eventos,
        )

    @staticmethod
    def _to_evento_dto(event: dict[str, Any]) -> AuditLogEventoDTO:
        return AuditLogEventoDTO(
            sequence=event["sequence"],
            tipo=event["event_type"],
            timestamp=event["occurred_at"] or "",
            datos=event["payload"],
        )

    @staticmethod
    def _extract_disciplina(stream_id: str, prefix: str) -> str:
        if stream_id.startswith(prefix):
            return stream_id.removeprefix(prefix)
        return ""
