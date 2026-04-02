"""Tests de integración de consulta overall — US-3.5.3."""

from __future__ import annotations

from uuid import uuid4

import aiosqlite
import pytest

from resultados.application.queries.obtener_overall import (
    ObtenerOverallHandler,
    ObtenerOverallQuery,
)
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

CREATE_EVENTS_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL
            DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""


async def _init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _append_overall(
    store: SQLiteEventStore, torneo_id, entries: list[dict]
) -> None:
    await store.append(
        stream_id=f"ranking-overall-{torneo_id}",
        event_type="RankingOverallCalculado",
        payload={
            "torneo_id": str(torneo_id),
            "disciplinas": ["STA", "DNF"],
            "total": len(entries),
            "entries": entries,
            "calculado_en": "2026-04-02T12:05:00+00:00",
            "occurred_at": "2026-04-02T12:05:00+00:00",
        },
    )


@pytest.mark.asyncio
async def test_obtener_overall_reconstituye_ultima_version(tmp_path) -> None:
    db_path = tmp_path / "resultados.db"
    await _init_db(str(db_path))
    store = SQLiteEventStore(str(db_path))
    torneo_id = uuid4()
    atleta_a = uuid4()
    atleta_b = uuid4()

    await _append_overall(
        store,
        torneo_id,
        [
            {
                "posicion": 1,
                "atleta_id": str(atleta_a),
                "puntaje": 3,
                "detalle": {"STA": 1, "DNF": 2},
                "en_podio": True,
            },
            {
                "posicion": 2,
                "atleta_id": str(atleta_b),
                "puntaje": 4,
                "detalle": {"STA": 2, "DNF": 2},
                "en_podio": True,
            },
        ],
    )

    handler = ObtenerOverallHandler(store)
    entries = await handler.handle(ObtenerOverallQuery(torneo_id=torneo_id))

    assert len(entries) == 2
    assert entries[0].detalle == {"STA": 1, "DNF": 2}
    assert entries[0].en_podio is True
