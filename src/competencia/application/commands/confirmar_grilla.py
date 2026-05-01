"""Command y Handler para ConfirmarGrilla — US-2.1.4."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.application.commands._stream_ids import competencia_stream_id


@dataclass(frozen=True)
class ConfirmarGrillaCommand:
    """Comando para confirmar la Grilla de Salida.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina de la competencia.
    """

    competencia_id: UUID
    disciplina: Disciplina


class ConfirmarGrillaHandler:
    """Handler del comando ConfirmarGrilla.

    Orquesta:
    1. Reconstitución del aggregate Competencia desde el Event Store.
    2. Ejecución del método de dominio confirmar_grilla().
    3. Persistencia del evento GrillaConfirmada.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: ConfirmarGrillaCommand) -> None:
        """Ejecuta el comando ConfirmarGrilla.

        Raises:
            GrillaNoGenerada: Si la grilla no fue generada aún.
            GrillaYaConfirmada: INV-C-02 — grilla ya confirmada.
        """
        stream_id = competencia_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)

        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )

        competencia.confirmar_grilla()

        for event in competencia.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )
