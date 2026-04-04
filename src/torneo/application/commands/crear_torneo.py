from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede


@dataclass(frozen=True)
class CrearTorneoCommand:
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede_nombre: str
    sede_ciudad: str
    sede_pais: str
    entidad_nombre: str
    entidad_tipo: str


class CrearTorneoHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: CrearTorneoCommand) -> UUID:
        torneo = Torneo(
            nombre=cmd.nombre,
            descripcion=cmd.descripcion,
            fecha_inicio=cmd.fecha_inicio,
            fecha_fin=cmd.fecha_fin,
            sede=Sede(nombre=cmd.sede_nombre, ciudad=cmd.sede_ciudad, pais=cmd.sede_pais),
            entidad_organizadora=EntidadOrganizadora(
                nombre=cmd.entidad_nombre, tipo=cmd.entidad_tipo
            ),
        )
        await self._repo.save(torneo)
        return torneo.torneo_id
