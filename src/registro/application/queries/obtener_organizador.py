from __future__ import annotations

from registro.domain.aggregates.organizador import Organizador
from registro.domain.exceptions import OrganizadorNoEncontrado
from registro.domain.ports.organizador_repository_port import OrganizadorRepositoryPort


class ObtenerOrganizadorHandler:
    def __init__(self, repo: OrganizadorRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, email: str) -> Organizador:
        organizador = await self._repo.find_by_email(email)
        if organizador is None:
            raise OrganizadorNoEncontrado(f"No existe perfil de organizador con email {email}")
        return organizador
