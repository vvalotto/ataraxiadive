from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from identidad.domain.exceptions import CampoRequerido
from identidad.domain.value_objects.rol import Rol


@dataclass
class Usuario:
    usuario_id: UUID
    nombre: str
    apellido: str
    email: str
    password_hash: str  # bcrypt — nunca plain text
    rol: Rol
    activo: bool = field(default=True)

    def __post_init__(self) -> None:
        self.nombre = self._validar_requerido(self.nombre, "nombre")
        self.apellido = self._validar_requerido(self.apellido, "apellido")

    @staticmethod
    def _validar_requerido(valor: str, campo: str) -> str:
        normalizado = valor.strip()
        if not normalizado:
            raise CampoRequerido(campo)
        return normalizado
