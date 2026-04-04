"""Domain Event APRegistrado — emitido cuando un atleta declara su AP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class APRegistrado(DomainEvent):
    """Evento emitido al registrar el Announced Performance de un atleta.

    Crea el aggregate Performance con estado AnunciadaAP.

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        competencia_id: Competencia en la que se declara el AP (UUID str).
        participante_id: Participante que declara el AP (UUID str).
        disciplina: Disciplina en la que se compite (valor del enum Disciplina).
        valor_ap: Marca declarada como string decimal (ej: "330.00").
        unidad: Unidad de medida (valor del enum UnidadMedida).
    """

    performance_id: str
    competencia_id: str
    participante_id: str
    disciplina: str
    valor_ap: str
    unidad: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "competencia_id": self.competencia_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "valor_ap": self.valor_ap,
            "unidad": self.unidad,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "APRegistrado":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="APRegistrado",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            competencia_id=payload["competencia_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            valor_ap=payload["valor_ap"],
            unidad=payload["unidad"],
        )
