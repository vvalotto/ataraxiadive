from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from collections.abc import Awaitable, Callable

from torneo.domain.exceptions import TorneoNoEncontrado
from torneo.domain.ports.torneo_repository_port import TorneoRepositoryPort


@dataclass(frozen=True)
class TransicionarTorneoCommand:
    torneo_id: UUID


class _TransicionHandler:
    def __init__(self, repo: TorneoRepositoryPort) -> None:
        self._repo = repo

    async def _ejecutar(self, torneo_id: UUID, accion: str) -> None:
        torneo = await self._repo.find_by_id(torneo_id)
        if torneo is None:
            raise TorneoNoEncontrado(f"Torneo {torneo_id} no encontrado")
        getattr(torneo, accion)()
        await self._repo.save(torneo)


class AbrirInscripcionHandler(_TransicionHandler):
    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        await self._ejecutar(cmd.torneo_id, "abrir_inscripcion")


class CerrarInscripcionHandler(_TransicionHandler):
    def __init__(
        self,
        repo: TorneoRepositoryPort,
        precondition: Callable[[UUID], Awaitable[None]] | None = None,
    ) -> None:
        super().__init__(repo)
        self._precondition = precondition

    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        if self._precondition is not None:
            await self._precondition(cmd.torneo_id)
        await self._ejecutar(cmd.torneo_id, "cerrar_inscripcion")


class IniciarEjecucionHandler(_TransicionHandler):
    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        await self._ejecutar(cmd.torneo_id, "iniciar_ejecucion")


class VolverAPreparacionHandler(_TransicionHandler):
    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        await self._ejecutar(cmd.torneo_id, "volver_a_preparacion")


class IniciarPremiacionHandler(_TransicionHandler):
    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        await self._ejecutar(cmd.torneo_id, "iniciar_premiacion")


class CerrarTorneoHandler(_TransicionHandler):
    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        await self._ejecutar(cmd.torneo_id, "cerrar")


class CancelarTorneoHandler(_TransicionHandler):
    async def handle(self, cmd: TransicionarTorneoCommand) -> None:
        await self._ejecutar(cmd.torneo_id, "cancelar")
