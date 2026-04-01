"""Re-export de EventStorePort desde shared.domain (fuente canónica)."""

from shared.domain.ports.event_store_port import EventStorePort

__all__ = ["EventStorePort"]
