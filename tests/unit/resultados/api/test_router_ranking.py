"""Tests HTTP del router de resultados para Ranking por categoría."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from registro.domain.value_objects.categoria import Categoria
from resultados.api.router import get_ranking_store, router
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


def _build_app(store: SQLiteEventStore) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_ranking_store] = lambda: store
    return TestClient(app)


async def _init_db(db_path: str) -> None:
    import aiosqlite

    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _append_ranking(
    store: SQLiteEventStore,
    competencia_id,
    disciplina: str,
    entries: list[dict],
) -> None:
    await store.append(
        stream_id=f"ranking-{competencia_id}-{disciplina}",
        event_type="ResultadosCalculados",
        payload={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina,
            "total": len(entries),
            "entries": entries,
            "calculado_en": "2026-04-03T12:00:00+00:00",
            "occurred_at": "2026-04-03T12:00:00+00:00",
        },
    )


def test_get_ranking_devuelve_agrupado_por_categoria(tmp_path) -> None:
    import asyncio

    db_path = tmp_path / "resultados.db"
    store = SQLiteEventStore(str(db_path))
    asyncio.run(_init_db(str(db_path)))
    competencia_id = uuid4()
    atleta_sf = uuid4()
    atleta_mm = uuid4()
    asyncio.run(
        _append_ranking(
            store,
            competencia_id,
            "STA",
            [
                {
                    "posicion": 1,
                    "atleta_id": str(atleta_sf),
                    "categoria": Categoria.SENIOR_FEMENINO.value,
                    "rp": "277",
                    "unidad": "Segundos",
                    "tarjeta": "Blanca",
                    "es_dns": False,
                    "en_podio": True,
                },
                {
                    "posicion": 1,
                    "atleta_id": str(atleta_mm),
                    "categoria": Categoria.MASTER_MASCULINO.value,
                    "rp": "196",
                    "unidad": "Segundos",
                    "tarjeta": "Blanca",
                    "es_dns": False,
                    "en_podio": True,
                },
            ],
        )
    )
    client = _build_app(store)

    response = client.get(f"/resultados/{competencia_id}/ranking?disciplina=STA")

    assert response.status_code == 200
    assert response.json() == {
        "calculado": True,
        "rankings": [
            {
                "categoria": Categoria.MASTER_MASCULINO.value,
                "entradas": [
                    {
                        "posicion": 1,
                        "atleta_id": str(atleta_mm),
                        "rp": "196",
                        "unidad": "Segundos",
                        "tarjeta": "Blanca",
                        "es_dns": False,
                        "en_podio": True,
                    }
                ],
            },
            {
                "categoria": Categoria.SENIOR_FEMENINO.value,
                "entradas": [
                    {
                        "posicion": 1,
                        "atleta_id": str(atleta_sf),
                        "rp": "277",
                        "unidad": "Segundos",
                        "tarjeta": "Blanca",
                        "es_dns": False,
                        "en_podio": True,
                    }
                ],
            },
        ],
    }
