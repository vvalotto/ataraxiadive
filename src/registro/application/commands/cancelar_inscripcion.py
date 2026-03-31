from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from registro.domain.exceptions import InscripcionNoEncontrada
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from registro.domain.ports.torneo_consulta_port import TorneoConsultaPort


@dataclass(frozen=True)
class CancelarInscripcionCommand:
    inscripcion_id: UUID
    fecha_actual: date


class CancelarInscripcionHandler:
    def __init__(
        self,
        inscripcion_repo: InscripcionRepositoryPort,
        torneo_consulta: TorneoConsultaPort,
    ) -> None:
        self._inscripcion_repo = inscripcion_repo
        self._torneo_consulta = torneo_consulta

    async def handle(self, cmd: CancelarInscripcionCommand) -> None:
        inscripcion = await self._inscripcion_repo.find_by_id(cmd.inscripcion_id)
        if inscripcion is None:
            raise InscripcionNoEncontrada(f"Inscripción {cmd.inscripcion_id} no encontrada")

        fecha_inicio = await self._torneo_consulta.obtener_fecha_inicio(inscripcion.torneo_id)
        inscripcion.cancelar(cmd.fecha_actual, fecha_inicio)
        await self._inscripcion_repo.save(inscripcion)
