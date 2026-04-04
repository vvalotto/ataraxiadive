"""Command y Handler para AjustarGrilla — US-2.1.3."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina

# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AjustarGrillaCommand:
    """Comando para aplicar ajustes manuales sobre la Grilla de Salida.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina de la competencia.
        cambios: Lista de cambios a aplicar sobre entradas de la grilla.
    """

    competencia_id: UUID
    disciplina: Disciplina
    cambios: list[CambioGrilla]


# ── Handler ───────────────────────────────────────────────────────────────────


class AjustarGrillaHandler:
    """Handler del comando AjustarGrilla.

    Orquesta:
    1. Reconstitución del aggregate Competencia desde el Event Store.
    2. Ejecución del método de dominio ajustar_grilla().
    3. Persistencia del evento GrillaDeSalidaAjustada.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: AjustarGrillaCommand) -> None:
        """Ejecuta el comando AjustarGrilla.

        Args:
            command: Datos para ajustar la grilla.

        Raises:
            GrillaNoGenerada: Si la grilla no fue generada aún.
            GrillaYaConfirmada: INV-C-02 — grilla confirmada, ajuste no permitido.
            PerformanceNoEncontrada: Si algún performance_id no existe en la grilla.
        """
        stream_id = _build_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)

        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )

        competencia.ajustar_grilla(command.cambios)

        for event in competencia.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID) -> str:
    """Construye el stream ID canónico para una Competencia."""
    return f"competencia-{competencia_id}"
