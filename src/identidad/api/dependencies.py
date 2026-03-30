from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from identidad.domain.exceptions import TokenInvalido
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
