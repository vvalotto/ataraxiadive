from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from registro.domain.exceptions import InscripcionNoEncontrada
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from shared.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class DeclararAPInscripcionCommand:
    inscripcion_id: UUID
    disciplina: Disciplina
    valor_ap: Decimal


class DeclararAPInscripcionHandler:
    def __init__(self, repo: InscripcionRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: DeclararAPInscripcionCommand) -> None:
        inscripcion = await self._repo.find_by_id(cmd.inscripcion_id)
        if inscripcion is None:
            raise InscripcionNoEncontrada(f"Inscripción {cmd.inscripcion_id} no encontrada")
        inscripcion.declarar_ap(cmd.disciplina, cmd.valor_ap)
        await self._repo.save(inscripcion)
