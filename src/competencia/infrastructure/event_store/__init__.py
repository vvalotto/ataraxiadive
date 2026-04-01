"""Implementaciones del Event Store para BC Competencia."""

from competencia.infrastructure.event_store.sqlite_event_store import (
    ConcurrencyError,
    SQLiteEventStore,
)

__all__ = ["SQLiteEventStore", "ConcurrencyError"]
