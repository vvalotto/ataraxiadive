"""Command y Handler para CalcularOverall — US-3.5.1 / US-5.6.4."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.ports.competencias_por_torneo_port import CompetenciasPorTorneoPort
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.aggregates.ranking_overall import RankingOverall
from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class CalcularOverallCommand:
    """Comando para calcular el ranking overall de un torneo."""

    torneo_id: UUID
    disciplinas: list[Disciplina]


class CalcularOverallHandler:
    """Handler del comando CalcularOverall.

    Usa la proyeccion materializada para mapear torneo -> competencia/disciplina
    y el Event Store de Resultados para leer los rankings ya calculados por disciplina.
    """

    def __init__(
        self,
        ranking_store: EventStorePort,
        competencias_por_torneo: CompetenciasPorTorneoPort,
    ) -> None:
        self._ranking_store = ranking_store
        self._competencias_por_torneo = competencias_por_torneo

    async def handle(self, command: CalcularOverallCommand) -> list:
        """Calcula y persiste el overall del torneo.

        Raises:
            DisciplinasNoFinalizadas: si alguna disciplina no tiene ranking calculado.
        """
        competencias = await self._mapear_competencias_por_torneo(command)
        if not competencias:
            return []

        rankings_por_disciplina = {}
        for disciplina, competencia_id in competencias.items():
            stream_id = f"ranking-{competencia_id}-{disciplina.value}"
            events = await self._ranking_store.load(stream_id)
            ranking = RankingCompetencia.reconstitute(competencia_id, disciplina, events)
            rankings_por_disciplina[disciplina] = ranking.entries

        overall_stream = _build_stream_id(command.torneo_id)
        existing = await self._ranking_store.load(overall_stream)
        ranking_overall = RankingOverall.reconstitute(command.torneo_id, existing)
        entries = ranking_overall.calcular(command.torneo_id, rankings_por_disciplina)

        for event in ranking_overall.pull_events():
            await self._ranking_store.append(
                stream_id=overall_stream,
                event_type=event.event_type,
                payload=event.to_payload(),
            )
        return entries

    async def _mapear_competencias_por_torneo(
        self, command: CalcularOverallCommand
    ) -> dict[Disciplina, UUID]:
        """Obtiene la competencia por disciplina para un torneo dado desde la proyeccion."""
        records = await self._competencias_por_torneo.listar_por_torneo(command.torneo_id)
        disciplinas_buscadas = set(command.disciplinas)
        mapeo: dict[Disciplina, UUID] = {}
        for record in records:
            disciplina = Disciplina(record.disciplina)
            if disciplina in disciplinas_buscadas:
                mapeo[disciplina] = record.competencia_id
        return mapeo


def _build_stream_id(torneo_id: UUID) -> str:
    """Construye el stream ID canónico para RankingOverall."""
    return f"ranking-overall-{torneo_id}"
