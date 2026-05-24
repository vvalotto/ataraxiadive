from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from registro.domain.exceptions import InscripcionNoEncontrada
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from registro.domain.value_objects.estado_aceptacion import EstadoAceptacion


@dataclass(frozen=True)
class CambiarAceptacionInscripcionCommand:
    inscripcion_id: UUID
    nuevo_estado: EstadoAceptacion


class CambiarAceptacionInscripcionHandler:
    def __init__(self, repo: InscripcionRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: CambiarAceptacionInscripcionCommand) -> None:
        inscripcion = await self._repo.find_by_id(cmd.inscripcion_id)
        if inscripcion is None:
            raise InscripcionNoEncontrada(f"Inscripción {cmd.inscripcion_id} no encontrada")
        inscripcion.cambiar_aceptacion(cmd.nuevo_estado)
        await self._repo.save(inscripcion)
