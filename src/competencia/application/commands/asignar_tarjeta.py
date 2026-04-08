"""Command y Handler para AsignarTarjeta — US-1.2.4 / US-1.4.1 / US-2.4.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from typing import Awaitable, Callable

from competencia.application._p08_finalizacion import trigger_finalizacion_si_corresponde
from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_estado_port import PerformancesEstadoPort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.motivo_dq import MotivoDQ
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
        motivo_dq: Motivo reglamentario para tarjeta roja.
        motivo_texto: Motivo libre para tarjeta amarilla.
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    tipo: TipoTarjeta
    asignada_por: str
    motivo_dq: MotivoDQ | None = field(default=None)
    motivo_texto: str | None = field(default=None)
    distancia_blackout: Decimal | None = field(default=None)


# ── Handler ───────────────────────────────────────────────────────────────────


class AsignarTarjetaHandler:
    """Handler del comando AsignarTarjeta.

    Carga la Performance desde el Event Store, ejecuta asignar_tarjeta()
    y persiste TarjetaAsignada. Tras persistir, verifica P-08: si todas las
    performances finalizaron, emite CompetenciaFinalizada automáticamente.

    Args:
        event_store: Puerto de persistencia de eventos.
        performances_estado: Puerto para verificar P-08. None = sin verificación.
    """

    def __init__(
        self,
        event_store: EventStorePort,
        performances_estado: PerformancesEstadoPort | None = None,
        on_finalizada: Callable[..., Awaitable[None]] | None = None,
    ) -> None:
        self._event_store = event_store
        self._performances_estado = performances_estado
        self._on_finalizada = on_finalizada

    async def handle(self, command: AsignarTarjetaCommand) -> None:
        """Ejecuta el comando AsignarTarjeta.

        Args:
            command: Datos de la tarjeta a asignar.

        Raises:
            PerformanceNoEncontrada: no existe Performance para este atleta.
            EstadoInvalidoParaAsignarTarjeta: Performance no está en ResultadoRegistrado (INV-P-07).
            MotivoObligatorio: tarjeta Amarilla sin motivo libre.
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
        performance.asignar_tarjeta(
            command.tipo,
            command.asignada_por,
            command.motivo_dq,
            command.motivo_texto,
            command.distancia_blackout,
        )

        # Persistir eventos pendientes
        for event in performance.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )

        # Política P-08: verificar si la competencia puede finalizar
        if self._performances_estado is not None:
            await trigger_finalizacion_si_corresponde(
                self._event_store,
                self._performances_estado,
                command.competencia_id,
                command.disciplina,
                on_finalizada=self._on_finalizada,
            )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID, participante_id: UUID, disciplina: Disciplina) -> str:
    """Construye el stream ID canónico para una Performance."""
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"
