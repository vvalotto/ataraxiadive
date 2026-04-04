"""Query y Handler para ObtenerOverall — US-3.5.3."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from resultados.domain.aggregates.ranking_overall import RankingOverall
from shared.domain.ports.event_store_port import EventStorePort


@dataclass(frozen=True)
class ObtenerOverallQuery:
    """Query para obtener el overall calculado de un torneo."""

    torneo_id: UUID


@dataclass(frozen=True)
class OverallEntradaDTO:
    """DTO de respuesta para una entrada del ranking overall."""

    posicion: int
    atleta_id: str
    puntaje: int
    detalle: dict[str, int]
    en_podio: bool


@dataclass(frozen=True)
class OverallCategoriaDTO:
    """DTO agrupado por categoría para respuesta HTTP."""

    categoria: str
    entradas: list[OverallEntradaDTO]


class ObtenerOverallHandler:
    """Handler de la query ObtenerOverall.

    Lee el stream `ranking-overall-{torneo_id}` del Event Store de Resultados y
    proyecta las entradas del último overall calculado.
    """

    def __init__(self, ranking_store: EventStorePort) -> None:
        self._ranking_store = ranking_store

    async def handle(self, query: ObtenerOverallQuery) -> list[OverallCategoriaDTO]:
        """Retorna las entradas calculadas del overall.

        Returns:
            Lista ordenada por posición.
            Lista vacía si el overall aún no fue calculado.
        """
        stream_id = f"ranking-overall-{query.torneo_id}"
        events = await self._ranking_store.load(stream_id)
        ranking = RankingOverall.reconstitute(query.torneo_id, events)
        agrupado: dict[str, list[OverallEntradaDTO]] = defaultdict(list)
        for entry in ranking.entries:
            agrupado[entry.categoria.value].append(
                OverallEntradaDTO(
                    posicion=entry.posicion,
                    atleta_id=str(entry.atleta_id),
                    puntaje=entry.puntaje,
                    detalle=dict(entry.detalle),
                    en_podio=entry.en_podio,
                )
            )
        return [
            OverallCategoriaDTO(categoria=categoria, entradas=entradas)
            for categoria, entradas in sorted(agrupado.items())
        ]
