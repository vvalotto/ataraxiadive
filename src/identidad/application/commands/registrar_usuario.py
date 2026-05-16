from __future__ import annotations

import logging
import re
import uuid
from dataclasses import dataclass, field
from uuid import UUID

from identidad.application.commands.autenticar_usuario import TokenResponse
from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import (
    CredencialesInvalidas,
    PasswordDemasiadoCorto,
    RolNoPermitido,
    RolYaAsignado,
)
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.perfil_registro_port import PerfilRegistroPort
from identidad.domain.ports.token_service_port import TokenServicePort
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
    roles: list[Rol]
    numero_licencia: str | None = field(default=None)
    federacion: str | None = field(default=None)
    nombre_organizacion: str | None = field(default=None)


@dataclass(frozen=True)
class RegistroResult:
    usuario_id: UUID
    es_usuario_nuevo: bool = True
    token_response: TokenResponse | None = None
    roles_disponibles: list[Rol] = field(default_factory=list)

    @property
    def requires_role_selection(self) -> bool:
        return self.token_response is None


class RegistrarUsuarioHandler:
    def __init__(
        self,
        repo: UsuarioRepositoryPort,
        password_hasher: PasswordHashingPort,
        token_service: TokenServicePort,
        email_sender: EmailPort | None = None,
        perfil_registro: PerfilRegistroPort | None = None,
    ) -> None:
        self._repo = repo
        self._password_hasher = password_hasher
        self._token_service = token_service
        self._email_sender = email_sender
        self._perfil_registro = perfil_registro

    async def handle(self, cmd: RegistrarUsuarioCommand) -> RegistroResult:
        if (
            len(cmd.password) < _MIN_PASSWORD_LENGTH
            or not re.search(r"[A-Z]", cmd.password)
            or not re.search(r"[0-9]", cmd.password)
        ):
            raise PasswordDemasiadoCorto()

        if Rol.ADMIN in cmd.roles:
            raise RolNoPermitido()

        existente = await self._repo.find_by_email(cmd.email)
        if existente is not None:
            # Email ya registrado: validar password y agregar roles nuevos
            if not self._password_hasher.verify(cmd.password, existente.password_hash):
                raise CredencialesInvalidas()
            for rol in cmd.roles:
                if rol in existente.roles:
                    raise RolYaAsignado(rol.value)
                existente.roles.append(rol)
            await self._repo.save(existente)
            await self._crear_perfiles(cmd, existente.usuario_id)
            return self._build_result(existente, es_usuario_nuevo=False)

        password_hash = self._password_hasher.hash(cmd.password)
        usuario = Usuario(
            usuario_id=uuid.uuid4(),
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            email=cmd.email,
            password_hash=password_hash,
            roles=list(cmd.roles),
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

        await self._crear_perfiles(cmd, usuario.usuario_id)
        return self._build_result(usuario, es_usuario_nuevo=True)

    async def _crear_perfiles(self, cmd: RegistrarUsuarioCommand, usuario_id: UUID) -> None:
        if self._perfil_registro is None:
            return
        await self._perfil_registro.crear_perfiles(
            usuario_id=usuario_id,
            nombre=cmd.nombre,
            apellido=cmd.apellido,
            email=cmd.email,
            roles=cmd.roles,
            numero_licencia=cmd.numero_licencia,
            federacion=cmd.federacion,
            nombre_organizacion=cmd.nombre_organizacion,
        )

    def _build_result(self, usuario: Usuario, *, es_usuario_nuevo: bool) -> RegistroResult:
        if len(usuario.roles) == 1:
            token = self._token_service.generate(usuario, usuario.roles[0])
            return RegistroResult(
                usuario_id=usuario.usuario_id,
                es_usuario_nuevo=es_usuario_nuevo,
                token_response=TokenResponse(access_token=token),
            )
        return RegistroResult(
            usuario_id=usuario.usuario_id,
            es_usuario_nuevo=es_usuario_nuevo,
            roles_disponibles=list(usuario.roles),
        )
