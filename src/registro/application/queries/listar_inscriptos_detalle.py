from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion


@dataclass
class InscriptoDetalleDto:
    inscripcion_id: UUID
    atleta_id: UUID
    nombre: str
    apellido: str
    categoria: str
    club: str
    disciplinas: list[str]
    estado: str


class ListarInscriptosDetalleHandler:
    def __init__(
        self,
        inscripcion_repo: InscripcionRepositoryPort,
        atleta_repo: AtletaRepositoryPort,
    ) -> None:
        self._inscripcion_repo = inscripcion_repo
        self._atleta_repo = atleta_repo

    async def handle(self, torneo_id: UUID) -> list[InscriptoDetalleDto]:
        inscripciones = await self._inscripcion_repo.find_by_torneo(torneo_id)
        activas = [i for i in inscripciones if i.estado == EstadoInscripcion.ACTIVA]

        resultado: list[InscriptoDetalleDto] = []
        for inscripcion in activas:
            atleta = await self._atleta_repo.find_by_id(inscripcion.atleta_id)
            if atleta is None:
                continue
            resultado.append(
                InscriptoDetalleDto(
                    inscripcion_id=inscripcion.inscripcion_id,
                    atleta_id=inscripcion.atleta_id,
                    nombre=atleta.nombre,
                    apellido=atleta.apellido,
                    categoria=atleta.categoria.value,
                    club=atleta.club,
                    disciplinas=[d.value for d in inscripcion.disciplinas],
                    estado=inscripcion.estado.value,
                )
            )
        return resultado
