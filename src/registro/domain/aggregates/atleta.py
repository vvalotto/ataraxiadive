from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def _no_vacio_si_presente(valor: str | None, label: str) -> None:
    if valor is not None and not valor.strip():
        raise ValueError(f"{label} no puede ser vacío")


@dataclass
class Atleta:
    atleta_id: UUID
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria | None = field(default=None)
    club: str | None = field(default=None)
    brevet: str | None = field(default=None)
    dni: str | None = field(default=None)
    telefono: str | None = field(default=None)

    def __post_init__(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("INV-A-01: nombre no puede ser vacío")
        if not self.apellido or not self.apellido.strip():
            raise ValueError("INV-A-01: apellido no puede ser vacío")
        if not _EMAIL_RE.match(self.email):
            raise ValueError("INV-A-02: email debe tener formato válido")
        if self.fecha_nacimiento >= date.today():
            raise ValueError("INV-A-04: fecha_nacimiento debe ser en el pasado")
        _no_vacio_si_presente(self.club, "INV-11.3-04: club")
        _no_vacio_si_presente(self.dni, "INV-11.3-05: dni")
        _no_vacio_si_presente(self.telefono, "INV-11.3-05: telefono")

    def actualizar(
        self,
        nombre: str | None = None,
        apellido: str | None = None,
        categoria: Categoria | None = None,
        club: str | None = None,
        fecha_nacimiento: date | None = None,
        brevet: str | None = None,
        dni: str | None = None,
        telefono: str | None = None,
    ) -> None:
        if nombre is not None:
            if not nombre.strip():
                raise ValueError("INV-A-01: nombre no puede ser vacío")
            self.nombre = nombre
        if apellido is not None:
            if not apellido.strip():
                raise ValueError("INV-A-01: apellido no puede ser vacío")
            self.apellido = apellido
        if categoria is not None:
            self.categoria = categoria
        if club is not None:
            _no_vacio_si_presente(club, "club")
            self.club = club
        if fecha_nacimiento is not None:
            if fecha_nacimiento >= date.today():
                raise ValueError("INV-A-04: fecha_nacimiento debe ser en el pasado")
            self.fecha_nacimiento = fecha_nacimiento
        if brevet is not None:
            self.brevet = brevet or None
        if dni is not None:
            _no_vacio_si_presente(dni, "dni")
            self.dni = dni
        if telefono is not None:
            _no_vacio_si_presente(telefono, "telefono")
            self.telefono = telefono
