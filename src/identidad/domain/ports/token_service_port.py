from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from identidad.domain.aggregates.usuario import Usuario

if TYPE_CHECKING:
    from identidad.domain.value_objects.rol import Rol


class TokenServicePort(ABC):
    """Puerto de generacion y verificacion de tokens de autenticacion."""

    @abstractmethod
    def generate(self, usuario: Usuario, rol_activo: "Rol") -> str:
        """Genera un token para el usuario autenticado con el rol activo indicado."""

    @abstractmethod
    def generate_reset_token(self, email: str) -> str:
        """Genera un token de recuperacion de password asociado a un email."""

    @abstractmethod
    def verify(self, token: str) -> dict:
        """Verifica el token y retorna su payload."""
