"""Command y Handler para CalcularOverall — US-3.5.1."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from resultados.domain.aggregates.ranking_overall import RankingOverall
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class CalcularOverallCommand:
    """Comando para calcular el ranking overall de un torneo."""

    torneo_id: UUID
    disciplinas: list[Disciplina]


class CalcularOverallHandler:
    """Handler del comando CalcularOverall.

    Usa el Event Store de Competencia para mapear torneo -> competencia/disciplina
    y el Event Store de Resultados para leer los rankings ya calculados por disciplina.
    """

    def __init__(
        self,
        ranking_store: EventStorePort,
        competencia_store: EventStorePort,
    ) -> None:
        self._ranking_store = ranking_store
        self._competencia_store = competencia_store

    async def handle(self, command: CalcularOverallCommand) -> list:
        """Calcula y persiste el overall del torneo."""
        competencias = await _mapear_competencias_por_torneo(
            self._competencia_store, command.torneo_id, command.disciplinas
        )
        rankings_por_disciplina = {}
        for disciplina, competencia_id in competencias.items():
            stream_id = f"ranking-{competencia_id}-{disciplina.value}"
            events = await self._ranking_store.load(stream_id)
            ranking = RankingCompetencia.reconstitute(competencia_id, disciplina, events)
            if ranking.entries:
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
    competencia_store: EventStorePort,
    torneo_id: UUID,
    disciplinas: list[Disciplina],
) -> dict[Disciplina, UUID]:
    """Obtiene la competencia por disciplina para un torneo dado."""
    streams = await competencia_store.load_all_streams_with_prefix("competencia-")
    disciplinas_buscadas = set(disciplinas)
    mapeo: dict[Disciplina, UUID] = {}

    for events in streams:
        for event in events:
            if event["event_type"] != "IntervaloOTConfigurado":
                continue
            payload = event["payload"]
            torneo_raw = payload.get("torneo_id")
            if torneo_raw != str(torneo_id):
                continue
            disciplina = Disciplina(payload["disciplina"])
            if disciplina not in disciplinas_buscadas:
                continue
            mapeo[disciplina] = UUID(payload["competencia_id"])
            break
    return mapeo


def _build_stream_id(torneo_id: UUID) -> str:
    """Construye el stream ID canónico para RankingOverall."""
    return f"ranking-overall-{torneo_id}"
