"""Domain Event DNSRegistrado — emitido cuando el atleta no se presenta al OT."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class DNSRegistrado(DomainEvent):
    """Evento emitido cuando el juez registra que el atleta no se presentó al OT.

    Transiciona la Performance de Llamada → DNS (estado final).

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        participante_id: Participante que no se presentó (UUID str).
        disciplina: Disciplina en la que debía competir (valor del enum Disciplina).
        ot_programado: Momento programado para el Official Top (ISO 8601).
        registrado_por: Identificador del juez que registra el DNS.
        registrado_en: Timestamp del momento del registro (ISO 8601).
    """

    performance_id: str
    participante_id: str
    disciplina: str
    ot_programado: str
    registrado_por: str
    registrado_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "ot_programado": self.ot_programado,
            "registrado_por": self.registrado_por,
            "registrado_en": self.registrado_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "DNSRegistrado":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="DNSRegistrado",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            ot_programado=payload["ot_programado"],
            registrado_por=payload["registrado_por"],
            registrado_en=payload["registrado_en"],
        )
