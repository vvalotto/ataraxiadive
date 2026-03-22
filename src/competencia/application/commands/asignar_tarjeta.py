"""Command y Handler para AsignarTarjeta — US-1.2.4."""
from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta


# ── Excepciones de aplicación ─────────────────────────────────────────────────


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class AsignarTarjetaCommand:
    """Comando para asignar la tarjeta al atleta tras registrar el resultado.

    Attributes:
        competencia_id: Competencia en la que se ejecutó la performance.
        participante_id: Participante al que se asigna la tarjeta.
        disciplina: Disciplina en la que compitió.
        tipo: Tipo de tarjeta — Blanca, Amarilla o Roja.
        asignada_por: Identificador del juez que asigna la tarjeta.
        motivo: Motivo obligatorio para Amarilla y Roja (INV-P-11). None para Blanca.
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    tipo: TipoTarjeta
    asignada_por: str
    motivo: str | None = field(default=None)


# ── Handler ───────────────────────────────────────────────────────────────────


class AsignarTarjetaHandler:
    """Handler del comando AsignarTarjeta.

    Carga la Performance desde el Event Store, ejecuta asignar_tarjeta()
    y persiste TarjetaAsignada. Es el paso final del ciclo de vida de la Performance.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: AsignarTarjetaCommand) -> None:
        """Ejecuta el comando AsignarTarjeta.

        Args:
            command: Datos de la tarjeta a asignar.

        Raises:
            PerformanceNoEncontrada: no existe Performance para este atleta.
            EstadoInvalidoParaAsignarTarjeta: Performance no está en ResultadoRegistrado (INV-P-07).
            MotivoObligatorio: tarjeta Amarilla o Roja sin motivo (INV-P-11).
        """
        stream_id = _build_stream_id(
            command.competencia_id, command.participante_id, command.disciplina
        )
        events = await self._event_store.load(stream_id)
        if not events:
            raise PerformanceNoEncontrada(
                f"No existe Performance para participante={command.participante_id} "
                f"disciplina={command.disciplina.value} "
                f"competencia={command.competencia_id}"
            )

        performance = Performance.reconstitute(events)

        # Ejecuta (lanza EstadoInvalidoParaAsignarTarjeta o MotivoObligatorio si aplica)
        performance.asignar_tarjeta(command.tipo, command.asignada_por, command.motivo)

        # Persistir eventos pendientes
        for event in performance.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(
    competencia_id: UUID, participante_id: UUID, disciplina: Disciplina
) -> str:
    """Construye el stream ID canónico para una Performance.

    Format: "performance-{competencia_id}-{participante_id}-{disciplina}"
    """
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"
