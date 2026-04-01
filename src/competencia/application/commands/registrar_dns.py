"""Command y Handler para RegistrarDNS — US-1.2.5 / US-2.4.1."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from typing import Awaitable, Callable

from competencia.application._p08_finalizacion import trigger_finalizacion_si_corresponde
from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_estado_port import PerformancesEstadoPort
from competencia.domain.value_objects.disciplina import Disciplina

# ── Excepciones de aplicación ─────────────────────────────────────────────────


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RegistrarDNSCommand:
    """Comando para registrar que el atleta no se presentó al OT (DNS).

    Attributes:
        competencia_id: Competencia en la que debía ejecutarse la performance.
        participante_id: Participante que no se presentó.
        disciplina: Disciplina en la que debía competir.
        registrado_por: Identificador del juez que registra el DNS.
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    registrado_por: str


# ── Handler ───────────────────────────────────────────────────────────────────


class RegistrarDNSHandler:
    """Handler del comando RegistrarDNS.

    Carga la Performance desde el Event Store, ejecuta registrar_dns()
    y persiste DNSRegistrado. Tras persistir, verifica P-08: si todas las
    performances finalizaron, emite CompetenciaFinalizada automáticamente.

    Args:
        event_store: Puerto de persistencia de eventos.
        performances_estado: Puerto para verificar P-08. None = sin verificación.
    """

    def __init__(
        self,
        event_store: EventStorePort,
        performances_estado: PerformancesEstadoPort | None = None,
        on_finalizada: Callable[[UUID, Disciplina], Awaitable[None]] | None = None,
    ) -> None:
        self._event_store = event_store
        self._performances_estado = performances_estado
        self._on_finalizada = on_finalizada

    async def handle(self, command: RegistrarDNSCommand) -> None:
        """Ejecuta el comando RegistrarDNS.

        Args:
            command: Datos del DNS a registrar.

        Raises:
            PerformanceNoEncontrada: no existe Performance para este atleta.
            EstadoInvalidoParaRegistrarDNS: Performance no está en Llamada (INV-P-08).
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

        # Ejecuta (lanza EstadoInvalidoParaRegistrarDNS si aplica)
        performance.registrar_dns(command.registrado_por)

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
    """Construye el stream ID canónico para una Performance.

    Format: "performance-{competencia_id}-{participante_id}-{disciplina}"
    """
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"
