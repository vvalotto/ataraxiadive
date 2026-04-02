"""Aggregates del BC Resultados."""

from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.aggregates.ranking_overall import RankingOverall

__all__ = ["RankingCompetencia", "RankingOverall"]
