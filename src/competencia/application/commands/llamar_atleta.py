"""Command y Handler para LlamarAtleta — US-1.2.2, US-2.3.1."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.andariveles_activos_port import AndarivelesActivosPort
from competencia.domain.ports.competencia_estado_port import CompetenciaEstadoPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


# ── Excepciones de aplicación ─────────────────────────────────────────────────


class CompetenciaNoEnEjecucion(Exception):
    """INV-P-05: la Competencia no está en estado EnEjecucion."""


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


class AndarivelesConflicto(Exception):
    """INV-C-05: el andarivel ya tiene una Performance en estado Llamada."""


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class LlamarAtletaCommand:
    """Comando para llamar a un atleta según el orden de grilla.

    Attributes:
        competencia_id: Competencia en ejecución.
        participante_id: Participante a llamar.
        disciplina: Disciplina en la que compite.
        ot_programado: Official Top programado para este atleta.
        posicion_grilla: Número de orden en la grilla de salida.
        andarivel: Número de andarivel asignado al atleta.
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    ot_programado: datetime
    posicion_grilla: int
    andarivel: int = 1


# ── Handler ───────────────────────────────────────────────────────────────────


class LlamarAtletaHandler:
    """Handler del comando LlamarAtleta.

    Verifica INV-P-05 (Competencia en EnEjecucion), INV-C-05 (andarivel libre),
    carga la Performance desde el Event Store, ejecuta llamar() y persiste
    AtletaLlamado.

    Args:
        event_store: Puerto de persistencia de eventos.
        competencia_estado: Puerto para verificar estado de Competencia.
        andariveles_activos: Puerto para verificar conflictos de andarivel.
    """

    def __init__(
        self,
        event_store: EventStorePort,
        competencia_estado: CompetenciaEstadoPort,
        andariveles_activos: AndarivelesActivosPort | None = None,
    ) -> None:
        self._event_store = event_store
        self._competencia_estado = competencia_estado
        self._andariveles_activos = andariveles_activos

    async def handle(self, command: LlamarAtletaCommand) -> None:
        """Ejecuta el comando LlamarAtleta.

        Args:
            command: Datos para llamar al atleta.

        Raises:
            CompetenciaNoEnEjecucion: INV-P-05 — competencia no iniciada.
            AndarivelesConflicto: INV-C-05 — andarivel ya ocupado.
            PerformanceNoEncontrada: no existe AP registrado para este atleta.
            EstadoInvalidoParaLlamar: Performance no está en AnunciadaAP.
        """
        # INV-P-05: Competencia en EnEjecucion?
        if not await self._competencia_estado.is_en_ejecucion(command.competencia_id):
            raise CompetenciaNoEnEjecucion(
                f"INV-P-05: competencia={command.competencia_id} no está en EnEjecucion"
            )

        # INV-C-05: andarivel libre? (solo si el port está inyectado)
        andarivel_activo = (
            self._andariveles_activos is not None
            and await self._andariveles_activos.is_andarivel_activo(
                command.competencia_id, command.disciplina, command.andarivel
            )
        )
        if andarivel_activo:
            raise AndarivelesConflicto(
                f"INV-C-05: andarivel={command.andarivel} ya tiene una Performance en Llamada"
            )

        # Cargar Performance desde Event Store
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

        # Ejecutar (lanza EstadoInvalidoParaLlamar si no está en AnunciadaAP)
        performance.llamar(command.ot_programado, command.posicion_grilla, command.andarivel)

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
