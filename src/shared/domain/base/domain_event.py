"""Clase base para todos los Domain Events del sistema."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class DomainEvent(ABC):
    """Clase base inmutable para todos los eventos de dominio.

    Todo evento de dominio es inmutable una vez creado. Describe algo
    que ocurrió en el dominio — no algo que podría ocurrir.

    Attributes:
        event_type: Nombre del tipo de evento (ej: "APRegistrado").
        aggregate_id: Identificador del aggregate que emitió el evento.
        occurred_at: Momento en que ocurrió el evento (UTC).
    """

    event_type: str
    aggregate_id: str
    occurred_at: datetime

    @abstractmethod
    def to_payload(self) -> dict[str, Any]:
        """Serializa el evento a un dict JSON-serializable para el Event Store.

        Returns:
            Dict con los datos del evento, sin incluir event_type ni occurred_at
            (el EventStore los gestiona por separado).
        """

    @classmethod
    def now(cls) -> datetime:
        """Retorna el momento actual en UTC."""
        return datetime.now(timezone.utc)
