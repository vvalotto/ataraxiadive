from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaYaRegistrado
from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.value_objects.categoria import Categoria


@dataclass(frozen=True)
class RegistrarAtletaCommand:
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria | None = field(default=None)
    club: str | None = field(default=None)
    brevet: str | None = field(default=None)
    dni: str | None = field(default=None)
    telefono: str | None = field(default=None)


class RegistrarAtletaHandler:
    def __init__(self, repo: AtletaRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: RegistrarAtletaCommand) -> UUID:
        existing = await self._repo.find_by_email(cmd.email)
        if existing is not None:
            raise AtletaYaRegistrado(f"Ya existe un atleta con email {cmd.email}")

        atleta = Atleta(
            atleta_id=uuid4(),
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            email=cmd.email,
            fecha_nacimiento=cmd.fecha_nacimiento,
            categoria=cmd.categoria,
            club=cmd.club,
            brevet=cmd.brevet,
            dni=cmd.dni,
            telefono=cmd.telefono,
        )
        await self._repo.save(atleta)
        return atleta.atleta_id
