"""Value Object DisciplinaTorneo — disciplina del torneo con juez opcional."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class DisciplinaTorneo:
    """Disciplina habilitada en un torneo, con juez opcionalmente asignado."""

    disciplina: Disciplina
    juez_id: UUID | None = None

    def con_juez(self, juez_id: UUID) -> DisciplinaTorneo:
        """Retorna una nueva instancia con el juez asignado."""
        return DisciplinaTorneo(disciplina=self.disciplina, juez_id=juez_id)

    def to_dict(self) -> dict[str, str | None]:
        return {
            "disciplina": self.disciplina.value,
            "juez_id": str(self.juez_id) if self.juez_id else None,
        }

    @classmethod
    def from_dict(cls, data: dict[str, str | None]) -> DisciplinaTorneo:
        juez_id = UUID(data["juez_id"]) if data.get("juez_id") else None
        return cls(disciplina=Disciplina(data["disciplina"]), juez_id=juez_id)
