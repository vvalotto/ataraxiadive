from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.value_objects.rol import Rol


class UsuarioRepositoryPort(ABC):
    @abstractmethod
    async def save(self, usuario: Usuario) -> None: ...

    @abstractmethod
    async def find_by_id(self, usuario_id: UUID) -> Usuario | None: ...

    @abstractmethod
    async def find_by_email(self, email: str) -> Usuario | None: ...

    @abstractmethod
    async def list_by_rol(self, rol: Rol) -> list[Usuario]: ...

    @abstractmethod
    async def list_all(self) -> list[Usuario]: ...
