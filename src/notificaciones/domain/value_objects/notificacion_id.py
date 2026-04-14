from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class NotificacionId:
    value: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if isinstance(self.value, str):
            object.__setattr__(self, "value", UUID(self.value))

    def __str__(self) -> str:
        return str(self.value)
