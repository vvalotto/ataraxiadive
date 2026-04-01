"""Implementación real de CompetenciaEstadoPort — consulta el stream de Competencia."""

from __future__ import annotations

from uuid import UUID

from competencia.domain.ports.competencia_estado_port import CompetenciaEstadoPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina


class CompetenciaEstadoAdapter(CompetenciaEstadoPort):
    """Implementación real del puerto CompetenciaEstadoPort.

    Lee el stream `competencia-{competencia_id}` del Event Store y proyecta
    el estado del aggregate para responder las consultas del BC Performance.

    Reemplaza al StubCompetenciaEstadoAdapter de SP1.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def is_plazo_vencido(self, competencia_id: UUID, disciplina: Disciplina) -> bool:
        """True si PlazoAPVencido fue emitido para esta competencia/disciplina.

        En Inc 2.1 el evento PlazoAPVencido no existe aún — retorna False.
        """
        events = await self._event_store.load(_build_stream_id(competencia_id))
        return any(e["event_type"] == "PlazoAPVencido" for e in events)

    async def is_grilla_confirmada(self, competencia_id: UUID, disciplina: Disciplina) -> bool:
        """True si GrillaConfirmada fue emitido para esta competencia."""
        events = await self._event_store.load(_build_stream_id(competencia_id))
        return any(e["event_type"] == "GrillaConfirmada" for e in events)

    async def is_en_ejecucion(self, competencia_id: UUID) -> bool:
        """True si CompetenciaIniciada existe y CompetenciaFinalizada no existe."""
        events = await self._event_store.load(_build_stream_id(competencia_id))
        event_types = {e["event_type"] for e in events}
        return "CompetenciaIniciada" in event_types and "CompetenciaFinalizada" not in event_types


def _build_stream_id(competencia_id: UUID) -> str:
    """Construye el stream ID canónico para una Competencia."""
    return f"competencia-{competencia_id}"
