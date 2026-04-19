"""Command y Handler para CorregirResultadoTrasDNS — US-ADJ-7.1."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from competencia.application.commands._handler_utils import (
    build_performance_stream_id,
    cargar_o_fallar,
    persistir_eventos_pendientes,
    reconstruir_performance,
)
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida


class PerformanceNoEncontrada(Exception):
    """El stream de la Performance no existe en el Event Store."""


@dataclass(frozen=True)
class CorregirResultadoTrasDNSCommand:
    """Comando para corregir un DNS registrado por error."""

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    valor_rp: Decimal
    unidad: UnidadMedida
    registrado_por: str
    motivo_correccion: str


class CorregirResultadoTrasDNSHandler:
    """Handler del comando CorregirResultadoTrasDNS."""

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, command: CorregirResultadoTrasDNSCommand) -> None:
        """Ejecuta el comando y persiste ResultadoCorregidoTrasDNS."""
        stream_id = build_performance_stream_id(
            command.competencia_id,
            command.participante_id,
            command.disciplina,
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
        performance.corregir_resultado_tras_dns(
            valor_rp=command.valor_rp,
            unidad=command.unidad,
            registrado_por=command.registrado_por,
            motivo_correccion=command.motivo_correccion,
        )
        await persistir_eventos_pendientes(
            event_store=self._event_store,
            stream_id=stream_id,
            aggregate=performance,
        )
