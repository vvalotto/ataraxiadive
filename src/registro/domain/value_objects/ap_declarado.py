from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida


@dataclass(frozen=True)
class APDeclarado:
    valor: Decimal
    unidad: UnidadMedida

    def __post_init__(self) -> None:
        if self.valor <= 0:
            raise ValueError("El AP debe ser mayor a cero")

    @classmethod
    def desde_disciplina(cls, disciplina: Disciplina, valor: Decimal) -> APDeclarado:
        return cls(
            valor=valor,
            unidad=UnidadMedida.Segundos if disciplina.es_tiempo() else UnidadMedida.Metros,
        )
