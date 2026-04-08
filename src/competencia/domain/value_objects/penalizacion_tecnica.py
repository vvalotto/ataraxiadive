"""Value Object PenalizacionTecnica — infracción con deducción acumulable."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from competencia.domain.value_objects.tipo_penalizacion import TipoPenalizacion


@dataclass(frozen=True)
class PenalizacionTecnica:
    """Representa una penalización técnica que descuenta metros del RP."""

    tipo: TipoPenalizacion
    deduccion: Decimal

    def __post_init__(self) -> None:
        if self.deduccion <= 0:
            raise ValueError("La deduccion de una PenalizacionTecnica debe ser > 0")

    def to_payload(self) -> dict[str, str]:
        """Serializa a payload JSON-serializable."""
        return {"tipo": self.tipo.value, "deduccion": str(self.deduccion)}
