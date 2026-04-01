"""Clase base para todos los Aggregate Roots del sistema."""

from __future__ import annotations

from shared.domain.base.domain_event import DomainEvent


class AggregateRoot:
    """Clase base para todos los Aggregates Roots.

    Gestiona la lista de eventos de dominio pendientes de persistir.
    La capa de aplicación (CommandHandler) extrae los eventos con
    `pull_events()` y los persiste en el Event Store.
    """

    def __init__(self) -> None:
        self._pending_events: list[DomainEvent] = []

    def _record(self, event: DomainEvent) -> None:
        """Registra un evento pendiente de persistir.

        Args:
            event: Evento de dominio emitido por el aggregate.
        """
        self._pending_events.append(event)

    def pull_events(self) -> list[DomainEvent]:
        """Extrae y limpia los eventos pendientes.

        Llamado por el CommandHandler después de ejecutar el método
        de dominio, antes de persistir en el Event Store.

        Returns:
            Lista de eventos emitidos en esta operación.
        """
        events = list(self._pending_events)
        self._pending_events.clear()
        return events
