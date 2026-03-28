"""Adaptador ResultadosCompetenciaAdapter — ACL que lee resultados de BC Competencia."""
from __future__ import annotations

from uuid import UUID

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from resultados.domain.ports.resultados_competencia_port import (
    ResultadoFinal,
    ResultadosCompetenciaPort,
)


class ResultadosCompetenciaAdapter(ResultadosCompetenciaPort):
    """ACL: lee los streams de BC Competencia y traduce al modelo de BC Resultados.

    Carga todos los streams `performance-{competencia_id}-*` del Event Store de
    BC Competencia, reconstituye cada Performance y extrae los datos necesarios
    para construir el ranking.

    Args:
        competencia_event_store: Event Store del BC Competencia.
    """

    def __init__(self, competencia_event_store: EventStorePort) -> None:
        self._event_store = competencia_event_store

    async def get_resultados_finales(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> list[ResultadoFinal]:
        """Retorna los resultados finales de todas las performances de la disciplina.

        Solo incluye performances en estado Ejecutada o DNS.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina a consultar.

        Returns:
            Lista de ResultadoFinal para todas las performances finalizadas.
        """
        prefix = f"performance-{competencia_id}-"
        all_streams = await self._event_store.load_all_streams_with_prefix(prefix)

        resultados: list[ResultadoFinal] = []
        for stream_events in all_streams:
            if not stream_events:
                continue

            performance = Performance.reconstitute(stream_events)

            if performance.disciplina != disciplina:
                continue
            if performance.estado not in (EstadoPerformance.Ejecutada, EstadoPerformance.DNS):
                continue

            es_dns = performance.estado == EstadoPerformance.DNS
            tarjeta = performance.tarjeta.value if performance.tarjeta is not None else None
            unidad = performance.ap.unidad.value if performance.ap is not None else None

            resultados.append(ResultadoFinal(
                atleta_id=performance.participante_id,
                rp=performance.rp if not es_dns else None,
                unidad=unidad if not es_dns else None,
                tarjeta=tarjeta,
                es_dns=es_dns,
            ))

        return resultados
