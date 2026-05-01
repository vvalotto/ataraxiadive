"""Domain Event JuezPerformanceAsignado — juez asignado a una fila de grilla."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class JuezPerformanceAsignado(DomainEvent):
    """Evento emitido al asignar o reasignar juez a una performance de la grilla."""

    competencia_id: str
    disciplina: str
    performance_id: str
    juez_id: str
    asignado_en: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "performance_id": self.performance_id,
            "juez_id": self.juez_id,
            "asignado_en": self.asignado_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "JuezPerformanceAsignado":
        return cls(
            event_type="JuezPerformanceAsignado",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            performance_id=payload["performance_id"],
            juez_id=payload["juez_id"],
            asignado_en=payload["asignado_en"],
        )
