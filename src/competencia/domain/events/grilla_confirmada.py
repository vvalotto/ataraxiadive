"""Domain Event GrillaConfirmada — grilla de salida congelada, INV-C-02."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class GrillaConfirmada(DomainEvent):
    """Evento emitido al confirmar la Grilla de Salida.

    Hito irreversible (v1): después de este evento la grilla no puede
    modificarse. Bloquea GenerarGrilla, AjustarGrilla y ConfigurarIntervaloOT.

    Persiste en el stream `competencia-{competencia_id}`.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina de la competencia.
        confirmada_en: Timestamp de confirmación.
    """

    competencia_id: str
    disciplina: str
    confirmada_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "confirmada_en": self.confirmada_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "GrillaConfirmada":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="GrillaConfirmada",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            confirmada_en=payload["confirmada_en"],
        )
