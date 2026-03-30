from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from identidad.domain.value_objects.rol import Rol


@dataclass
class Usuario:
    usuario_id: UUID
    email: str
    password_hash: str  # bcrypt — nunca plain text
    rol: Rol
    activo: bool = field(default=True)
