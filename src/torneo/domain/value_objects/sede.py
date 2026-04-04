from dataclasses import dataclass


@dataclass(frozen=True)
class Sede:
    nombre: str
    ciudad: str
    pais: str
