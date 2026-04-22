"""Command y Handler para finalizacion manual de competencia — US-5.2.2."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.application.commands._stream_ids import competencia_stream_id
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import CompetenciaNoFinalizable
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_estado_port import PerformancesEstadoPort
from competencia.domain.services.calculador_hash_competencia import CalculadorHashCompetencia
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia


@dataclass(frozen=True)
class FinalizarCompetenciaManualCommand:
    """Comando para cerrar explicitamente una competencia desde organizador."""

    competencia_id: UUID
    disciplina: Disciplina
    solicitado_por: str


class FinalizarCompetenciaManualHandler:
    """Handler de cierre manual de disciplina.

    Reutiliza el mismo aggregate y calculo de hash que P-08, pero agrega una
    precondicion operativa: solo una competencia en ejecucion y sin pendientes
    puede cerrarse manualmente.
    """

    def __init__(
        self,
        event_store: EventStorePort,
        performances_estado: PerformancesEstadoPort,
    ) -> None:
        self._event_store = event_store
        self._performances_estado = performances_estado

    async def handle(self, command: FinalizarCompetenciaManualCommand) -> None:
        """Ejecuta el cierre manual de competencia.

        Raises:
            CompetenciaNoFinalizable: si la competencia no esta en ejecucion o
                quedan performances pendientes.
        """
        stream_id = competencia_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)
        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )

        if competencia.estado == EstadoCompetencia.Finalizada:
            return

        if competencia.estado != EstadoCompetencia.EnEjecucion:
            raise CompetenciaNoFinalizable(
                f"Competencia {command.competencia_id}: se requiere estado EnEjecucion "
                f"para finalizar manualmente; estado actual '{competencia.estado}'"
            )

        estado = await self._performances_estado.get_estado(
            command.competencia_id,
            command.disciplina,
        )
        if not estado.todas_finalizadas:
            pendientes = estado.total - estado.ejecutadas - estado.dns_count
            raise CompetenciaNoFinalizable(
                f"Competencia {command.competencia_id}: INV-C-04 — "
                f"{pendientes} performance(s) aún pendientes"
            )

        performance_events = await self._event_store.load_all_events_ordered(
            f"performance-{command.competencia_id}-"
        )
        eventos_disciplina = [
            event
            for event in performance_events
            if event["stream_id"].endswith(f"-{command.disciplina.value}")
        ]
        hash_sha256 = CalculadorHashCompetencia.calcular(eventos_disciplina)

        competencia.finalizar(
            total_performances=estado.total,
            ejecutadas=estado.ejecutadas,
            dns_count=estado.dns_count,
            hash_sha256=hash_sha256,
            origen="manual",
            finalizada_por=command.solicitado_por,
        )

        for event in competencia.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )
