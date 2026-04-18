"""Domain Event TarjetaAsignada — emitido cuando el juez asigna la tarjeta al atleta."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from competencia.domain.value_objects.motivo_dq import MotivoDQ
from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class TarjetaAsignada(DomainEvent):
    """Evento emitido cuando el juez asigna la tarjeta a la Performance.

    Transiciona la Performance de ResultadoRegistrado → Ejecutada (estado final).

    Attributes:
        performance_id: Identificador único de la Performance (UUID str).
        participante_id: Participante que ejecutó la performance (UUID str).
        disciplina: Disciplina en la que compitió (valor del enum Disciplina).
        tipo: Tipo de tarjeta — Blanca, Amarilla o Roja.
        motivo_dq_codigo: Motivo formal para tarjeta roja.
        motivo_texto: Motivo libre para amarilla o compatibilidad histórica.
        asignada_por: Identificador del juez que asignó la tarjeta.
        asignada_en: Timestamp del momento de asignación (ISO 8601).
    """

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
        """Serializa el evento a payload JSON-serializable para el Event Store."""
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
    def from_payload(cls, payload: dict[str, Any]) -> "TarjetaAsignada":
        """Reconstruye el evento desde el payload del Event Store."""
        motivo_dq_codigo = payload.get("motivo_dq_codigo")
        motivo_texto = payload.get("motivo_texto")
        legacy_motivo = payload.get("motivo")
        if motivo_dq_codigo is None and legacy_motivo == "black-out":
            motivo_dq_codigo = MotivoDQ.BKO_SUPERFICIE.value
        elif motivo_texto is None and isinstance(legacy_motivo, str):
            motivo_texto = legacy_motivo

        return cls(
            event_type="TarjetaAsignada",
            aggregate_id=payload["performance_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            performance_id=payload["performance_id"],
            participante_id=payload["participante_id"],
            disciplina=payload["disciplina"],
            tipo=payload["tipo"],
            motivo_dq_codigo=motivo_dq_codigo,
            motivo_texto=motivo_texto,
            asignada_por=payload["asignada_por"],
            asignada_en=payload["asignada_en"],
            distancia_blackout=payload.get("distancia_blackout"),
            penalizaciones=tuple(payload.get("penalizaciones", [])),
            rp_medido=payload.get("rp_medido"),
            rp_penalizado=payload.get("rp_penalizado"),
        )
