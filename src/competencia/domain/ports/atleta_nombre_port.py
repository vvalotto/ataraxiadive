"""Puerto AtletaNombrePort — resolución de nombre de atleta por ID."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class AtletaNombrePort(ABC):
    """Puerto para resolver el nombre completo de un atleta dado su ID.

    La implementación concreta consulta el BC Registro.
    Requerido por:
        ObtenerGrillaHandler: necesita el nombre del atleta para el read model.
    """

    @abstractmethod
    async def get_nombre(self, atleta_id: UUID) -> str:
        """Retorna el nombre completo del atleta.

        Args:
            atleta_id: Identificador del atleta en el BC Registro.

        Returns:
            Nombre completo (nombre + apellido) o un fallback si no se encuentra.
        """
