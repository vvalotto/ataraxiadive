"""Domain Event GrillaDeSalidaGenerada — snapshot completo de la grilla ordenada."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class GrillaDeSalidaGenerada(DomainEvent):
    """Evento emitido al generar (o regenerar) la Grilla de Salida.

    Persiste en el stream `competencia-{competencia_id}`.
    Contiene un snapshot completo de la grilla ordenada con OTs calculados.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina de la competencia.
        ot_inicio: Timestamp de inicio usado para calcular los OTs.
        performances: Lista ordenada de entradas: [{performance_id, atleta_id,
            posicion, andarivel, ot_programado}].
        generada_en: Timestamp de generación de la grilla.
    """

    competencia_id: str
    disciplina: str
    ot_inicio: str
    performances: tuple[dict[str, Any], ...]
    generada_en: str

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "ot_inicio": self.ot_inicio,
            "performances": list(self.performances),
            "generada_en": self.generada_en,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "GrillaDeSalidaGenerada":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="GrillaDeSalidaGenerada",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            ot_inicio=payload["ot_inicio"],
            performances=tuple(payload["performances"]),
            generada_en=payload["generada_en"],
        )
