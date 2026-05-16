from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from registro.domain.aggregates.juez import Juez


class JuezRepositoryPort(ABC):
    @abstractmethod
    async def save(self, juez: Juez) -> None: ...

    @abstractmethod
    async def find_by_id(self, juez_id: UUID) -> Juez | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Juez | None: ...
