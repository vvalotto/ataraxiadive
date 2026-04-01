"""Query handler para obtener disciplinas asignadas a un juez en un torneo."""

from __future__ import annotations

from uuid import UUID

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.exceptions import TorneoNoEncontrado
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort


class ObtenerDisciplinasDeJuezHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, torneo_id: UUID, juez_id: UUID) -> list[Disciplina]:
        torneo = await self._repo.find_by_id(torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {torneo_id} no encontrado")
        return torneo.obtener_disciplinas_de_juez(juez_id)
