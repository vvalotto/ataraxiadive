from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Atleta:
    atleta_id: UUID
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
    club: str
    brevet: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("INV-A-01: nombre no puede ser vacío")
        if not self.apellido or not self.apellido.strip():
            raise ValueError("INV-A-01: apellido no puede ser vacío")
        if not _EMAIL_RE.match(self.email):
            raise ValueError("INV-A-02: email debe tener formato válido")
        if self.fecha_nacimiento >= date.today():
            raise ValueError("INV-A-04: fecha_nacimiento debe ser en el pasado")
        if not self.club or not self.club.strip():
            raise ValueError("INV-A-05: club no puede ser vacío")
