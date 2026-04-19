"""Domain Event ResultadoCorregidoTrasDNS — corrige un DNS registrado por error."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class ResultadoCorregidoTrasDNS(DomainEvent):
    """Evento emitido cuando un juez corrige un DNS y registra el RP real.

    Transiciona la Performance de DNS a ResultadoRegistrado.
    El motivo de correccion es obligatorio para trazabilidad de auditoria.
    """

    performance_id: str
    participante_id: str
    disciplina: str
    valor_rp: str
    unidad: str
    registrado_por: str
    motivo_correccion: str
    corregido_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "valor_rp": self.valor_rp,
            "unidad": self.unidad,
            "registrado_por": self.registrado_por,
            "motivo_correccion": self.motivo_correccion,
            "corregido_en": self.corregido_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ResultadoCorregidoTrasDNS":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="ResultadoCorregidoTrasDNS",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            valor_rp=payload["valor_rp"],
            unidad=payload["unidad"],
            registrado_por=payload["registrado_por"],
            motivo_correccion=payload["motivo_correccion"],
            corregido_en=payload["corregido_en"],
        )
