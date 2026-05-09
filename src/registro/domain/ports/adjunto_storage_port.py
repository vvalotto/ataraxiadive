from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class AdjuntoStoragePort(ABC):
    @abstractmethod
    def guardar(
        self,
        *,
        inscripcion_id: UUID,
        nombre_archivo: str,
        filename_original: str | None,
        contenido: bytes,
    ) -> str: ...
