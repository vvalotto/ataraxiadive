"""Query y Handler para ObtenerRanking — US-2.4.2."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from uuid import UUID

from shared.domain.ports.event_store_port import EventStorePort
from shared.domain.value_objects.disciplina import Disciplina
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia

# ── Query ─────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ObtenerRankingQuery:
    """Query para obtener el ranking calculado de una disciplina.

    Attributes:
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina del ranking.
    """

    competencia_id: UUID
    disciplina: Disciplina


# ── DTO ───────────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RankingEntradaDTO:
    """DTO de respuesta para una entrada del ranking.

    Attributes:
        posicion: Posición en el ranking.
        atleta_id: Identificador del participante (str UUID).
        rp: Marca efectiva como string, o None.
        unidad: Unidad de medida, o None.
        tarjeta: Tipo de tarjeta, o None.
        es_dns: True si el atleta no se presentó.
        en_podio: True si está en el podio (posición 1, 2 o 3).
        puntos: Puntaje FAAS del atleta (2 decimales). "0.00" sin algoritmo.
    """

    posicion: int
    atleta_id: str
    rp: str | None
    unidad: str | None
    tarjeta: str | None
    es_dns: bool
    en_podio: bool
    puntos: str = "0.00"
    motivo_dq: str | None = None
    penalizaciones: tuple[str, ...] = ()
    rp_medido: str | None = None


@dataclass(frozen=True)
class RankingCategoriaDTO:
    """DTO agrupado por categoría para respuesta HTTP."""

    categoria: str
    entradas: list[RankingEntradaDTO]


# ── Handler ───────────────────────────────────────────────────────────────────


class ObtenerRankingHandler:
    """Handler de la query ObtenerRanking.

    Lee el stream `ranking-{competencia_id}-{disciplina}` del Event Store de
    BC Resultados y devuelve las entradas del último ranking calculado.

    Args:
        ranking_store: Event Store del BC Resultados.
    """

    def __init__(self, ranking_store: EventStorePort) -> None:
        self._ranking_store = ranking_store

    async def handle(self, query: ObtenerRankingQuery) -> list[RankingCategoriaDTO]:
        """Retorna las entradas del ranking calculado.

        Args:
            query: Datos de la consulta.

        Returns:
            Lista de RankingEntradaDTO ordenada por posición.
            Lista vacía si el ranking aún no fue calculado.
        """
        stream_id = f"ranking-{query.competencia_id}-{query.disciplina.value}"
        events = await self._ranking_store.load(stream_id)

        ranking = RankingCompetencia.reconstitute(
            competencia_id=query.competencia_id,
            disciplina=query.disciplina,
            events=events,
        )

        agrupado: dict[str, list[RankingEntradaDTO]] = defaultdict(list)
        for entry in ranking.entries:
            agrupado[entry.categoria.value].append(
                RankingEntradaDTO(
                    posicion=entry.posicion,
                    atleta_id=str(entry.atleta_id),
                    rp=str(entry.rp) if entry.rp is not None else None,
                    unidad=entry.unidad,
                    tarjeta=entry.tarjeta,
                    es_dns=entry.es_dns,
                    en_podio=entry.en_podio,
                    puntos=str(entry.puntos),
                )
            )
        return [
            RankingCategoriaDTO(categoria=categoria, entradas=entradas)
            for categoria, entradas in sorted(agrupado.items())
        ]
