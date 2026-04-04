from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import TorneoNoEncontrado
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort


@dataclass(frozen=True)
class ObtenerTorneoQuery:
    torneo_id: UUID


@dataclass(frozen=True)
class ListarTorneosQuery:
    pass


class ObtenerTorneoHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, query: ObtenerTorneoQuery) -> Torneo:
        torneo = await self._repo.find_by_id(query.torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {query.torneo_id} no encontrado")
        return torneo


class ListarTorneosHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, query: ListarTorneosQuery) -> list[Torneo]:
        return await self._repo.find_all()
