"""Adapter DisciplinaDescriptorAdapter — implementación local del port para BC Resultados."""
from __future__ import annotations

from competencia.domain.ports.disciplina_descriptor_port import DisciplinaDescriptorPort
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor


class DisciplinaDescriptorAdapter(DisciplinaDescriptorPort):
    """Deriva el descriptor directamente del enum Disciplina, sin acceso a I/O."""

    def describe(self, disciplina: Disciplina) -> DisciplinaDescriptor:
        """Retorna el descriptor canónico para una disciplina usando DisciplinaDescriptor.para()."""
        return DisciplinaDescriptor.para(disciplina)
