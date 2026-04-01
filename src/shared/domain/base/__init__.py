"""Clases base del dominio compartidas por todos los Bounded Contexts."""

from shared.domain.base.aggregate_root import AggregateRoot
from shared.domain.base.domain_event import DomainEvent

__all__ = ["AggregateRoot", "DomainEvent"]
