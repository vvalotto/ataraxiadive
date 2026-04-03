"""Step definitions BDD — US-3.5.3: API Overall."""

from __future__ import annotations

import asyncio
from uuid import uuid4

import aiosqlite
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from pytest_bdd import given, scenarios, then, when

from resultados.api.router import get_ranking_store, router
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

scenarios("../US-3.5.3-api-overall.feature")

CREATE_EVENTS_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""


async def _init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _append_overall(
    store: SQLiteEventStore, torneo_id, entries: list[dict], disciplinas: list[str]
) -> None:
    await store.append(
        stream_id=f"ranking-overall-{torneo_id}",
        event_type="RankingOverallCalculado",
        payload={
            "torneo_id": str(torneo_id),
            "disciplinas": disciplinas,
            "total": len(entries),
            "entries": entries,
            "calculado_en": "2026-04-02T12:05:00+00:00",
            "occurred_at": "2026-04-02T12:05:00+00:00",
        },
    )


@pytest.fixture
def ctx(tmp_path) -> dict:
    db_path = tmp_path / "resultados.db"
    asyncio.run(_init_db(str(db_path)))
    store = SQLiteEventStore(str(db_path))
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_ranking_store] = lambda: store
    client = TestClient(app)
    return {
        "store": store,
        "client": client,
        "torneo_id": uuid4(),
        "response": None,
    }


@given("P-09 calculo el overall para un torneo con STA y DNF")
def given_overall_calculado(ctx: dict) -> None:
    torneo_id = ctx["torneo_id"]
    atletas = [uuid4() for _ in range(3)]
    asyncio.run(
        _append_overall(
            ctx["store"],
            torneo_id,
            [
                {
                    "posicion": 1,
                    "atleta_id": str(atletas[0]),
                    "puntaje": 3,
                    "detalle": {"STA": 1, "DNF": 2},
                    "en_podio": True,
                },
                {
                    "posicion": 2,
                    "atleta_id": str(atletas[1]),
                    "puntaje": 4,
                    "detalle": {"STA": 2, "DNF": 2},
                    "en_podio": True,
                },
                {
                    "posicion": 3,
                    "atleta_id": str(atletas[2]),
                    "puntaje": 5,
                    "detalle": {"STA": 3, "DNF": 2},
                    "en_podio": True,
                },
            ],
            ["STA", "DNF"],
        )
    )


@given("un torneo con disciplinas no finalizadas")
def given_torneo_sin_overall(ctx: dict) -> None:
    pass


@given("un overall calculado con 5 atletas")
def given_overall_con_cinco_atletas(ctx: dict) -> None:
    torneo_id = ctx["torneo_id"]
    atletas = [uuid4() for _ in range(5)]
    asyncio.run(
        _append_overall(
            ctx["store"],
            torneo_id,
            [
                {
                    "posicion": index + 1,
                    "atleta_id": str(atleta_id),
                    "puntaje": index + 3,
                    "detalle": {"STA": index + 1, "DNF": 2},
                    "en_podio": index < 3,
                }
                for index, atleta_id in enumerate(atletas)
            ],
            ["STA", "DNF"],
        )
    )


@when("consulto GET /resultados/{torneo_id}/overall")
def when_consulto_overall(ctx: dict) -> None:
    ctx["response"] = ctx["client"].get(f"/resultados/{ctx['torneo_id']}/overall")


@then("la respuesta es 200 con calculado true")
def then_calculado_true(ctx: dict) -> None:
    assert ctx["response"].status_code == 200
    assert ctx["response"].json()["calculado"] is True


@then("el ranking overall contiene entradas ordenadas por posicion")
def then_ordenado(ctx: dict) -> None:
    rankings = ctx["response"].json()["rankings"]
    for grupo in rankings:
        entradas = grupo["entradas"]
        assert [entry["posicion"] for entry in entradas] == sorted(
            entry["posicion"] for entry in entradas
        )


@then("la respuesta es 200 con calculado false")
def then_calculado_false(ctx: dict) -> None:
    assert ctx["response"].status_code == 200
    assert ctx["response"].json()["calculado"] is False


@then("el ranking overall es vacio")
def then_vacio(ctx: dict) -> None:
    payload = ctx["response"].json()
    assert payload["rankings"] == []


@then("cada entrada incluye detalle STA y DNF con sus posiciones")
def then_detalle_disciplina(ctx: dict) -> None:
    for grupo in ctx["response"].json()["rankings"]:
        for entry in grupo["entradas"]:
            assert "STA" in entry["detalle"]
            assert "DNF" in entry["detalle"]


@then("los puestos 1, 2 y 3 tienen en_podio true")
def then_podio_true(ctx: dict) -> None:
    for grupo in ctx["response"].json()["rankings"]:
        for entry in grupo["entradas"][:3]:
            assert entry["en_podio"] is True


@then("los demas puestos tienen en_podio false")
def then_podio_false(ctx: dict) -> None:
    for grupo in ctx["response"].json()["rankings"]:
        for entry in grupo["entradas"][3:]:
            assert entry["en_podio"] is False
