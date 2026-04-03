from __future__ import annotations

import bcrypt

from identidad.domain.ports.password_hashing_port import PasswordHashingPort


class BcryptPasswordHasher(PasswordHashingPort):
    """Adapter de infraestructura para hashing con bcrypt."""

    def hash(self, password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    def verify(self, password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())
