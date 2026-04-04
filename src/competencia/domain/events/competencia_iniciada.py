"""Domain Event CompetenciaIniciada — disciplina en marcha, performances habilitadas."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class CompetenciaIniciada(DomainEvent):
    """Evento emitido al iniciar la Competencia.

    Habilita LlamarAtleta para las performances (política P-06).
    Transiciona el estado de Confirmada → EnEjecucion.

    Persiste en el stream `competencia-{competencia_id}`.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina de la competencia.
        juez_id: Identificador del juez que inició la competencia.
        iniciada_en: Timestamp de inicio.
    """

    competencia_id: str
    disciplina: str
    juez_id: str
    iniciada_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "juez_id": self.juez_id,
            "iniciada_en": self.iniciada_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CompetenciaIniciada":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="CompetenciaIniciada",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            juez_id=payload["juez_id"],
            iniciada_en=payload["iniciada_en"],
        )
