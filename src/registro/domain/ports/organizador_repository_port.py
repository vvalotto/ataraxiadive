from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from registro.domain.aggregates.organizador import Organizador


class OrganizadorRepositoryPort(ABC):
    @abstractmethod
    async def save(self, organizador: Organizador) -> None: ...

    @abstractmethod
    async def find_by_id(self, organizador_id: UUID) -> Organizador | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Organizador | None: ...
