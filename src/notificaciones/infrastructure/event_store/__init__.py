"""Event store del BC Notificaciones."""

from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)

__all__ = ["SQLiteNotificacionEventStore"]
