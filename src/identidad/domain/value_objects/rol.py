from __future__ import annotations

from enum import StrEnum


class Rol(StrEnum):
    ORGANIZADOR = "ORGANIZADOR"
    JUEZ = "JUEZ"
    ATLETA = "ATLETA"
    ADMIN = "ADMIN"
