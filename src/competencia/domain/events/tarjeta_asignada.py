"""Domain Event TarjetaAsignada — emitido cuando el juez asigna la tarjeta al atleta."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class TarjetaAsignada(DomainEvent):
    """Evento emitido cuando el juez asigna la tarjeta a la Performance.

    Transiciona la Performance de ResultadoRegistrado → Ejecutada (estado final).

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        participante_id: Participante que ejecutó la performance (UUID str).
        disciplina: Disciplina en la que compitió (valor del enum Disciplina).
        tipo: Tipo de tarjeta — Blanca, Amarilla o Roja.
        motivo: Motivo de la tarjeta (obligatorio si Amarilla o Roja — INV-P-11).
        asignada_por: Identificador del juez que asignó la tarjeta.
        asignada_en: Timestamp del momento de asignación (ISO 8601).
    """

    performance_id: str
    participante_id: str
    disciplina: str
    tipo: str
    motivo: str | None
    asignada_por: str
    asignada_en: str
    distancia_blackout: str | None = None

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "tipo": self.tipo,
            "motivo": self.motivo,
            "asignada_por": self.asignada_por,
            "asignada_en": self.asignada_en,
            "distancia_blackout": self.distancia_blackout,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "TarjetaAsignada":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="TarjetaAsignada",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            tipo=payload["tipo"],
            motivo=payload.get("motivo"),
            asignada_por=payload["asignada_por"],
            asignada_en=payload["asignada_en"],
            distancia_blackout=payload.get("distancia_blackout"),
        )
