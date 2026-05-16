from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from registro.domain.aggregates.organizador import Organizador
from registro.domain.exceptions import OrganizadorYaRegistrado
from registro.domain.ports.organizador_repository_port import OrganizadorRepositoryPort


@dataclass(frozen=True)
class RegistrarOrganizadorCommand:
    email: str
    nombre_organizacion: str | None = field(default=None)


class RegistrarOrganizadorHandler:
    def __init__(self, repo: OrganizadorRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: RegistrarOrganizadorCommand) -> UUID:
        existing = await self._repo.find_by_email(cmd.email)
        if existing is not None:
            raise OrganizadorYaRegistrado(
                f"Ya existe un perfil de organizador con email {cmd.email}"
            )

        organizador = Organizador(
            organizador_id=uuid4(),
            email=cmd.email,
            nombre_organizacion=cmd.nombre_organizacion,
        )
        await self._repo.save(organizador)
        return organizador.organizador_id
