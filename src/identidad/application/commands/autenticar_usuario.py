from __future__ import annotations

from dataclasses import dataclass

import bcrypt

from identidad.domain.exceptions import CredencialesInvalidas, UsuarioInactivo
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.infrastructure.jwt_service import JWTService


@dataclass(frozen=True)
class AutenticarUsuarioCommand:
    email: str
    password: str


@dataclass(frozen=True)
class TokenResponse:
    access_token: str
    token_type: str = "bearer"


class AutenticarUsuarioHandler:
    def __init__(self, repo: UsuarioRepositoryPort, jwt_service: JWTService) -> None:
        self._repo = repo
        self._jwt = jwt_service

    async def handle(self, cmd: AutenticarUsuarioCommand) -> TokenResponse:
        usuario = await self._repo.find_by_email(cmd.email)
        if usuario is None:
            raise CredencialesInvalidas()

        if not usuario.activo:
            raise UsuarioInactivo(cmd.email)

        if not bcrypt.checkpw(cmd.password.encode(), usuario.password_hash.encode()):
            raise CredencialesInvalidas()

        token = self._jwt.generate(usuario)
        return TokenResponse(access_token=token)
