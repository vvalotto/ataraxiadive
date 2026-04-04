"""Implementación SQLite del Event Store — ADR-007, ADR-008."""

from __future__ import annotations

import json
from typing import Any

import aiosqlite

from shared.domain.ports.event_store_port import EventStorePort


class ConcurrencyError(Exception):
    """Se lanza cuando la versión esperada no coincide con la versión actual del stream."""


class SQLiteEventStore(EventStorePort):
    """Implementación del EventStorePort sobre SQLite (aiosqlite).

    La tabla `events` es append-only: no se permiten UPDATE ni DELETE.
    Un stream_id corresponde a una instancia de aggregate (ej: "performance-<uuid>").
    """

    def __init__(self, db_path: str) -> None:
        self._db_path = db_path

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        async with aiosqlite.connect(self._db_path) as db:
            if expected_version is not None:
                cursor = await db.execute(
                    "SELECT COUNT(*) FROM events WHERE stream_id = ?", (stream_id,)
                )
                row = await cursor.fetchone()
                current_version = row[0] if row else 0
                if current_version != expected_version:
                    raise ConcurrencyError(
                        f"Versión esperada {expected_version}, versión actual {current_version} "
                        f"en stream '{stream_id}'"
                    )
            await db.execute(
                """
                INSERT INTO events (stream_id, event_type, payload, version)
                VALUES (
                    ?, ?, ?,
                    (SELECT COALESCE(MAX(version), 0) + 1 FROM events WHERE stream_id = ?)
                )
                """,
                (stream_id, event_type, json.dumps(payload), stream_id),
            )
            await db.commit()

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT event_type, payload, version, occurred_at
                FROM events
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

    async def load_all_streams_with_prefix(self, prefix: str) -> list[list[dict[str, Any]]]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT stream_id, event_type, payload, version, occurred_at
                FROM events
                WHERE stream_id LIKE ?
                ORDER BY stream_id, version ASC
                """,
                (prefix + "%",),
            )
            rows = await cursor.fetchall()

        streams: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            sid = row["stream_id"]
            if sid not in streams:
                streams[sid] = []
            streams[sid].append(
                {
                    "event_type": row["event_type"],
                    "payload": json.loads(row["payload"]),
                    "version": row["version"],
                    "occurred_at": row["occurred_at"],
                }
            )
        return list(streams.values())

    async def load_all_events_ordered(self, prefix: str) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT id AS sequence, stream_id, event_type, payload, occurred_at
                FROM events
                WHERE stream_id LIKE ?
                ORDER BY id ASC
                """,
                (prefix + "%",),
            )
            rows = await cursor.fetchall()
        return [
            {
                "sequence": row["sequence"],
                "stream_id": row["stream_id"],
                "event_type": row["event_type"],
                "payload": json.loads(row["payload"]),
                "occurred_at": row["occurred_at"],
            }
            for row in rows
        ]

    async def load_from(self, stream_id: str, from_version: int) -> list[dict[str, Any]]:
        async with aiosqlite.connect(self._db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                """
                SELECT event_type, payload, version, occurred_at
                FROM events
                WHERE stream_id = ? AND version >= ?
                ORDER BY version ASC
                """,
                (stream_id, from_version),
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
