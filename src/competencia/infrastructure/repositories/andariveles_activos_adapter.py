"""Adaptador AndarivelesActivosAdapter — implementación de AndarivelesActivosPort."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.andariveles_activos_port import (
    AndarivelesActivosData,
    AndarivelesActivosPort,
)
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance


class AndarivelesActivosAdapter(AndarivelesActivosPort):
    """Implementación de AndarivelesActivosPort que proyecta el estado desde el Event Store.

    Carga todos los streams `performance-{competencia_id}-*-{disciplina}`, reconstituye
    cada Performance y proyecta el estado de cada andarivel: ocupado si la Performance
    está en estado Llamada.

    Args:
        event_store: Puerto de persistencia de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def get_andariveles_activos(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        andariveles: int,
    ) -> list[AndarivelesActivosData]:
        """Proyecta el estado de cada andarivel para la competencia y disciplina.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina en ejecución.
            andariveles: Número total de andariveles configurados en la grilla.

        Returns:
            Lista de AndarivelesActivosData, un elemento por andarivel (1..N).
        """
        performances_en_llamada = await self._get_performances_en_llamada(
            competencia_id, disciplina
        )

        # Construir mapa andarivel → performance activa
        activos: dict[int, Performance] = {}
        for perf in performances_en_llamada:
            if perf.andarivel is not None:
                activos[perf.andarivel] = perf

        result: list[AndarivelesActivosData] = []
        for numero in range(1, andariveles + 1):
            perf_activa = activos.get(numero)
            if perf_activa is not None:
                ot: datetime | None = perf_activa._ot_programado  # noqa: SLF001
                result.append(
                    AndarivelesActivosData(
                        numero=numero,
                        ocupado=True,
                        atleta_id=perf_activa.participante_id,
                        performance_id=perf_activa.performance_id,
                        ot_programado=ot,
                    )
                )
            else:
                result.append(
                    AndarivelesActivosData(
                        numero=numero,
                        ocupado=False,
                        atleta_id=None,
                        performance_id=None,
                        ot_programado=None,
                    )
                )

        return result

    async def is_andarivel_activo(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        numero_andarivel: int,
    ) -> bool:
        """Indica si el andarivel tiene una Performance en estado Llamada.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina en ejecución.
            numero_andarivel: Número de andarivel a verificar.

        Returns:
            True si el andarivel está ocupado.
        """
        performances_en_llamada = await self._get_performances_en_llamada(
            competencia_id, disciplina
        )
        return any(p.andarivel == numero_andarivel for p in performances_en_llamada)

    async def _get_performances_en_llamada(
        self, competencia_id: UUID, disciplina: Disciplina
    ) -> list[Performance]:
        """Carga y filtra las performances en estado Llamada para la disciplina.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a filtrar.

        Returns:
            Lista de Performance en estado Llamada con andarivel asignado.
        """
        prefix = f"performance-{competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        result: list[Performance] = []
        for stream_events in all_streams:
            if not stream_events:
                continue

            performance = Performance.reconstitute(stream_events)
            if performance.disciplina != disciplina:
                continue
            if performance.estado != EstadoPerformance.Llamada:
                continue

            result.append(performance)

        return result
