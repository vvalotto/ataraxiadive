"""Comando y handler para asignar juez a una disciplina del torneo."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.exceptions import TorneoNoEncontrado
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort


@dataclass(frozen=True)
class AsignarJuezCommand:
    torneo_id: UUID
    disciplina: Disciplina
    juez_id: UUID


class AsignarJuezHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: AsignarJuezCommand) -> None:
        torneo = await self._repo.find_by_id(cmd.torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {cmd.torneo_id} no encontrado")
        torneo.asignar_juez(cmd.disciplina, cmd.juez_id)
        await self._repo.save(torneo)
