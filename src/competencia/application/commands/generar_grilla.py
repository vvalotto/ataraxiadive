"""Command y Handler para GenerarGrilla — US-2.1.2."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

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
        stream_id = _build_stream_id(command.competencia_id)
        events = await self._event_store.load(stream_id)

        competencia = Competencia.reconstitute(
            competencia_id=command.competencia_id,
            disciplina=command.disciplina,
            events=events,
        )

        performances = await self._performances_ap.get_performances_con_ap(
            command.competencia_id
        )

        descriptor = self._disciplina_descriptor.describe(command.disciplina)

        competencia.generar_grilla(
            ot_inicio=command.ot_inicio,
            performances=performances,
            descriptor=descriptor,
            andariveles=command.andariveles,
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
