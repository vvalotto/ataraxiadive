"""Value Object DisciplinaDescriptor — reglas de medición y ordenamiento por disciplina."""

from __future__ import annotations

from dataclasses import dataclass

from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida


@dataclass(frozen=True)
class DisciplinaDescriptor:
    """Encapsula las reglas de una disciplina: unidad esperada y orden de grilla.

    Política P-01:
        - STA (tiempo): unidad=Segundos, orden_ascendente=True (menor AP primero)
        - SPE_* (tiempo): unidad=Segundos, orden_ascendente=False
        - Distancia (DNF, DYN, ...): unidad=Metros, orden_ascendente=True (menor AP primero)

    Attributes:
        disciplina: Disciplina a la que pertenece este descriptor.
        unidad_esperada: Unidad de medida válida para APs y RPs de esta disciplina.
        orden_ascendente: True si la grilla ordena de menor a mayor AP.
    """

    disciplina: Disciplina
    unidad_esperada: UnidadMedida
    orden_ascendente: bool

    @classmethod
    def para(cls, disciplina: Disciplina) -> DisciplinaDescriptor:
        """Construye el descriptor canónico para una disciplina.

        Args:
            disciplina: Disciplina para la que se construye el descriptor.

        Returns:
            DisciplinaDescriptor con unidad y orden correctos según política P-01.
        """
        return cls(
            disciplina=disciplina,
            unidad_esperada=cls._resolver_unidad(disciplina),
            orden_ascendente=cls._resolver_orden(disciplina),
        )

    @staticmethod
    def _resolver_unidad(disciplina: Disciplina) -> UnidadMedida:
        if disciplina.es_tiempo():
            return UnidadMedida.Segundos
        return UnidadMedida.Metros

    @staticmethod
    def _resolver_orden(disciplina: Disciplina) -> bool:
        if disciplina.es_spe() and disciplina != Disciplina.SPE:
            return False
        return True
