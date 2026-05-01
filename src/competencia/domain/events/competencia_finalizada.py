"""Domain Event CompetenciaFinalizada — todas las performances completadas (P-08)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

from shared.domain.base.domain_event import DomainEvent


@dataclass(frozen=True)
class CompetenciaFinalizada(DomainEvent):
    """Evento emitido cuando todas las performances de la disciplina finalizaron.

    Disparado automáticamente por política P-08 desde AsignarTarjetaHandler
    o RegistrarDNSHandler cuando ejecutadas + dns_count == total_performances.

    Habilita BC Resultados para calcular el ranking (US-2.4.2).
    Transiciona el estado de EnEjecucion → Finalizada.

    Persiste en el stream `competencia-{competencia_id}`.

    Attributes:
        competencia_id: Identificador de la competencia (UUID str).
        disciplina: Disciplina que finalizó.
        total_performances: Total de performances en la disciplina.
        ejecutadas: Cantidad en estado Ejecutada (tarjeta asignada).
        dns_count: Cantidad en estado DNS.
        finalizada_en: Timestamp de finalización.
        origen: Origen auditable del cierre: automatico o manual.
        finalizada_por: Identificador opcional del usuario que solicito el cierre manual.
    """

    competencia_id: str
    disciplina: str
    total_performances: int
    ejecutadas: int
    dns_count: int
    finalizada_en: str
    hash_sha256: str | None = None
    origen: str = "automatico"
    finalizada_por: str | None = None

    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a payload JSON-serializable para el Event Store."""
        return {
            "competencia_id": self.competencia_id,
            "disciplina": self.disciplina,
            "total_performances": self.total_performances,
            "ejecutadas": self.ejecutadas,
            "dns_count": self.dns_count,
            "finalizada_en": self.finalizada_en,
            "hash_sha256": self.hash_sha256,
            "origen": self.origen,
            "finalizada_por": self.finalizada_por,
            "occurred_at": self.occurred_at.isoformat(),
        }

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> "CompetenciaFinalizada":
        """Reconstruye el evento desde el payload del Event Store."""
        return cls(
            event_type="CompetenciaFinalizada",
            aggregate_id=payload["competencia_id"],
            occurred_at=datetime.fromisoformat(payload["occurred_at"]),
            competencia_id=payload["competencia_id"],
            disciplina=payload["disciplina"],
            total_performances=payload["total_performances"],
            ejecutadas=payload["ejecutadas"],
            dns_count=payload["dns_count"],
            finalizada_en=payload["finalizada_en"],
            hash_sha256=payload.get("hash_sha256"),
            origen=payload.get("origen", "automatico"),
            finalizada_por=payload.get("finalizada_por"),
        )
