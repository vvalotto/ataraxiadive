"""Domain Event IntervaloOTConfigurado — emitido al configurar el intervalo entre OTs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class IntervaloOTConfigurado(DomainEvent):
    """Evento emitido cuando el organizador configura (o reconfigura) el intervalo OT.

    Persiste en el stream `competencia-{competencia_id}`.
    La Competencia mantiene estado Preparacion tras este evento.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina asociada a la competencia.
        intervalo_minutos: Tiempo en minutos entre OTs consecutivos.
        configurado_por: Identificador del organizador o juez que configuró el intervalo.
    """

    competencia_id: str
    disciplina: str
    intervalo_minutos: int
    configurado_por: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "intervalo_minutos": self.intervalo_minutos,
            "configurado_por": self.configurado_por,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "IntervaloOTConfigurado":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="IntervaloOTConfigurado",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            intervalo_minutos=payload["intervalo_minutos"],
            configurado_por=payload["configurado_por"],
        )
