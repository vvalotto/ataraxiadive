"""Command y Handler para asignar juez a una performance de la grilla."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.application.commands._stream_ids import competencia_stream_id
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class AsignarJuezPerformanceCommand:
    competencia_id: UUID
    disciplina: Disciplina
    performance_id: UUID
    juez_id: str


class AsignarJuezPerformanceHandler:
    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: AsignarJuezPerformanceCommand) -> None:
        stream_id = competencia_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)

        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )
        competencia.asignar_juez_performance(command.performance_id, command.juez_id)

        for event in competencia.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )
