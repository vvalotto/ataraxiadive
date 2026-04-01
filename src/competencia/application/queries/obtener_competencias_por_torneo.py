"""Query y Handler para ObtenerCompetenciasPorTorneo — US-3.3.1."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from competencia.domain.ports.event_store_port import EventStorePort


@dataclass
class CompetenciaSummaryDTO:
    """Resumen de una competencia asociada a un torneo."""

    competencia_id: UUID
    disciplina: str
    torneo_id: UUID


@dataclass(frozen=True)
class ObtenerCompetenciasPorTorneoQuery:
    """Query para listar competencias de un torneo."""

    torneo_id: UUID


class ObtenerCompetenciasPorTorneoHandler:
    """Escanea el Event Store y retorna las competencias de un torneo.

    Itera los streams con prefijo 'competencia-' y filtra aquellos cuyo
    primer evento IntervaloOTConfigurado tenga el torneo_id indicado.

    Args:
        event_store: Puerto de lectura de eventos.
    """

    def __init__(self, event_store: EventStorePort) -> None:
        self._event_store = event_store

    async def handle(self, query: ObtenerCompetenciasPorTorneoQuery) -> list[CompetenciaSummaryDTO]:
        """Retorna la lista de competencias pertenecientes al torneo."""
        streams = await self._event_store.load_all_streams_with_prefix("competencia-")
        result: list[CompetenciaSummaryDTO] = []

        for stream in streams:
            for event in stream:
                if event["event_type"] != "IntervaloOTConfigurado":
                    continue
                payload = event["payload"]
                raw_torneo_id = payload.get("torneo_id")
                if raw_torneo_id is None:
                    break
                if UUID(raw_torneo_id) == query.torneo_id:
                    result.append(
                        CompetenciaSummaryDTO(
                            competencia_id=UUID(payload["competencia_id"]),
                            disciplina=payload["disciplina"],
                            torneo_id=query.torneo_id,
                        )
                    )
                break  # solo el primer IntervaloOTConfigurado define el torneo_id

        return result
