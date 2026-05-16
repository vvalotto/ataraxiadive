from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from identidad.domain.value_objects.rol import Rol


class PerfilRegistroPort(ABC):
    @abstractmethod
    async def crear_perfiles(
        self,
        usuario_id: UUID,
        nombre: str,
        apellido: str,
        email: str,
        roles: list[Rol],
        numero_licencia: str | None = None,
        federacion: str | None = None,
        nombre_organizacion: str | None = None,
    ) -> None: ...
