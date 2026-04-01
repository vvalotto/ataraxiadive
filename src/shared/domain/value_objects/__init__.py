"""Value Objects compartidos entre Bounded Contexts."""

from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from shared.domain.value_objects.unidad_medida import UnidadMedida

__all__ = ["Disciplina", "DisciplinaDescriptor", "UnidadMedida"]
