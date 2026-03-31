from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from uuid import UUID

from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaYaRegistrado
from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.value_objects.categoria import Categoria


@dataclass(frozen=True)
class RegistrarAtletaCommand:
    atleta_id: UUID
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
    brevet: str | None = None


class RegistrarAtletaHandler:
    def __init__(self, repo: AtletaRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: RegistrarAtletaCommand) -> UUID:
        existing = await self._repo.find_by_id(cmd.atleta_id)
        if existing is not None:
            raise AtletaYaRegistrado(f"Atleta {cmd.atleta_id} ya registrado")

        atleta = Atleta(
            atleta_id=cmd.atleta_id,
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            email=cmd.email,
            fecha_nacimiento=cmd.fecha_nacimiento,
            categoria=cmd.categoria,
            brevet=cmd.brevet,
        )
        await self._repo.save(atleta)
        return atleta.atleta_id
