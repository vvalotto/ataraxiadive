"""Value Object AP — Announced Performance declarada por el atleta."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from competencia.domain.value_objects.unidad_medida import UnidadMedida


class ValorAPInvalido(Exception):
    """INV-P-01: el valor del AP debe ser estrictamente mayor que cero."""


@dataclass(frozen=True)
class AP:
    """Announced Performance declarada por el atleta antes de competir.

    Invariante:
        INV-P-01: valor > 0

    Attributes:
        valor: Marca declarada (metros o segundos según disciplina).
        unidad: Unidad de medida (Metros | Segundos).
    """

    valor: Decimal
    unidad: UnidadMedida

    def __post_init__(self) -> None:
        """Valida INV-P-01: valorAP debe ser > 0."""
        if self.valor <= Decimal("0"):
            raise ValorAPInvalido(
                f"INV-P-01: valorAP debe ser > 0, recibido: {self.valor}"
            )

    def __str__(self) -> str:
        return f"{self.valor} {self.unidad.value}"
