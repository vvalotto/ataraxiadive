"""Tests HTTP del router de resultados para Overall — US-3.5.3 / US-5.6.4."""

from __future__ import annotations

from uuid import uuid4

from fastapi import FastAPI
from fastapi.testclient import TestClient

from registro.domain.value_objects.categoria import Categoria
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
        "calculado": False,
        "rankings": [],
    }


def test_get_overall_devuelve_puntos_overall_y_detalle(tmp_path) -> None:
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
                    "categoria": Categoria.SENIOR_MASCULINO.value,
                    "puntos_overall": "175.00",
                    "detalle": {"DNF": "100.00", "STA": "75.00"},
                    "en_podio": True,
                }
            ],
        )
    )
    client = _build_app(store)

    response = client.get(f"/resultados/{torneo_id}/overall")

    assert response.status_code == 200
    assert response.json() == {
        "calculado": True,
        "rankings": [
            {
                "categoria": Categoria.SENIOR_MASCULINO.value,
                "entradas": [
                    {
                        "posicion": 1,
                        "atleta_id": str(atleta_id),
                        "puntos_overall": "175.00",
                        "detalle": {"DNF": "100.00", "STA": "75.00"},
                        "en_podio": True,
                    }
                ],
            }
        ],
    }
