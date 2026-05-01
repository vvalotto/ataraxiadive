"""Puertos del BC Resultados."""

from resultados.domain.ports.algoritmo_puntaje import AlgoritmoPuntaje
from resultados.domain.ports.resultados_competencia_port import (
    AtletaCategoriaPort,
    ResultadoFinal,
    ResultadosCompetenciaPort,
)

__all__ = [
    "AlgoritmoPuntaje",
    "AtletaCategoriaPort",
    "ResultadoFinal",
    "ResultadosCompetenciaPort",
]
