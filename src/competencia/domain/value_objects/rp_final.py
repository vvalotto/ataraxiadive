"""Value Object RPFinal — encapsula calculo de RP medido y penalizado."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica


@dataclass(frozen=True)
class RPFinal:
    """Representa el RP medido y el RP final observable."""

    medido: Decimal | None
    penalizado: Decimal | None

    @classmethod
    def desde_medicion(
        cls,
        rp_medido: Decimal | None,
        penalizaciones: tuple[PenalizacionTecnica, ...] = (),
    ) -> "RPFinal":
        """Calcula el RP final aplicando penalizaciones acumuladas."""
        if rp_medido is None:
            return cls(medido=None, penalizado=None)

        if not penalizaciones:
            return cls(medido=rp_medido, penalizado=None)

        deduccion_total = sum((p.deduccion for p in penalizaciones), start=Decimal("0"))
        rp_penalizado = max(rp_medido - deduccion_total, Decimal("0"))
        return cls(medido=rp_medido, penalizado=rp_penalizado)

    @property
    def observable(self) -> Decimal | None:
        """RP expuesto por el aggregate: penalizado si existe, medido en caso contrario."""
        return self.penalizado if self.penalizado is not None else self.medido
