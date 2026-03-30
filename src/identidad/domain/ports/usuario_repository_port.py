from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from identidad.domain.aggregates.usuario import Usuario


class UsuarioRepositoryPort(ABC):
    @abstractmethod
    async def save(self, usuario: Usuario) -> None: ...

    @abstractmethod
    async def find_by_id(self, usuario_id: UUID) -> Usuario | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Usuario | None: ...
