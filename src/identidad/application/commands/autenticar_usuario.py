from __future__ import annotations

from dataclasses import dataclass

from identidad.domain.exceptions import CredencialesInvalidas, UsuarioInactivo
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort


@dataclass(frozen=True)
class AutenticarUsuarioCommand:
    email: str
    password: str


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str = "bearer"


class AutenticarUsuarioHandler:
    def __init__(
        self,
        repo: UsuarioRepositoryPort,
        token_service: TokenServicePort,
        password_hasher: PasswordHashingPort,
    ) -> None:
        self._repo = repo
        self._token_service = token_service
        self._password_hasher = password_hasher

    async def handle(self, cmd: AutenticarUsuarioCommand) -> TokenResponse:
        usuario = await self._repo.find_by_email(cmd.email)
        if usuario is None:
            raise CredencialesInvalidas()

        if not usuario.activo:
            raise UsuarioInactivo(cmd.email)

        if not self._password_hasher.verify(cmd.password, usuario.password_hash):
            raise CredencialesInvalidas()

        token = self._token_service.generate(usuario)
        return TokenResponse(access_token=token)
