"""Command y Handler para resolver una performance que quedó en revisión."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Awaitable, Callable
from uuid import UUID

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


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


_DISCIPLINAS_DINAMICAS_CON_PENALIZACION = {
    Disciplina.DNF,
    Disciplina.DYN,
    Disciplina.DBF,
}


@dataclass(frozen=True)
class ResolverRevisionCommand:
    """Comando para cerrar la revisión de una performance."""

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    tipo: TipoTarjeta
    resuelta_por: str
    motivo_dq: MotivoDQ | None = field(default=None)
    penalizaciones: tuple[PenalizacionTecnica, ...] = field(default_factory=tuple)


class ResolverRevisionHandler:
    """Handler del comando ResolverRevision."""

    def __init__(
        self,
        event_store: EventStorePort,
        performances_estado: PerformancesEstadoPort | None = None,
        on_finalizada: Callable[..., Awaitable[None]] | None = None,
    ) -> None:
        self._event_store = event_store
        self._performances_estado = performances_estado
        self._on_finalizada = on_finalizada

    async def handle(self, command: ResolverRevisionCommand) -> None:
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

        performance.resolver_revision(
            command.tipo,
            command.resuelta_por,
            command.motivo_dq,
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
    def _validar_penalizaciones(command: ResolverRevisionCommand) -> None:
        if (
            command.tipo == TipoTarjeta.BlancaConPenalizaciones
            and command.disciplina not in _DISCIPLINAS_DINAMICAS_CON_PENALIZACION
        ):
            raise DisciplinaNoAdmitePenalizaciones(
                f"La disciplina {command.disciplina.value} no admite BlancaConPenalizaciones"
            )
