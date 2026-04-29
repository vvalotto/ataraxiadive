"""Adaptador PerformancesAPAdapter — lee AP primario desde Registro."""

from __future__ import annotations

from uuid import NAMESPACE_URL, UUID, uuid5

from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.competencias_por_torneo_port import CompetenciasPorTorneoPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_ap_port import (
    PerformancesAPData,
    PerformancesAPPort,
)
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from shared.domain.value_objects.disciplina import Disciplina


class PerformancesAPAdapter(PerformancesAPPort):
    """Implementación de PerformancesAPPort usando AP declarados en inscripción."""

    def __init__(
        self,
        event_store: EventStorePort,
        competencias_por_torneo: CompetenciasPorTorneoPort,
        inscripcion_repo: InscripcionRepositoryPort,
    ) -> None:
        self._event_store = event_store
        self._competencias_por_torneo = competencias_por_torneo
        self._inscripcion_repo = inscripcion_repo

    async def get_performances_con_ap(self, competencia_id: UUID) -> list[PerformancesAPData]:
        record = await self._competencias_por_torneo.obtener_por_competencia_id(competencia_id)
        if record is None:
            return []

        disciplina = Disciplina(record.disciplina)
        result: list[PerformancesAPData] = []
        for inscripcion in await self._inscripcion_repo.find_active_by_torneo(record.torneo_id):
            ap = inscripcion.obtener_ap(disciplina)
            if ap is None:
                continue
            result.append(
                PerformancesAPData(
                    performance_id=await self._resolver_performance_id(
                        competencia_id,
                        inscripcion.atleta_id,
                        disciplina,
                    ),
                    atleta_id=inscripcion.atleta_id,
                    valor_ap=ap.valor,
                    unidad=ap.unidad,
                )
            )
        return result

    async def _resolver_performance_id(
        self,
        competencia_id: UUID,
        atleta_id: UUID,
        disciplina: Disciplina,
    ) -> UUID:
        stream_id = f"performance-{competencia_id}-{atleta_id}-{disciplina.value}"
        events = await self._event_store.load(stream_id)
        if events:
            return Performance.reconstitute(events).performance_id
        return uuid5(NAMESPACE_URL, f"{competencia_id}:{atleta_id}:{disciplina.value}")
