from __future__ import annotations

from abc import ABC, abstractmethod


class PasswordHashingPort(ABC):
    """Puerto de hashing y verificacion de contrasenas."""

    @abstractmethod
    def hash(self, password: str) -> str:
        """Retorna el hash persistible de una contrasena."""

    @abstractmethod
    def verify(self, password: str, hashed: str) -> bool:
        """Verifica si la contrasena coincide con el hash dado."""
