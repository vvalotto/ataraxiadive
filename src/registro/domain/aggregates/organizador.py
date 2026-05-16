from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import UUID

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass
class Organizador:
    organizador_id: UUID
    email: str
    nombre_organizacion: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.email):
            raise ValueError("INV-11.5-01: email debe tener formato válido")
        if self.nombre_organizacion is not None and not self.nombre_organizacion.strip():
            raise ValueError("INV-11.5-03: nombre_organizacion no puede ser string vacío")

    def actualizar(self, nombre_organizacion: str | None) -> None:
        """Actualiza nombre_organizacion. None limpia el campo explícitamente."""
        if nombre_organizacion is not None and not nombre_organizacion.strip():
            raise ValueError("INV-11.5-03: nombre_organizacion no puede ser string vacío")
        self.nombre_organizacion = nombre_organizacion
