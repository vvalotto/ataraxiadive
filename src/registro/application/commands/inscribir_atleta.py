from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import (
    AtletaYaInscripto,
    DisciplinaNoDisponible,
    TorneoNoDisponible,
)
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from registro.domain.ports.torneo_consulta_port import TorneoConsultaPort
from shared.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class InscribirAtletaCommand:
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]


class InscribirAtletaHandler:
    def __init__(
        self,
        inscripcion_repo: InscripcionRepositoryPort,
        torneo_consulta: TorneoConsultaPort,
    ) -> None:
        self._inscripcion_repo = inscripcion_repo
        self._torneo_consulta = torneo_consulta

    async def handle(self, cmd: InscribirAtletaCommand) -> UUID:
        if not cmd.disciplinas:
            raise ValueError("Debe seleccionar al menos una disciplina")  # INV-I-05

        if not await self._torneo_consulta.esta_abierto_para_inscripcion(cmd.torneo_id):
            raise TorneoNoDisponible(
                f"El torneo {cmd.torneo_id} no está abierto para inscripción"
            )  # INV-I-02

        disciplinas_torneo = await self._torneo_consulta.obtener_disciplinas(cmd.torneo_id)
        no_disponibles = cmd.disciplinas - disciplinas_torneo
        if no_disponibles:
            raise DisciplinaNoDisponible(
                f"Disciplinas no disponibles en el torneo: {no_disponibles}"
            )  # INV-I-01

        existente = await self._inscripcion_repo.find_by_atleta_y_torneo(
            cmd.atleta_id, cmd.torneo_id
        )
        if existente is not None:
            raise AtletaYaInscripto(
                f"El atleta {cmd.atleta_id} ya está inscripto en el torneo {cmd.torneo_id}"
            )  # INV-I-04

        inscripcion = Inscripcion(
            atleta_id=cmd.atleta_id,
            torneo_id=cmd.torneo_id,
            disciplinas=cmd.disciplinas,
        )
        await self._inscripcion_repo.save(inscripcion)
        return inscripcion.inscripcion_id
