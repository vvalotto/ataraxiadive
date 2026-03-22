"""Domain Event ResultadoRegistrado — emitido cuando el juez registra el RP del atleta."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class ResultadoRegistrado(DomainEvent):
    """Evento emitido cuando el juez registra el resultado efectivo del atleta.

    Transiciona la Performance de Llamada → ResultadoRegistrado.

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        participante_id: Participante que ejecutó la performance (UUID str).
        disciplina: Disciplina en la que compitió (valor del enum Disciplina).
        valor_rp: Realized Performance — marca efectivamente lograda (Decimal como str).
        unidad: Unidad de medida del RP (valor del enum UnidadMedida).
        registrado_por: Identificador del juez que registró el resultado.
        registrado_en: Timestamp del momento de registro (ISO 8601).
    """

    performance_id: str
    participante_id: str
    disciplina: str
    valor_rp: str
    unidad: str
    registrado_por: str
    registrado_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "valor_rp": self.valor_rp,
            "unidad": self.unidad,
            "registrado_por": self.registrado_por,
            "registrado_en": self.registrado_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "ResultadoRegistrado":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="ResultadoRegistrado",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            valor_rp=payload["valor_rp"],
            unidad=payload["unidad"],
            registrado_por=payload["registrado_por"],
            registrado_en=payload["registrado_en"],
        )
