from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from torneo.domain.exceptions import EdicionNoPermitida, TorneoNoEncontrado
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort
from torneo.domain.value_objects.grupo_etario import GrupoEtario
from torneo.domain.value_objects.sede import Sede


@dataclass(frozen=True)
class ActualizarTorneoCommand:
    torneo_id: UUID
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede_nombre: str
    sede_ciudad: str
    sede_pais: str
    grupos_etarios: frozenset[GrupoEtario]


class ActualizarTorneoHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: ActualizarTorneoCommand) -> None:
        torneo = await self._repo.find_by_id(cmd.torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {cmd.torneo_id} no encontrado")
        torneo.actualizar(
            nombre=cmd.nombre,
            descripcion=cmd.descripcion,
            fecha_inicio=cmd.fecha_inicio,
            fecha_fin=cmd.fecha_fin,
            sede=Sede(nombre=cmd.sede_nombre, ciudad=cmd.sede_ciudad, pais=cmd.sede_pais),
            grupos_etarios=cmd.grupos_etarios,
        )
        await self._repo.save(torneo)
