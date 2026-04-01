"""Comando y handler para asignar disciplinas a un torneo."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.exceptions import TorneoNoEncontrado
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort


@dataclass(frozen=True)
class AsignarDisciplinasCommand:
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]


class AsignarDisciplinasHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: AsignarDisciplinasCommand) -> None:
        torneo = await self._repo.find_by_id(cmd.torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {cmd.torneo_id} no encontrado")
        torneo.asignar_disciplinas(cmd.disciplinas)
        await self._repo.save(torneo)
