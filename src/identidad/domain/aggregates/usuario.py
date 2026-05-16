from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID

from identidad.domain.exceptions import (
    CampoRequerido,
    RolDuplicado,
    RolesVacios,
    RolNoEncontrado,
    RolNoRemovible,
    UltimoRolNoRemovible,
)
from identidad.domain.value_objects.rol import Rol


@dataclass
class Usuario:
    usuario_id: UUID
    nombre: str
    apellido: str
    email: str
    password_hash: str  # bcrypt — nunca plain text
    roles: list[Rol]
    activo: bool = field(default=True)

    def __post_init__(self) -> None:
        self.nombre = self._validar_requerido(self.nombre, "nombre")
        self.apellido = self._validar_requerido(self.apellido, "apellido")
        if not self.roles:
            raise RolesVacios()
        if len(self.roles) != len(set(self.roles)):
            raise RolDuplicado()

    def agregar_rol(self, rol: Rol) -> None:
        from identidad.domain.exceptions import RolNoPermitido, RolYaAsignado

        if rol == Rol.ADMIN:
            raise RolNoPermitido()
        if rol in self.roles:
            raise RolYaAsignado(rol.value)
        self.roles.append(rol)

    def quitar_rol(self, rol: Rol) -> None:
        if rol == Rol.ATLETA:
            raise RolNoRemovible(rol.value)
        if rol not in self.roles:
            raise RolNoEncontrado(rol.value)
        if len(self.roles) == 1:
            raise UltimoRolNoRemovible()
        self.roles.remove(rol)

    @staticmethod
    def _validar_requerido(valor: str, campo: str) -> str:
        normalizado = valor.strip()
        if not normalizado:
            raise CampoRequerido(campo)
        return normalizado
