"""Domain Event ResultadosCalculados — ranking de la disciplina disponible."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class ResultadosCalculados(DomainEvent):
    """Evento emitido cuando el ranking de la disciplina fue calculado.

    Persiste en el stream `ranking-{competencia_id}-{disciplina}`.
    Habilita la consulta del ranking completo con posiciones, marcas y podio.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina cuyo ranking fue calculado.
        total: Total de performances incluidas en el ranking.
        entries: Tupla de dicts con las entradas del ranking (posicion, atleta_id,
                 rp, unidad, tarjeta, es_dns, en_podio).
        calculado_en: Timestamp de cálculo (ISO 8601).
    """

    competencia_id: str
    disciplina: str
    total: int
    entries: tuple[dict[str, Any], ...]
    calculado_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "total": self.total,
            "entries": list(self.entries),
            "calculado_en": self.calculado_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ResultadosCalculados":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="ResultadosCalculados",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            total=payload["total"],
            entries=tuple(payload["entries"]),
            calculado_en=payload["calculado_en"],
        )
