from __future__ import annotations

import re
from dataclasses import dataclass

from notificaciones.domain.exceptions import DestinatarioInvalido

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


@dataclass(frozen=True)
class Destinatario:
    email: str
    nombre: str | None = None

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.email):
            raise DestinatarioInvalido("Destinatario.email debe tener formato válido")
        if self.nombre is not None and not self.nombre.strip():
            raise DestinatarioInvalido("Destinatario.nombre no puede ser vacío")
