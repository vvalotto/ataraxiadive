"""Value Object EstadoCompetencia — máquina de estados del aggregate Competencia."""

from __future__ import annotations

from enum import StrEnum


class EstadoCompetencia(StrEnum):
    """Estados posibles del aggregate Competencia.

    Transiciones válidas:
        Preparacion → Confirmada → EnEjecucion → Finalizada
    """

    Preparacion = "Preparacion"
    Confirmada = "Confirmada"
    EnEjecucion = "EnEjecucion"
    Finalizada = "Finalizada"
