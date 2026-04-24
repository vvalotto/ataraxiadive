from __future__ import annotations

import uuid
from dataclasses import dataclass
from uuid import UUID

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import EmailYaRegistrado, PasswordDemasiadoCorto, RolNoPermitido
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol

_MIN_PASSWORD_LENGTH = 8


@dataclass(frozen=True)
class RegistrarUsuarioCommand:
    nombre: str
    apellido: str
    email: str
    password: str  # plain — el handler hashea con bcrypt
    rol: Rol


class RegistrarUsuarioHandler:
    def __init__(self, repo: UsuarioRepositoryPort, password_hasher: PasswordHashingPort) -> None:
        self._repo = repo
        self._password_hasher = password_hasher

    async def handle(self, cmd: RegistrarUsuarioCommand) -> UUID:
        # INV-ID-02: mínimo 8 caracteres
        if len(cmd.password) < _MIN_PASSWORD_LENGTH:
            raise PasswordDemasiadoCorto()

        if cmd.rol == Rol.ADMIN:
            raise RolNoPermitido()

        # INV-ID-01: email único
        existente = await self._repo.find_by_email(cmd.email)
        if existente is not None:
            raise EmailYaRegistrado(cmd.email)

        # INV-ID-03: hash bcrypt — nunca plain text
        password_hash = self._password_hasher.hash(cmd.password)

        usuario = Usuario(
            usuario_id=uuid.uuid4(),
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            email=cmd.email,
            password_hash=password_hash,
            rol=cmd.rol,
        )
        await self._repo.save(usuario)
        return usuario.usuario_id
