"""Domain Event GrillaDeSalidaAjustada — cambios manuales aplicados sobre la grilla."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class GrillaDeSalidaAjustada(DomainEvent):
    """Evento emitido al ajustar manualmente la Grilla de Salida.

    Persiste en el stream `competencia-{competencia_id}`.
    Contiene la lista de cambios aplicados: campo modificado, valor anterior y nuevo.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina de la competencia.
        cambios: Lista de cambios aplicados: [{performance_id, campo,
            valor_anterior, valor_nuevo}].
        ajustada_en: Timestamp del ajuste.
    """

    competencia_id: str
    disciplina: str
    cambios: tuple[dict[str, Any], ...]
    ajustada_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "cambios": list(self.cambios),
            "ajustada_en": self.ajustada_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "GrillaDeSalidaAjustada":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="GrillaDeSalidaAjustada",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            cambios=tuple(payload["cambios"]),
            ajustada_en=payload["ajustada_en"],
        )
