"""Command y Handler para ConfigurarIntervaloOT — US-2.1.1."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ConfigurarIntervaloOTCommand:
    """Comando para configurar el intervalo entre OTs de una competencia.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina de la competencia.
        intervalo_minutos: Tiempo en minutos entre OTs. Debe ser > 0.
        configurado_por: Identificador del organizador o juez.
    """

    competencia_id: UUID
    disciplina: Disciplina
    intervalo_minutos: int
    configurado_por: str


# ── Handler ───────────────────────────────────────────────────────────────────


class ConfigurarIntervaloOTHandler:
    """Handler del comando ConfigurarIntervaloOT.

    Carga el aggregate Competencia desde el Event Store (o crea uno nuevo
    si no existe), ejecuta el método de dominio y persiste el evento
    IntervaloOTConfigurado.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: ConfigurarIntervaloOTCommand) -> None:
        """Ejecuta el comando ConfigurarIntervaloOT.

        Args:
            command: Datos del intervalo a configurar.

        Raises:
            IntervaloInvalido: Si intervalo_minutos <= 0.
            GrillaYaConfirmada: Si la grilla ya fue confirmada.
        """
        stream_id = _build_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)

        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )

        competencia.configurar_intervalo_ot(
            intervalo_minutos=command.intervalo_minutos,
            configurado_por=command.configurado_por,
        )

        for event in competencia.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID) -> str:
    """Construye el stream ID canónico para una Competencia.

    Format: "competencia-{competencia_id}"
    """
    return f"competencia-{competencia_id}"
