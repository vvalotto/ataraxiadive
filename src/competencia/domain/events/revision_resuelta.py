"""Domain Event RevisionResuelta — cierre definitivo de una tarjeta amarilla."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class RevisionResuelta(DomainEvent):
    """Evento emitido cuando una performance en revision recibe su tarjeta definitiva."""

    performance_id: str
    participante_id: str
    disciplina: str
    tipo: str
    motivo_dq_codigo: str | None
    motivo_texto: str | None
    asignada_por: str
    asignada_en: str
    distancia_blackout: str | None = None
    penalizaciones: tuple[dict[str, str], ...] = ()
    rp_medido: str | None = None
    rp_penalizado: str | None = None

    def to_payload(self) -> dict[str, Any]:
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "tipo": self.tipo,
            "motivo_dq_codigo": self.motivo_dq_codigo,
            "motivo_texto": self.motivo_texto,
            "asignada_por": self.asignada_por,
            "asignada_en": self.asignada_en,
            "distancia_blackout": self.distancia_blackout,
            "penalizaciones": list(self.penalizaciones),
            "rp_medido": self.rp_medido,
            "rp_penalizado": self.rp_penalizado,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "RevisionResuelta":
        return cls(
            event_type="RevisionResuelta",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            tipo=payload["tipo"],
            motivo_dq_codigo=payload.get("motivo_dq_codigo"),
            motivo_texto=payload.get("motivo_texto"),
            asignada_por=payload["asignada_por"],
            asignada_en=payload["asignada_en"],
            distancia_blackout=payload.get("distancia_blackout"),
            penalizaciones=tuple(payload.get("penalizaciones", [])),
            rp_medido=payload.get("rp_medido"),
            rp_penalizado=payload.get("rp_penalizado"),
        )
