from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from uuid import UUID

from shared.domain.value_objects.disciplina import Disciplina


class TorneoConsultaPort(ABC):
    """ACL read-only sobre BC Torneo para validar inscripciones."""

    @abstractmethod
    async def esta_abierto_para_inscripcion(self, torneo_id: UUID) -> bool: ...

    @abstractmethod
    async def obtener_fecha_inicio(self, torneo_id: UUID) -> date: ...

    @abstractmethod
    async def obtener_disciplinas(self, torneo_id: UUID) -> frozenset[Disciplina]: ...
