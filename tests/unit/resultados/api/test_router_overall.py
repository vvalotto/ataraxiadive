"""Tests HTTP del router de resultados para Overall — US-3.5.3."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from resultados.api.router import (
    get_ranking_store,
    router,
)
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore


def _build_app(store: SQLiteEventStore) -> TestClient:
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_ranking_store] = lambda: store
    return TestClient(app)


def test_get_overall_devuelve_calculado_false_sin_eventos(tmp_path) -> None:
    db_path = tmp_path / "resultados.db"
    store = SQLiteEventStore(str(db_path))
    from tests.integration.resultados.test_obtener_overall_integration import _init_db

    import asyncio

    asyncio.run(_init_db(str(db_path)))
    client = _build_app(store)
    torneo_id = uuid4()

    response = client.get(f"/resultados/{torneo_id}/overall")

    assert response.status_code == 200
    assert response.json() == {
        "torneo_id": str(torneo_id),
        "total": 0,
        "calculado": False,
        "ranking": [],
    }


def test_get_overall_devuelve_detalle_y_podio(tmp_path) -> None:
    db_path = tmp_path / "resultados.db"
    store = SQLiteEventStore(str(db_path))
    from tests.integration.resultados.test_obtener_overall_integration import (
        _append_overall,
        _init_db,
    )

    import asyncio

    asyncio.run(_init_db(str(db_path)))
    torneo_id = uuid4()
    atleta_id = uuid4()
    asyncio.run(
        _append_overall(
            store,
            torneo_id,
            [
                {
                    "posicion": 1,
                    "atleta_id": str(atleta_id),
                    "puntaje": 3,
                    "detalle": {"STA": 1, "DNF": 2},
                    "en_podio": True,
                }
            ],
        )
    )
    client = _build_app(store)

    response = client.get(f"/resultados/{torneo_id}/overall")

    assert response.status_code == 200
    assert response.json() == {
        "torneo_id": str(torneo_id),
        "total": 1,
        "calculado": True,
        "ranking": [
            {
                "posicion": 1,
                "atleta_id": str(atleta_id),
                "puntaje": 3,
                "detalle": {"STA": 1, "DNF": 2},
                "en_podio": True,
            }
        ],
    }
