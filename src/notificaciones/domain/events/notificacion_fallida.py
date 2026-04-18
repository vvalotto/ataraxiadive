from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class NotificacionFallida(DomainEvent):
    notificacion_id: str
    evento_fuente_id: str
    motivo: str
    fallida_en: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "notificacion_id": self.notificacion_id,
            "evento_fuente_id": self.evento_fuente_id,
            "motivo": self.motivo,
            "fallida_en": self.fallida_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "NotificacionFallida":
        return cls(
            event_type="NotificacionFallida",
            aggregate_id=payload["notificacion_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            notificacion_id=payload["notificacion_id"],
            evento_fuente_id=payload["evento_fuente_id"],
            motivo=payload["motivo"],
            fallida_en=payload["fallida_en"],
        )
