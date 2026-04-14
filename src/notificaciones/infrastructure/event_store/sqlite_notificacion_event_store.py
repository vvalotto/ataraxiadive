"""Event Store SQLite específico del BC Notificaciones."""

from __future__ import annotations

import json
import os
from typing import Any

import aiosqlite

_CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS notificaciones_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload TEXT NOT NULL,
    version INTEGER NOT NULL,
    occurred_at TEXT NOT NULL
)
"""

_CREATE_STREAM_INDEX = """
CREATE INDEX IF NOT EXISTS idx_notificaciones_stream
ON notificaciones_events(stream_id)
"""

_CREATE_FUENTE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_notificaciones_fuente
ON notificaciones_events(json_extract(payload, '$.evento_fuente_id'))
"""


class SQLiteNotificacionEventStore:
    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or os.getenv("NOTIFICACIONES_DB_PATH", "data/notificaciones.db")

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            await self._ensure_schema(db)
            if expected_version is not None:
                current_version = await self._current_version(db, stream_id)
                if current_version != expected_version:
                    raise ValueError(
                        f"Versión esperada {expected_version}, versión actual {current_version}"
                    )
            version = await self._current_version(db, stream_id) + 1
            occurred_at = payload.get("occurred_at", "")
            await db.execute(
                """
                INSERT INTO notificaciones_events
                    (stream_id, event_type, payload, version, occurred_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (stream_id, event_type, json.dumps(payload), version, occurred_at),
            )
            await db.commit()

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self._db_path) as db:
            await self._ensure_schema(db)
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT event_type, payload, version, occurred_at
                FROM notificaciones_events
                WHERE stream_id = ?
                ORDER BY version ASC
                """,
                (stream_id,),
            )
            rows = await cursor.fetchall()
        return [
            {
                "event_type": row["event_type"],
                "payload": json.loads(row["payload"]),
                "version": row["version"],
                "occurred_at": row["occurred_at"],
            }
            for row in rows
        ]

    async def exists_success_by_evento_fuente_id(self, evento_fuente_id: str) -> bool:
        async with aiosqlite.connect(self._db_path) as db:
            await self._ensure_schema(db)
            cursor = await db.execute(
                """
                SELECT 1
                FROM notificaciones_events
                WHERE event_type = 'NotificacionEnviada'
                  AND json_extract(payload, '$.evento_fuente_id') = ?
                LIMIT 1
                """,
                (evento_fuente_id,),
            )
            row = await cursor.fetchone()
        return row is not None

    async def _ensure_schema(self, db: aiosqlite.Connection) -> None:
        await db.execute(_CREATE_TABLE)
        await db.execute(_CREATE_STREAM_INDEX)
        await db.execute(_CREATE_FUENTE_INDEX)
        await db.commit()

    async def _current_version(self, db: aiosqlite.Connection, stream_id: str) -> int:
        cursor = await db.execute(
            "SELECT COALESCE(MAX(version), 0) FROM notificaciones_events WHERE stream_id = ?",
            (stream_id,),
        )
        row = await cursor.fetchone()
        return int(row[0]) if row and row[0] is not None else 0
