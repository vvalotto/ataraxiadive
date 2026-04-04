"""Port DisciplinaDescriptorPort — abstracción para consultar el descriptor de una disciplina."""

from __future__ import annotations

from abc import ABC, abstractmethod

from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor


class DisciplinaDescriptorPort(ABC):
    """Puerto para consultar las reglas de una disciplina sin acoplarse a la implementación.

    Permite que los handlers de aplicación obtengan el DisciplinaDescriptor
    (unidad esperada, orden de grilla) sin depender directamente del enum Disciplina
    ni de lógica hardcodeada en la capa de aplicación.
    """

    @abstractmethod
    def describe(self, disciplina: Disciplina) -> DisciplinaDescriptor:
        """Retorna el descriptor canónico para una disciplina.

        Args:
            disciplina: Disciplina a describir.

        Returns:
            DisciplinaDescriptor con unidad_esperada y orden_ascendente correctos.
        """
