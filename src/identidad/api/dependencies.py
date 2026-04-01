from __future__ import annotations

from typing import Annotated, Callable

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from identidad.domain.exceptions import TokenInvalido
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.jwt_service import JWTService

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(_oauth2_scheme)],
) -> dict:  # type: ignore[type-arg]
    """Verifica JWT y retorna payload {sub, email, rol}. Lanza 401 si inválido."""
    try:
        jwt_svc = JWTService()
        return jwt_svc.verify(token)
    except (TokenInvalido, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def require_rol(*roles: Rol) -> Callable:  # type: ignore[type-arg]
    """Factory de dependencia que exige uno de los roles dados. Lanza 403 si el rol es insuficiente."""
    _roles_values = {r.value for r in roles}

    def _dep(current_user: Annotated[dict, Depends(get_current_user)]) -> dict:  # type: ignore[type-arg]
        if current_user.get("rol") not in _roles_values:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Rol insuficiente")
        return current_user

    return _dep


OrganizadorDep = Annotated[dict, Depends(require_rol(Rol.ORGANIZADOR, Rol.ADMIN))]
JuezDep = Annotated[dict, Depends(require_rol(Rol.JUEZ, Rol.ORGANIZADOR, Rol.ADMIN))]
AtletaDep = Annotated[dict, Depends(require_rol(Rol.ATLETA, Rol.ADMIN))]
