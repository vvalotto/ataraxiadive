"""Domain Event ResultadoCorregido — emitido cuando el juez corrige el RP del atleta."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class ResultadoCorregido(DomainEvent):
    """Evento emitido cuando el juez corrige el resultado efectivo del atleta.

    La Performance permanece en estado Ejecutada.
    El evento preserva el valor anterior para trazabilidad completa.

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        participante_id: Participante cuya performance fue corregida (UUID str).
        disciplina: Disciplina en la que compitió (valor del enum Disciplina).
        valor_rp_anterior: RP previo a la corrección (Decimal como str).
        valor_rp_nuevo: RP corregido (Decimal como str).
        unidad: Unidad de medida del RP (valor del enum UnidadMedida).
        motivo: Razón de la corrección — obligatorio sin excepción (INV-P-12).
        registrado_por: Identificador del juez que realiza la corrección.
        corregido_en: Timestamp del momento de corrección (ISO 8601).
    """

    performance_id: str
    participante_id: str
    disciplina: str
    valor_rp_anterior: str
    valor_rp_nuevo: str
    unidad: str
    motivo: str
    registrado_por: str
    corregido_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "valor_rp_anterior": self.valor_rp_anterior,
            "valor_rp_nuevo": self.valor_rp_nuevo,
            "unidad": self.unidad,
            "motivo": self.motivo,
            "registrado_por": self.registrado_por,
            "corregido_en": self.corregido_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ResultadoCorregido":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="ResultadoCorregido",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            valor_rp_anterior=payload["valor_rp_anterior"],
            valor_rp_nuevo=payload["valor_rp_nuevo"],
            unidad=payload["unidad"],
            motivo=payload["motivo"],
            registrado_por=payload["registrado_por"],
            corregido_en=payload["corregido_en"],
        )
