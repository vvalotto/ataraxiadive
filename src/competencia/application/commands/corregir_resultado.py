"""Command y Handler para CorregirResultado — US-1.2.6."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida


# ── Excepciones de aplicación ─────────────────────────────────────────────────


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class CorregirResultadoCommand:
    """Comando para corregir el resultado efectivo de un atleta ya ejecutado.

    Attributes:
        competencia_id: Competencia en la que se ejecutó la performance.
        participante_id: Participante cuyo resultado se corrige.
        disciplina: Disciplina en la que compitió.
        valor_rp: Nuevo valor del Realized Performance corregido.
        unidad: Unidad de medida del RP corregido.
        registrado_por: Identificador del juez que realiza la corrección.
        motivo: Razón de la corrección — obligatorio (INV-P-12).
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    valor_rp: Decimal
    unidad: UnidadMedida
    registrado_por: str
    motivo: str


# ── Handler ───────────────────────────────────────────────────────────────────


class CorregirResultadoHandler:
    """Handler del comando CorregirResultado.

    Carga la Performance desde el Event Store, ejecuta corregir_resultado()
    y persiste ResultadoCorregido.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: CorregirResultadoCommand) -> None:
        """Ejecuta el comando CorregirResultado.

        Args:
            command: Datos de la corrección a registrar.

        Raises:
            PerformanceNoEncontrada: no existe Performance para este atleta.
            EstadoInvalidoParaCorregirResultado: Performance no en Ejecutada (INV-P-12/13).
            MotivoObligatorio: motivo ausente o vacío (INV-P-12).
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

        # Ejecuta (lanza EstadoInvalidoParaCorregirResultado o MotivoObligatorio si aplica)
        performance.corregir_resultado(
            valor_rp=command.valor_rp,
            unidad=command.unidad,
            registrado_por=command.registrado_por,
            motivo=command.motivo,
        )

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
