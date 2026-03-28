"""Command y Handler para IniciarCompetencia — US-2.1.4."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.application.commands._stream_ids import competencia_stream_id

@dataclass(frozen=True)
class IniciarCompetenciaCommand:
    """Comando para iniciar la Competencia.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina de la competencia.
        juez_id: Identificador del juez que inicia la competencia.
    """

    competencia_id: UUID
    disciplina: Disciplina
    juez_id: str


class IniciarCompetenciaHandler:
    """Handler del comando IniciarCompetencia.

    Orquesta:
    1. Reconstitución del aggregate Competencia desde el Event Store.
    2. Ejecución del método de dominio iniciar_competencia().
    3. Persistencia del evento CompetenciaIniciada.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: IniciarCompetenciaCommand) -> None:
        """Ejecuta el comando IniciarCompetencia.

        Raises:
            CompetenciaNoConfirmada: INV-C-03 — competencia no está en estado Confirmada.
        """
        stream_id = competencia_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)

        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )

        competencia.iniciar_competencia(command.juez_id)

        for event in competencia.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )
