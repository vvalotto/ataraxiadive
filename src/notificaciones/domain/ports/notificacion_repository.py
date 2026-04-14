from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class NotificacionRepository(ABC):
    @abstractmethod
    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None: ...

    @abstractmethod
    async def load(self, stream_id: str) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def exists_success_by_evento_fuente_id(self, evento_fuente_id: str) -> bool: ...
