from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from registro.domain.aggregates.juez import Juez
from registro.domain.exceptions import JuezYaRegistrado
from registro.domain.ports.juez_repository_port import JuezRepositoryPort


@dataclass(frozen=True)
class RegistrarJuezCommand:
    email: str
    numero_licencia: str | None = field(default=None)
    federacion: str | None = field(default=None)


class RegistrarJuezHandler:
    def __init__(self, repo: JuezRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: RegistrarJuezCommand) -> UUID:
        existing = await self._repo.find_by_email(cmd.email)
        if existing is not None:
            raise JuezYaRegistrado(f"Ya existe un perfil de juez con email {cmd.email}")

        juez = Juez(
            juez_id=uuid4(),
            email=cmd.email,
            numero_licencia=cmd.numero_licencia,
            federacion=cmd.federacion,
        )
        await self._repo.save(juez)
        return juez.juez_id
