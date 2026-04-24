from __future__ import annotations

import re
from dataclasses import dataclass
from uuid import UUID

from identidad.domain.exceptions import (
    PasswordActualIncorrecto,
    PasswordDemasiadoCorto,
    UsuarioNoEncontrado,
)
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort

_MIN_PASSWORD_LENGTH = 10


@dataclass(frozen=True)
class CambiarPasswordCommand:
    usuario_id: UUID
    password_actual: str
    password_nueva: str


class CambiarPasswordHandler:
    def __init__(self, repo: UsuarioRepositoryPort, password_hasher: PasswordHashingPort) -> None:
        self._repo = repo
        self._password_hasher = password_hasher

    async def handle(self, cmd: CambiarPasswordCommand) -> None:
        usuario = await self._repo.find_by_id(cmd.usuario_id)
        if usuario is None:
            raise UsuarioNoEncontrado(str(cmd.usuario_id))

        if not self._password_hasher.verify(cmd.password_actual, usuario.password_hash):
            raise PasswordActualIncorrecto()

        if (
            len(cmd.password_nueva) < _MIN_PASSWORD_LENGTH
            or not re.search(r"[A-Z]", cmd.password_nueva)
            or not re.search(r"[0-9]", cmd.password_nueva)
        ):
            raise PasswordDemasiadoCorto()

        usuario.password_hash = self._password_hasher.hash(cmd.password_nueva)
        await self._repo.save(usuario)
