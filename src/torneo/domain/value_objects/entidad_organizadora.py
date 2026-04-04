from dataclasses import dataclass


@dataclass(frozen=True)
class EntidadOrganizadora:
    nombre: str
    tipo: str  # "FEDERACION" | "CLUB" | "ORGANIZACION"
