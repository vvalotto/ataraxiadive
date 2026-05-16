from __future__ import annotations

from dataclasses import dataclass

from identidad.domain.exceptions import CredencialesInvalidas, UsuarioInactivo
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol


@dataclass(frozen=True)
class AutenticarUsuarioCommand:
    email: str
    password: str
    rol_elegido: Rol | None = None


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str = "bearer"


@dataclass(frozen=True)
class RoleSelectionRequired:
    roles: list[Rol]


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

    async def handle(self, cmd: AutenticarUsuarioCommand) -> TokenResponse | RoleSelectionRequired:
        usuario = await self._repo.find_by_email(cmd.email)
        if usuario is None:
            raise CredencialesInvalidas()

        if not usuario.activo:
            raise UsuarioInactivo(cmd.email)

        if not self._password_hasher.verify(cmd.password, usuario.password_hash):
            raise CredencialesInvalidas()

        if cmd.rol_elegido is not None:
            if cmd.rol_elegido not in usuario.roles:
                raise CredencialesInvalidas()
            token = self._token_service.generate(usuario, cmd.rol_elegido)
            return TokenResponse(access_token=token)

        if len(usuario.roles) == 1:
            token = self._token_service.generate(usuario, usuario.roles[0])
            return TokenResponse(access_token=token)

        return RoleSelectionRequired(roles=list(usuario.roles))
