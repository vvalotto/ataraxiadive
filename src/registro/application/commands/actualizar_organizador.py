from __future__ import annotations

from dataclasses import dataclass, field

from registro.domain.aggregates.organizador import Organizador
from registro.domain.exceptions import OrganizadorNoEncontrado
from registro.domain.ports.organizador_repository_port import OrganizadorRepositoryPort

_UNSET = object()


@dataclass(frozen=True)
class ActualizarOrganizadorCommand:
    email: str
    nombre_organizacion: str | None = field(default=None)


class ActualizarOrganizadorHandler:
    def __init__(self, repo: OrganizadorRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: ActualizarOrganizadorCommand) -> Organizador:
        organizador = await self._repo.find_by_email(cmd.email)
        if organizador is None:
            raise OrganizadorNoEncontrado(f"No existe perfil de organizador con email {cmd.email}")

        organizador.actualizar(nombre_organizacion=cmd.nombre_organizacion)
        await self._repo.save(organizador)
        return organizador
