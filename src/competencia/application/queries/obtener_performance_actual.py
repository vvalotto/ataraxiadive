"""Query y Handler para ObtenerPerformanceActual — US-1.3.1 / US-2.2.2."""
from __future__ import annotations

import json
from dataclasses import dataclass
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.disciplina_descriptor_port import DisciplinaDescriptorPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.estado_performance import EstadoPerformance


@dataclass
class PerformanceActualDTO:
    """Read model de la performance que el juez está evaluando en este momento."""

    performance_id: str
    nombre_atleta: str
    ap_declarado: str
    unidad: str
    unidad_esperada: str
    andarivel: int
    estado: str


@dataclass(frozen=True)  # pylint: disable=too-few-public-methods
class ObtenerPerformanceActualQuery:
    """Query para obtener la performance activa de una competencia."""

    competencia_id: UUID


class ObtenerPerformanceActualHandler:  # pylint: disable=too-few-public-methods
    """Proyecta el read model PerformanceActual desde el Event Store.

    Retorna la performance en estado Llamada o ResultadoRegistrado.
    Si hay más de una (condición de error operativo), retorna la primera.
    Retorna None si no hay performance activa.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    _ESTADOS_ACTIVOS = {EstadoPerformance.Llamada, EstadoPerformance.ResultadoRegistrado}

    def __init__(
        self, event_store: EventStorePort, disciplina_descriptor: DisciplinaDescriptorPort
    ) -> None:
        self._event_store = event_store
        self._disciplina_descriptor = disciplina_descriptor

    async def handle(self, query: ObtenerPerformanceActualQuery) -> PerformanceActualDTO | None:
        """Ejecuta la query y retorna la performance activa, o None."""
        prefix = f"performance-{query.competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        for stream in all_streams:
            performance = Performance.reconstitute(stream)
            if performance.estado in self._ESTADOS_ACTIVOS:
                return self._to_dto(performance, stream)
        return None

    def _to_dto(
        self, performance: Performance, stream: list[dict]
    ) -> PerformanceActualDTO:
        ap = performance.ap
        ap_valor = str(ap.valor) if ap else ""
        ap_unidad = ap.unidad.value if ap else ""

        descriptor = self._disciplina_descriptor.describe(performance.disciplina)
        andarivel = self._extract_andarivel(stream)
        participante_id = str(performance.participante_id)

        return PerformanceActualDTO(
            performance_id=str(performance.performance_id),
            nombre_atleta=f"Atleta-{participante_id[:8]}",
            ap_declarado=ap_valor,
            unidad=ap_unidad,
            unidad_esperada=descriptor.unidad_esperada.value,
            andarivel=andarivel,
            estado=performance.estado.value if performance.estado else "",
        )

    @staticmethod
    def _extract_andarivel(stream: list[dict]) -> int:
        for event in stream:
            if event["event_type"] == "AtletaLlamado":
                payload = event["payload"]
                if isinstance(payload, str):
                    payload = json.loads(payload)
                return int(payload.get("posicion_grilla", 0))
        return 0
