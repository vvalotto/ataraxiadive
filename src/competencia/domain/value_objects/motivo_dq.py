"""Value Object MotivoDQ — catálogo formal de causas de descalificación."""

from __future__ import annotations

from enum import StrEnum


class MotivoDQ(StrEnum):
    """Códigos reglamentarios de descalificación para tarjeta roja."""

    BKO_SUPERFICIE = "BKO_SUPERFICIE"
    BKO_SUBACUATICO = "BKO_SUBACUATICO"
    PROTOCOLO_SUPERFICIE = "PROTOCOLO_SUPERFICIE"
    INFRACCION_TECNICA_DQ = "INFRACCION_TECNICA_DQ"
    NO_INICIO_EN_VENTANA = "NO_INICIO_EN_VENTANA"
    SALIDA_EN_FALSO = "SALIDA_EN_FALSO"

    def requiere_distancia_blackout(self) -> bool:
        """Indica si el motivo exige distancia de blackout asociada."""
        return self in {MotivoDQ.BKO_SUPERFICIE, MotivoDQ.BKO_SUBACUATICO}
