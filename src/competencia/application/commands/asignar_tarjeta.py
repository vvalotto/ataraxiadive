"""Command y Handler para AsignarTarjeta — US-1.2.4 / US-1.4.1 / US-2.4.1."""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal
from uuid import UUID

from typing import Awaitable, Callable

from competencia.application._p08_finalizacion import trigger_finalizacion_si_corresponde
from competencia.application.commands._handler_utils import (
    build_performance_stream_id,
    cargar_o_fallar,
    persistir_eventos_pendientes,
    reconstruir_performance,
)
from competencia.domain.exceptions import DisciplinaNoAdmitePenalizaciones
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_estado_port import PerformancesEstadoPort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta

# ── Excepciones de aplicación ─────────────────────────────────────────────────


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


_DISCIPLINAS_DINAMICAS_CON_PENALIZACION = {
    Disciplina.DNF,
    Disciplina.DYN,
    Disciplina.DBF,
}


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
    penalizaciones: tuple[PenalizacionTecnica, ...] = field(default_factory=tuple)


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
        on_finalizada: Callable[[UUID, Disciplina, UUID | None], Awaitable[None]] | None = None,
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
        stream_id = build_performance_stream_id(
            command.competencia_id, command.participante_id, command.disciplina
        )
        events = await cargar_o_fallar(
            event_store=self._event_store,
            stream_id=stream_id,
            exception_factory=lambda: PerformanceNoEncontrada(
                f"No existe Performance para participante={command.participante_id} "
                f"disciplina={command.disciplina.value} "
                f"competencia={command.competencia_id}"
            ),
        )
        performance = reconstruir_performance(events)

        self._validar_penalizaciones(command)

        performance.asignar_tarjeta(
            command.tipo,
            command.asignada_por,
            command.motivo_dq,
            command.motivo_texto,
            command.distancia_blackout,
            command.penalizaciones,
        )
        await persistir_eventos_pendientes(
            event_store=self._event_store,
            stream_id=stream_id,
            aggregate=performance,
        )

        if self._performances_estado is not None:
            await trigger_finalizacion_si_corresponde(
                self._event_store,
                self._performances_estado,
                command.competencia_id,
                command.disciplina,
                on_finalizada=self._on_finalizada,
            )

    @staticmethod
    def _validar_penalizaciones(command: AsignarTarjetaCommand) -> None:
        if (
            command.tipo == TipoTarjeta.BlancaConPenalizaciones
            and command.disciplina not in _DISCIPLINAS_DINAMICAS_CON_PENALIZACION
        ):
            raise DisciplinaNoAdmitePenalizaciones(
                f"La disciplina {command.disciplina.value} no admite BlancaConPenalizaciones"
            )
