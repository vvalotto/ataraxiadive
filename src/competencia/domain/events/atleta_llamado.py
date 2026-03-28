"""Domain Event AtletaLlamado — emitido cuando el sistema llama a un atleta."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class AtletaLlamado(DomainEvent):
    """Evento emitido al llamar a un atleta según el orden de grilla.

    Transiciona la Performance de AnunciadaAP → Llamada.

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        participante_id: Participante convocado (UUID str).
        disciplina: Disciplina en la que compite (valor del enum Disciplina).
        posicion_grilla: Número de orden en la grilla de salida.
        ot_programado: Official Top programado (ISO 8601).
        llamado_en: Timestamp del momento en que fue llamado (ISO 8601).
    """

    performance_id: str
    participante_id: str
    disciplina: str
    posicion_grilla: int
    ot_programado: str
    llamado_en: str
    andarivel: int = 1

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "performance_id": self.performance_id,
            "participante_id": self.participante_id,
            "disciplina": self.disciplina,
            "posicion_grilla": self.posicion_grilla,
            "ot_programado": self.ot_programado,
            "llamado_en": self.llamado_en,
            "andarivel": self.andarivel,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "AtletaLlamado":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="AtletaLlamado",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            posicion_grilla=payload["posicion_grilla"],
            ot_programado=payload["ot_programado"],
            llamado_en=payload["llamado_en"],
            andarivel=payload.get("andarivel", 1),
        )
