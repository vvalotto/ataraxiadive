"""Domain Event RankingOverallCalculado — ranking general del torneo disponible."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class RankingOverallCalculado(DomainEvent):
    """Evento emitido cuando el overall de un torneo fue calculado."""

    torneo_id: str
    disciplinas: tuple[str, ...]
    total: int
    entries: tuple[dict[str, Any], ...]
    calculado_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento para el Event Store."""
        return {
            "torneo_id": self.torneo_id,
            "disciplinas": list(self.disciplinas),
            "total": self.total,
            "entries": list(self.entries),
            "calculado_en": self.calculado_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RankingOverallCalculado":
        """Reconstruye el evento desde el payload persistido."""
        return cls(
            event_type="RankingOverallCalculado",
            aggregate_id=payload["torneo_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            torneo_id=payload["torneo_id"],
            disciplinas=tuple(payload["disciplinas"]),
            total=payload["total"],
            entries=tuple(payload["entries"]),
            calculado_en=payload["calculado_en"],
        )
