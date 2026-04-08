"""Catálogo de penalizaciones técnicas acumulables."""

from __future__ import annotations

from enum import StrEnum


class TipoPenalizacion(StrEnum):
    """Códigos reglamentarios de penalización técnica."""

    SIN_CONTACTO_PARED = "SIN_CONTACTO_PARED"
    FUERA_DE_CARRIL = "FUERA_DE_CARRIL"
    ASISTENTE_EN_ZONA = "ASISTENTE_EN_ZONA"
    PATADA_DELFIN_BIALETAS = "PATADA_DELFIN_BIALETAS"
