"""Command y Handler para GenerarGrilla — US-2.1.2."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from competencia.application.commands._handler_utils import (
    build_competencia_stream_id,
    build_performance_stream_id,
    persistir_eventos_pendientes,
    reconstruir_competencia,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.disciplina_descriptor_port import DisciplinaDescriptorPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_ap_port import PerformancesAPPort
from competencia.domain.value_objects.disciplina import Disciplina

# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class GenerarGrillaCommand:
    """Comando para generar (o regenerar) la Grilla de Salida.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina de la competencia.
        ot_inicio: Timestamp de inicio usado para calcular los OTs.
        andariveles: Número de andariveles disponibles (default 1).
    """

    competencia_id: UUID
    disciplina: Disciplina
    ot_inicio: datetime
    andariveles: int = 1


# ── Handler ───────────────────────────────────────────────────────────────────


class GenerarGrillaHandler:
    """Handler del comando GenerarGrilla.

    Orquesta:
    1. Reconstitución del aggregate Competencia desde el Event Store.
    2. Consulta de performances con AP registrado via PerformancesAPPort.
    3. Ejecución del método de dominio generar_grilla().
    4. Persistencia del evento GrillaDeSalidaGenerada.

    Args:
        event_store: Puerto de persistencia de eventos.
        performances_ap: Puerto para consultar performances con AP.
        disciplina_descriptor: Puerto para obtener el descriptor de una disciplina.
    """

    def __init__(
        self,
        event_store: EventStorePort,
        performances_ap: PerformancesAPPort,
        disciplina_descriptor: DisciplinaDescriptorPort,
    ) -> None:
        self._event_store = event_store
        self._performances_ap = performances_ap
        self._disciplina_descriptor = disciplina_descriptor

    async def handle(self, command: GenerarGrillaCommand) -> None:
        """Ejecuta el comando GenerarGrilla.

        Args:
            command: Datos para generar la grilla.

        Raises:
            IntervaloNoConfigurado: INV-C-01 — intervalo no configurado.
            GrillaYaConfirmada: La grilla fue confirmada — regeneración no permitida.
            SinPerformancesParaGrilla: No hay performances con AP.
        """
        stream_id = build_competencia_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)
        competencia = reconstruir_competencia(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )
        performances = await self._performances_ap.get_performances_con_ap(command.competencia_id)
        await self._bootstrap_performances_faltantes(command, performances)
        descriptor = self._disciplina_descriptor.describe(command.disciplina)
        competencia.generar_grilla(
            ot_inicio=command.ot_inicio,
            performances=performances,
            descriptor=descriptor,
            andariveles=command.andariveles,
        )
        await persistir_eventos_pendientes(
            event_store=self._event_store,
            stream_id=stream_id,
            aggregate=competencia,
        )

    async def _bootstrap_performances_faltantes(
        self,
        command: GenerarGrillaCommand,
        performances: list[PerformancesAPData],
    ) -> None:
        for performance_data in performances:
            stream_id = build_performance_stream_id(
                command.competencia_id,
                performance_data.atleta_id,
                command.disciplina,
            )
            if await self._event_store.load(stream_id):
                continue
            performance = Performance(
                performance_id=performance_data.performance_id,
                competencia_id=command.competencia_id,
                participante_id=performance_data.atleta_id,
                disciplina=command.disciplina,
            )
            performance.registrar_ap(performance_data.valor_ap, performance_data.unidad)
            await persistir_eventos_pendientes(
                event_store=self._event_store,
                stream_id=stream_id,
                aggregate=performance,
            )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID) -> str:
    """Construye el stream ID canónico para una Competencia.

    Format: "competencia-{competencia_id}"
    """
    return build_competencia_stream_id(competencia_id)
