from __future__ import annotations

import re
from dataclasses import dataclass, field
from uuid import UUID

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _no_vacio_si_presente(valor: str | None, label: str) -> None:
    if valor is not None and not valor.strip():
        raise ValueError(f"{label} no puede ser vacío")


@dataclass
class Juez:
    juez_id: UUID
    email: str
    numero_licencia: str | None = field(default=None)
    federacion: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not _EMAIL_RE.match(self.email):
            raise ValueError("INV-11.4-01: email debe tener formato válido")
        _no_vacio_si_presente(self.numero_licencia, "INV-11.4-03: numero_licencia")
        _no_vacio_si_presente(self.federacion, "INV-11.4-04: federacion")

    def actualizar(
        self,
        numero_licencia: str | None = None,
        federacion: str | None = None,
    ) -> None:
        if numero_licencia is not None:
            _no_vacio_si_presente(numero_licencia, "numero_licencia")
            self.numero_licencia = numero_licencia
        if federacion is not None:
            _no_vacio_si_presente(federacion, "federacion")
            self.federacion = federacion
