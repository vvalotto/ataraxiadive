from __future__ import annotations

from dataclasses import dataclass, field

from registro.domain.exceptions import JuezNoEncontrado
from registro.domain.ports.juez_repository_port import JuezRepositoryPort


@dataclass(frozen=True)
class ActualizarJuezCommand:
    email: str
    numero_licencia: str | None = field(default=None)
    federacion: str | None = field(default=None)


class ActualizarJuezHandler:
    def __init__(self, repo: JuezRepositoryPort) -> None:
        self._repo = repo

    async def handle(self, cmd: ActualizarJuezCommand):  # type: ignore[return]
        juez = await self._repo.find_by_email(cmd.email)
        if juez is None:
            raise JuezNoEncontrado(f"No existe perfil de juez con email {cmd.email}")

        juez.actualizar(
            numero_licencia=cmd.numero_licencia,
            federacion=cmd.federacion,
        )
        await self._repo.save(juez)
        return juez
