from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from identidad.domain.exceptions import TokenInvalido
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.perfil_registro_port import PerfilRegistroPort
from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.jwt_service import JWTService
from identidad.infrastructure.repositories.sqlite_usuario_repository import (
    SQLiteUsuarioRepository,
)
from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.infrastructure.email.logging_email_adapter import LoggingEmailAdapter

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
_token_service: TokenServicePort | None = None
_password_hasher: PasswordHashingPort | None = None
_email_sender: EmailPort | None = None
_perfil_registro: PerfilRegistroPort | None = None


def configure_identity_dependencies(
    *,
    token_service: TokenServicePort | None = None,
    password_hasher: PasswordHashingPort | None = None,
    email_sender: EmailPort | None = None,
    perfil_registro: PerfilRegistroPort | None = None,
) -> None:
    """Permite configurar dependencias tecnicas desde el composition root."""
    global _token_service, _password_hasher, _email_sender, _perfil_registro
    _token_service = token_service
    _password_hasher = password_hasher
    _email_sender = email_sender
    _perfil_registro = perfil_registro


def get_perfil_registro() -> PerfilRegistroPort | None:
    return _perfil_registro


def get_usuario_repository() -> UsuarioRepositoryPort:
    return SQLiteUsuarioRepository()


def get_token_service() -> TokenServicePort:
    global _token_service
    if _token_service is None:
        _token_service = JWTService()
    return _token_service


def get_password_hasher() -> PasswordHashingPort:
    global _password_hasher
    if _password_hasher is None:
        _password_hasher = BcryptPasswordHasher()
    return _password_hasher


def get_email_sender() -> EmailPort:
    global _email_sender
    if _email_sender is None:
        _email_sender = LoggingEmailAdapter()
    return _email_sender


async def get_current_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
    token_service: Annotated[TokenServicePort, Depends(get_token_service)],
) -> dict:  # type: ignore[type-arg]
    """Verifica JWT y retorna payload {sub, email, rol}. Lanza 401 si inválido."""
    try:
        return token_service.verify(token)
    except (TokenInvalido, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_rol(*roles: Rol) -> Callable:  # type: ignore[type-arg]
    """Factory de dependencia que exige uno de los roles dados."""
    _roles_values = {r.value for r in roles}

    def _dep(
        current_user: Annotated[dict, Depends(get_current_user)],
    ) -> dict:  # type: ignore[type-arg]
        if current_user.get("rol") not in _roles_values:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Rol insuficiente",
            )
        return current_user

    return _dep


OrganizadorDep = Annotated[dict, Depends(require_rol(Rol.ORGANIZADOR, Rol.ADMIN))]
JuezDep = Annotated[dict, Depends(require_rol(Rol.JUEZ, Rol.ORGANIZADOR, Rol.ADMIN))]
AtletaDep = Annotated[dict, Depends(require_rol(Rol.ATLETA, Rol.ADMIN))]
