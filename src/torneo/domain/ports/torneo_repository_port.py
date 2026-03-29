from abc import ABC, abstractmethod
from uuid import UUID

from torneo.domain.aggregates.torneo import Torneo


class TorneoRepositoryPort(ABC):
    @abstractmethod
    async def save(self, torneo: Torneo) -> None: ...

    @abstractmethod
    async def find_by_id(self, torneo_id: UUID) -> Torneo | None: ...

    @abstractmethod
    async def find_all(self) -> list[Torneo]: ...
