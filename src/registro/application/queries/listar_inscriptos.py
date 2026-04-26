from __future__ import annotations

from uuid import UUID

from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort


class ListarInscriptosHandler:
    def __init__(self, inscripcion_repo: InscripcionRepositoryPort) -> None:
        self._inscripcion_repo = inscripcion_repo

    async def handle(self, torneo_id: UUID) -> list[Inscripcion]:
        return await self._inscripcion_repo.find_active_by_torneo(torneo_id)
