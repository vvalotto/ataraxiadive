from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import TokenInvalido
from identidad.domain.ports.token_service_port import TokenServicePort

_DEFAULT_EXPIRY_HOURS = 24
_RESET_TOKEN_EXPIRY_HOURS = 1


class JWTService(TokenServicePort):
    """Genera y verifica tokens JWT. INV-ID-04/05."""

    def __init__(self) -> None:
        secret = os.environ.get("IDENTIDAD_JWT_SECRET")
        if not secret:
            raise ValueError("IDENTIDAD_JWT_SECRET no está configurada")
        expiry_hours = int(os.environ.get("IDENTIDAD_JWT_EXPIRY_HOURS", _DEFAULT_EXPIRY_HOURS))
        self._secret = secret
        self._expiry_hours = expiry_hours
        self._algorithm = "HS256"

    def generate(self, usuario: Usuario) -> str:
        payload = {
            "sub": str(usuario.usuario_id),
            "email": usuario.email,
            "rol": usuario.rol.value,
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=self._expiry_hours),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def generate_reset_token(self, email: str) -> str:
        payload = {
            "sub": email,
            "type": "password_reset",
            "exp": datetime.now(tz=timezone.utc) + timedelta(hours=_RESET_TOKEN_EXPIRY_HOURS),
        }
        return jwt.encode(payload, self._secret, algorithm=self._algorithm)

    def verify(self, token: str) -> dict:  # type: ignore[type-arg]
        try:
            return jwt.decode(token, self._secret, algorithms=[self._algorithm])
        except jwt.PyJWTError as exc:
            raise TokenInvalido() from exc
