"""Tests unitarios de SQLiteEventStore.load_all_streams_with_prefix."""

from __future__ import annotations

import tempfile
import os
from pathlib import Path
import pytest
import pytest_asyncio

from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from alembic.config import Config
from alembic import command

_PROJECT_ROOT = Path(__file__).parents[4]


def run_migrations(db_path: str) -> None:
    alembic_cfg = Config(str(_PROJECT_ROOT / "alembic.ini"))
    alembic_cfg.set_main_option("sqlalchemy.url", f"sqlite:///{db_path}")
    command.upgrade(alembic_cfg, "head")


@pytest_asyncio.fixture
async def store() -> SQLiteEventStore:
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "test.db")
        run_migrations(db_path)
        yield SQLiteEventStore(db_path)


@pytest.mark.asyncio
async def test_load_all_streams_retorna_streams_del_prefijo(store: SQLiteEventStore) -> None:
    await store.append("performance-C001-P001-DNF", "APRegistrado", {"v": "1"})
    await store.append("performance-C001-P001-DNF", "AtletaLlamado", {"v": "2"})
    await store.append("performance-C001-P002-DNF", "APRegistrado", {"v": "3"})

    streams = await store.load_all_streams_with_prefix("performance-C001-")

    assert len(streams) == 2
    stream_sizes = sorted(len(s) for s in streams)
    assert stream_sizes == [1, 2]


@pytest.mark.asyncio
async def test_load_all_streams_no_incluye_otra_competencia(store: SQLiteEventStore) -> None:
    await store.append("performance-C001-P001-DNF", "APRegistrado", {"v": "1"})
    await store.append("performance-C002-P001-DNF", "APRegistrado", {"v": "2"})

    streams = await store.load_all_streams_with_prefix("performance-C001-")

    assert len(streams) == 1
    assert streams[0][0]["payload"]["v"] == "1"


@pytest.mark.asyncio
async def test_load_all_streams_competencia_sin_performances(store: SQLiteEventStore) -> None:
    streams = await store.load_all_streams_with_prefix("performance-C999-")

    assert streams == []


@pytest.mark.asyncio
async def test_load_all_streams_eventos_ordenados_por_version(store: SQLiteEventStore) -> None:
    await store.append("performance-C001-P001-DNF", "APRegistrado", {"seq": 1})
    await store.append("performance-C001-P001-DNF", "AtletaLlamado", {"seq": 2})
    await store.append("performance-C001-P001-DNF", "ResultadoRegistrado", {"seq": 3})

    streams = await store.load_all_streams_with_prefix("performance-C001-")

    assert len(streams) == 1
    event_types = [e["event_type"] for e in streams[0]]
    assert event_types == ["APRegistrado", "AtletaLlamado", "ResultadoRegistrado"]
