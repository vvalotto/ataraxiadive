"""Value Object IntervaloDisciplina — tiempo en minutos entre OTs consecutivos."""
from __future__ import annotations

from dataclasses import dataclass


class IntervaloInvalido(Exception):
    """Intervalo en minutos debe ser > 0 (INV-C-01)."""


@dataclass(frozen=True)
class IntervaloDisciplina:
    """Tiempo en minutos entre Official Tops consecutivos.

    Inmutable. Valida que el valor sea positivo en construcción.

    Attributes:
        minutos: Tiempo en minutos entre OTs. Debe ser > 0.

    Raises:
        IntervaloInvalido: Si minutos <= 0.
    """

    minutos: int

    def __post_init__(self) -> None:
        """Valida INV-C-01: intervalo debe ser > 0."""
        if self.minutos <= 0:
            raise IntervaloInvalido(
                f"IntervaloDisciplina debe ser > 0, recibido: {self.minutos}"
            )
