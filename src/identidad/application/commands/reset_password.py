from __future__ import annotations

import re
from dataclasses import dataclass

from identidad.domain.exceptions import PasswordDemasiadoCorto, TokenInvalido, TokenResetInvalido
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort

_MIN_PASSWORD_LENGTH = 10


@dataclass(frozen=True)
class ResetPasswordCommand:
    token: str
    password_nueva: str


class ResetPasswordHandler:
    def __init__(
        self,
        repo: UsuarioRepositoryPort,
        token_service: TokenServicePort,
        password_hasher: PasswordHashingPort,
    ) -> None:
        self._repo = repo
        self._token_service = token_service
        self._password_hasher = password_hasher

    async def handle(self, cmd: ResetPasswordCommand) -> None:
        if (
            len(cmd.password_nueva) < _MIN_PASSWORD_LENGTH
            or not re.search(r"[A-Z]", cmd.password_nueva)
            or not re.search(r"[0-9]", cmd.password_nueva)
        ):
            raise PasswordDemasiadoCorto()

        try:
            payload = self._token_service.verify(cmd.token)
        except TokenInvalido as exc:
            raise TokenResetInvalido() from exc

        if payload.get("type") != "password_reset":
            raise TokenResetInvalido()

        email = payload.get("sub")
        if not isinstance(email, str) or not email.strip():
            raise TokenResetInvalido()

        usuario = await self._repo.find_by_email(email)
        if usuario is None:
            raise TokenResetInvalido()

        usuario.password_hash = self._password_hasher.hash(cmd.password_nueva)
        await self._repo.save(usuario)
