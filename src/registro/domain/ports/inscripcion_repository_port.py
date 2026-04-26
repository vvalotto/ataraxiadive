from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from registro.domain.aggregates.inscripcion import Inscripcion


class InscripcionRepositoryPort(ABC):
    @abstractmethod
    async def save(self, inscripcion: Inscripcion) -> None: ...

    @abstractmethod
    async def find_by_id(self, inscripcion_id: UUID) -> Inscripcion | None: ...

    @abstractmethod
    async def find_by_atleta_y_torneo(
        self, atleta_id: UUID, torneo_id: UUID
    ) -> Inscripcion | None: ...

    @abstractmethod
    async def find_by_torneo(self, torneo_id: UUID) -> list[Inscripcion]: ...

    @abstractmethod
    async def find_by_atleta(self, atleta_id: UUID) -> list[Inscripcion]: ...
