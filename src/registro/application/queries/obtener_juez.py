from __future__ import annotations

from registro.domain.aggregates.juez import Juez
from registro.domain.exceptions import JuezNoEncontrado
from registro.domain.ports.juez_repository_port import JuezRepositoryPort


class ObtenerJuezHandler:
    def __init__(self, repo: JuezRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, email: str) -> Juez:
        juez = await self._repo.find_by_email(email)
        if juez is None:
            raise JuezNoEncontrado(f"No existe perfil de juez con email {email}")
        return juez
