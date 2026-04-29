from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.ports.inscripcion_repository_port import InscripcionRepositoryPort


@dataclass(frozen=True)
class APFaltanteDetalle:
    inscripcion_id: UUID
    atleta_id: UUID
    atleta_nombre: str
    disciplina: str


class VerificarCompletitudAPHandler:
    def __init__(
        self,
        inscripcion_repo: InscripcionRepositoryPort,
        atleta_repo: AtletaRepositoryPort,
    ) -> None:
        self._inscripcion_repo = inscripcion_repo
        self._atleta_repo = atleta_repo

    async def obtener_faltantes(self, torneo_id: UUID) -> list[APFaltanteDetalle]:
        faltantes: list[APFaltanteDetalle] = []
        for inscripcion in await self._inscripcion_repo.find_active_by_torneo(torneo_id):
            atleta = await self._atleta_repo.find_by_id(inscripcion.atleta_id)
            atleta_nombre = (
                f"{atleta.apellido}, {atleta.nombre}".strip(", ")
                if atleta is not None
                else str(inscripcion.atleta_id)
            )
            for disciplina in sorted(inscripcion.disciplinas, key=lambda item: item.value):
                if inscripcion.obtener_ap(disciplina) is None:
                    faltantes.append(
                        APFaltanteDetalle(
                            inscripcion_id=inscripcion.inscripcion_id,
                            atleta_id=inscripcion.atleta_id,
                            atleta_nombre=atleta_nombre,
                            disciplina=disciplina.value,
                        )
                    )
        return faltantes
