"""Excepciones de dominio del BC Resultados."""

from __future__ import annotations


class DomainError(Exception):
    """Base de todas las excepciones de dominio del BC Resultados."""


class ResultadosIncompletos(DomainError):
    """La lista de resultados no cubre todas las performances esperadas."""


class RankingYaCalculado(DomainError):
    """El ranking ya fue calculado para esta competencia y disciplina."""


class TorneoNoEncontrado(DomainError):
    """El torneo solicitado no existe en la base de datos de Torneo."""
