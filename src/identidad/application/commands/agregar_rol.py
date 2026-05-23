from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from identidad.domain.exceptions import UsuarioNoEncontrado
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol


@dataclass(frozen=True)
class AgregarRolCommand:
    usuario_id: UUID
    rol: Rol


class AgregarRolHandler:
    def __init__(self, repo: UsuarioRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: AgregarRolCommand) -> None:
        usuario = await self._repo.find_by_id(cmd.usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(str(cmd.usuario_id))
        usuario.agregar_rol(cmd.rol)
        await self._repo.save(usuario)
