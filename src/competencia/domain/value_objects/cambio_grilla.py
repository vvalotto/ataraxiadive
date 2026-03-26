"""Value Object CambioGrilla — representa un ajuste manual sobre una entrada de la grilla."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class CambioGrilla:
    """Describe un cambio puntual sobre una entrada de la Grilla de Salida.

    Attributes:
        performance_id: Identificador de la Performance a modificar.
        campo: Campo a cambiar: "posicion" o "andarivel".
        valor_nuevo: Nuevo valor para el campo (entero positivo).
    """

    performance_id: UUID
    campo: Literal["posicion", "andarivel"]
    valor_nuevo: int
