from __future__ import annotations

from uuid import UUID

from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaNoEncontrado
from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort


class ObtenerAtletaHandler:
    def __init__(self, repo: AtletaRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, atleta_id: UUID) -> Atleta:
        atleta = await self._repo.find_by_id(atleta_id)
        if atleta is None:
            raise AtletaNoEncontrado(f"Atleta {atleta_id} no encontrado")
        return atleta
