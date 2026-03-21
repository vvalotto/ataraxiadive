"""Value Object UnidadMedida — unidad de medida del AP/RP."""
from __future__ import annotations

from enum import Enum


class UnidadMedida(str, Enum):
    """Unidades de medida usadas en las performances de apnea."""

    Metros = "Metros"
    Segundos = "Segundos"
