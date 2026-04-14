from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class NotificacionSolicitada(DomainEvent):
    notificacion_id: str
    evento_fuente_id: str
    destinatario_email: str
    destinatario_nombre: str | None
    asunto: str
    cuerpo_texto: str
    cuerpo_html: str | None
    canal: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "notificacion_id": self.notificacion_id,
            "evento_fuente_id": self.evento_fuente_id,
            "destinatario_email": self.destinatario_email,
            "destinatario_nombre": self.destinatario_nombre,
            "asunto": self.asunto,
            "cuerpo_texto": self.cuerpo_texto,
            "cuerpo_html": self.cuerpo_html,
            "canal": self.canal,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "NotificacionSolicitada":
        return cls(
            event_type="NotificacionSolicitada",
            aggregate_id=payload["notificacion_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            notificacion_id=payload["notificacion_id"],
            evento_fuente_id=payload["evento_fuente_id"],
            destinatario_email=payload["destinatario_email"],
            destinatario_nombre=payload.get("destinatario_nombre"),
            asunto=payload["asunto"],
            cuerpo_texto=payload["cuerpo_texto"],
            cuerpo_html=payload.get("cuerpo_html"),
            canal=payload["canal"],
        )
