from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class NotificacionEnviada(DomainEvent):
    notificacion_id: str
    evento_fuente_id: str
    proveedor_id: str | None
    enviada_en: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "notificacion_id": self.notificacion_id,
            "evento_fuente_id": self.evento_fuente_id,
            "proveedor_id": self.proveedor_id,
            "enviada_en": self.enviada_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "NotificacionEnviada":
        return cls(
            event_type="NotificacionEnviada",
            aggregate_id=payload["notificacion_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            notificacion_id=payload["notificacion_id"],
            evento_fuente_id=payload["evento_fuente_id"],
            proveedor_id=payload.get("proveedor_id"),
            enviada_en=payload["enviada_en"],
        )
