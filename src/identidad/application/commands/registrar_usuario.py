from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass
from uuid import UUID

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import EmailYaRegistrado, PasswordDemasiadoCorto, RolNoPermitido
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol
from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario

_MIN_PASSWORD_LENGTH = 10
_log = logging.getLogger(__name__)


@dataclass(frozen=True)
class RegistrarUsuarioCommand:
    nombre: str
    apellido: str
    email: str
    password: str  # plain — el handler hashea con bcrypt
    rol: Rol


class RegistrarUsuarioHandler:
    def __init__(
        self,
        repo: UsuarioRepositoryPort,
        password_hasher: PasswordHashingPort,
        email_sender: EmailPort | None = None,
    ) -> None:
        self._repo = repo
        self._password_hasher = password_hasher
        self._email_sender = email_sender

    async def handle(self, cmd: RegistrarUsuarioCommand) -> UUID:
        # INV-ID-02: mínimo 10 caracteres, al menos 1 mayúscula y 1 número
        if (
            len(cmd.password) < _MIN_PASSWORD_LENGTH
            or not re.search(r"[A-Z]", cmd.password)
            or not re.search(r"[0-9]", cmd.password)
        ):
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

        if self._email_sender is not None:
            try:
                await self._email_sender.enviar(
                    Destinatario(
                        email=usuario.email,
                        nombre=f"{usuario.nombre} {usuario.apellido}".strip(),
                    ),
                    ContenidoEmail(
                        asunto="Bienvenido/a a AtaraxiaDive",
                        cuerpo_texto=(
                            f"Hola {usuario.nombre},\n"
                            "Tu cuenta en AtaraxiaDive fue creada exitosamente.\n"
                            "Ya podés acceder a tu portal."
                        ),
                    ),
                )
            except Exception:
                _log.warning("No se pudo enviar email de bienvenida a %s", usuario.email)

        return usuario.usuario_id
