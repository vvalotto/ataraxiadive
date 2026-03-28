"""Re-export de SQLiteEventStore desde shared.infrastructure (fuente canónica)."""
from shared.infrastructure.event_store.sqlite_event_store import (
    ConcurrencyError,
    SQLiteEventStore,
)

__all__ = ["ConcurrencyError", "SQLiteEventStore"]
