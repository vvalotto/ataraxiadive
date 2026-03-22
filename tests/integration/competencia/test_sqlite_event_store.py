"""Tests de integración — SQLiteEventStore sobre SQLite in-memory."""
from __future__ import annotations

import pytest
import aiosqlite

from competencia.infrastructure.event_store.sqlite_event_store import (
    ConcurrencyError,
    SQLiteEventStore,
)

STREAM_ID = "performance-test-001"


@pytest.fixture
async def store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    """EventStore con SQLite in-memory inicializado con el schema de events."""
    db_path = str(tmp_path / "test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(
            """
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
        )
        await db.commit()
    return SQLiteEventStore(db_path)


async def test_append_y_load_un_evento(store: SQLiteEventStore) -> None:
    """Append de un evento y load retorna ese evento con versión 1."""
    await store.append(STREAM_ID, "APRegistrado", {"valor_ap": 60.0})

    eventos = await store.load(STREAM_ID)

    assert len(eventos) == 1
    assert eventos[0]["event_type"] == "APRegistrado"
    assert eventos[0]["payload"] == {"valor_ap": 60.0}
    assert eventos[0]["version"] == 1


async def test_append_multiples_eventos_version_incremental(
    store: SQLiteEventStore,
) -> None:
    """Múltiples appends incrementan la versión secuencialmente."""
    await store.append(STREAM_ID, "APRegistrado", {"valor_ap": 60.0})
    await store.append(STREAM_ID, "AtletaLlamado", {})
    await store.append(STREAM_ID, "ResultadoRegistrado", {"valor_rp": 58.5})

    eventos = await store.load(STREAM_ID)

    assert len(eventos) == 3
    assert [e["version"] for e in eventos] == [1, 2, 3]
    assert [e["event_type"] for e in eventos] == [
        "APRegistrado",
        "AtletaLlamado",
        "ResultadoRegistrado",
    ]


async def test_load_from_version(store: SQLiteEventStore) -> None:
    """load_from retorna solo los eventos desde la versión indicada."""
    await store.append(STREAM_ID, "APRegistrado", {"valor_ap": 60.0})
    await store.append(STREAM_ID, "AtletaLlamado", {})
    await store.append(STREAM_ID, "ResultadoRegistrado", {"valor_rp": 58.5})

    eventos = await store.load_from(STREAM_ID, from_version=2)

    assert len(eventos) == 2
    assert eventos[0]["version"] == 2
    assert eventos[1]["version"] == 3


async def test_load_stream_inexistente_retorna_lista_vacia(
    store: SQLiteEventStore,
) -> None:
    """load de un stream que no existe retorna lista vacía."""
    eventos = await store.load("stream-que-no-existe")
    assert eventos == []


async def test_streams_distintos_son_independientes(store: SQLiteEventStore) -> None:
    """Eventos de streams distintos no se mezclan."""
    stream_a = "performance-A"
    stream_b = "performance-B"

    await store.append(stream_a, "APRegistrado", {"valor_ap": 60.0})
    await store.append(stream_b, "APRegistrado", {"valor_ap": 70.0})
    await store.append(stream_a, "AtletaLlamado", {})

    eventos_a = await store.load(stream_a)
    eventos_b = await store.load(stream_b)

    assert len(eventos_a) == 2
    assert len(eventos_b) == 1
    assert eventos_a[0]["version"] == 1
    assert eventos_b[0]["version"] == 1


async def test_concurrency_error_cuando_version_no_coincide(
    store: SQLiteEventStore,
) -> None:
    """append con expected_version incorrecto lanza ConcurrencyError."""
    await store.append(STREAM_ID, "APRegistrado", {"valor_ap": 60.0})

    with pytest.raises(ConcurrencyError):
        await store.append(
            STREAM_ID, "AtletaLlamado", {}, expected_version=0
        )


async def test_append_con_expected_version_correcto(store: SQLiteEventStore) -> None:
    """append con expected_version correcto (versión actual) procede sin error."""
    await store.append(STREAM_ID, "APRegistrado", {"valor_ap": 60.0})
    # versión actual = 1, expected_version = 1 → OK
    await store.append(
        STREAM_ID, "AtletaLlamado", {}, expected_version=1
    )

    eventos = await store.load(STREAM_ID)
    assert len(eventos) == 2
