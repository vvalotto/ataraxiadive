from __future__ import annotations

from dataclasses import dataclass

from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaNoEncontrado
from registro.domain.ports.atleta_repository_port import AtletaRepositoryPort
from registro.domain.value_objects.categoria import Categoria


@dataclass(frozen=True)
class ActualizarAtletaCommand:
    email: str
    nombre: str | None = None
    apellido: str | None = None
    categoria: Categoria | None = None
    club: str | None = None


class ActualizarAtletaHandler:
    def __init__(self, repo: AtletaRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: ActualizarAtletaCommand) -> Atleta:
        atleta = await self._repo.find_by_email(cmd.email)
        if atleta is None:
            raise AtletaNoEncontrado(f"No existe perfil de atleta para {cmd.email}")
        atleta.actualizar(
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            categoria=cmd.categoria,
            club=cmd.club,
        )
        await self._repo.save(atleta)
        return atleta
