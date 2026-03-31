from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from registro.domain.aggregates.atleta import Atleta


class AtletaRepositoryPort(ABC):
    @abstractmethod
    async def save(self, atleta: Atleta) -> None: ...

    @abstractmethod
    async def find_by_id(self, atleta_id: UUID) -> Atleta | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Atleta | None: ...
