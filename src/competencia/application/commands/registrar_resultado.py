"""Command y Handler para RegistrarResultado — US-1.2.3."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.disciplina_descriptor_port import DisciplinaDescriptorPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida


# ── Excepciones de aplicación ─────────────────────────────────────────────────


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


class UnidadIncompatible(Exception):
    """La unidad del comando no coincide con la unidad esperada por la disciplina."""


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RegistrarResultadoCommand:
    """Comando para registrar el resultado efectivo (RP) de un atleta.

    Attributes:
        competencia_id: Competencia en la que se ejecutó la performance.
        participante_id: Participante que completó su actuación.
        disciplina: Disciplina en la que compitió.
        valor_rp: Realized Performance — marca efectivamente lograda.
        unidad: Unidad de medida del RP (Metros | Segundos).
        registrado_por: Identificador del juez que registra el resultado.
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    valor_rp: Decimal
    unidad: UnidadMedida
    registrado_por: str


# ── Handler ───────────────────────────────────────────────────────────────────


class RegistrarResultadoHandler:
    """Handler del comando RegistrarResultado.

    Carga la Performance desde el Event Store, ejecuta registrar_resultado()
    y persiste ResultadoRegistrado. No requiere puertos externos adicionales.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(
        self, event_store: EventStorePort, disciplina_descriptor: DisciplinaDescriptorPort
    ) -> None:
        self._event_store = event_store
        self._disciplina_descriptor = disciplina_descriptor

    async def handle(self, command: RegistrarResultadoCommand) -> None:
        """Ejecuta el comando RegistrarResultado.

        Args:
            command: Datos del resultado a registrar.

        Raises:
            UnidadIncompatible: la unidad no coincide con la disciplina.
            PerformanceNoEncontrada: no existe Performance para este atleta.
            EstadoInvalidoParaRegistrarResultado: Performance no está en Llamada (INV-P-06).
        """
        descriptor = self._disciplina_descriptor.describe(command.disciplina)
        if command.unidad != descriptor.unidad_esperada:
            raise UnidadIncompatible(
                f"{command.disciplina.value} requiere {descriptor.unidad_esperada.value}, "
                f"recibido {command.unidad.value}"
            )

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

        # Ejecutar (lanza EstadoInvalidoParaRegistrarResultado si no está en Llamada)
        performance.registrar_resultado(command.valor_rp, command.unidad, command.registrado_por)

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
