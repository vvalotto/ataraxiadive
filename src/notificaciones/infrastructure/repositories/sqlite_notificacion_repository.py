from __future__ import annotations

from typing import Any

from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)


class SQLiteNotificacionRepository(NotificacionRepository):
    def __init__(self, event_store: SQLiteNotificacionEventStore | None = None) -> None:
        self._event_store = event_store or SQLiteNotificacionEventStore()

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        await self._event_store.append(stream_id, event_type, payload, expected_version)

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        return await self._event_store.load(stream_id)

    async def exists_success_by_evento_fuente_id(self, evento_fuente_id: str) -> bool:
        return await self._event_store.exists_success_by_evento_fuente_id(evento_fuente_id)
