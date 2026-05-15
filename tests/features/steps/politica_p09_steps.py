"""Step definitions BDD — US-3.5.2: Politica P-09."""

from __future__ import annotations

import asyncio
from datetime import date
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, scenarios, then, when

import app as app_module
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

scenarios("../US-3.5.2-politica-p09.feature")

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


async def _init_event_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _seed_torneo(
    repo: SQLiteTorneoRepository, torneo_id, disciplinas: set[Disciplina]
) -> None:
    torneo = Torneo(
        torneo_id=torneo_id,
        nombre="Torneo test",
        descripcion="US-3.5.2",
        fecha_inicio=date(2026, 4, 2),
        fecha_fin=date(2026, 4, 3),
        sede=Sede(nombre="Piscina", ciudad="Cordoba", pais="AR"),
        entidad_organizadora=EntidadOrganizadora(nombre="AIDA", tipo="FEDERACION"),
    )
    torneo.asignar_disciplinas(frozenset(disciplinas))
    await repo.save(torneo)


async def _append_competencia(
    store: SQLiteEventStore,
    competencia_id,
    torneo_id,
    disciplina: Disciplina,
    finalizada: bool,
) -> None:
    stream_id = f"competencia-{competencia_id}"
    payload = {
        "competencia_id": str(competencia_id),
        "disciplina": disciplina.value,
        "intervalo_minutos": 3,
        "configurado_por": "organizador",
        "torneo_id": str(torneo_id) if torneo_id else None,
        "occurred_at": "2026-04-02T12:00:00+00:00",
    }
    await store.append(stream_id=stream_id, event_type="IntervaloOTConfigurado", payload=payload)
    if torneo_id is not None:
        await SQLiteCompetenciasPorTorneo().guardar(competencia_id, disciplina.value, torneo_id)
    if finalizada:
        await store.append(
            stream_id=stream_id,
            event_type="CompetenciaFinalizada",
            payload={
                "competencia_id": str(competencia_id),
                "disciplina": disciplina.value,
                "total_performances": 2,
                "ejecutadas": 2,
                "dns_count": 0,
                "occurred_at": "2026-04-02T12:10:00+00:00",
            },
        )


async def _append_finalizacion(
    store: SQLiteEventStore, competencia_id, disciplina: Disciplina
) -> None:
    await store.append(
        stream_id=f"competencia-{competencia_id}",
        event_type="CompetenciaFinalizada",
        payload={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "total_performances": 2,
            "ejecutadas": 2,
            "dns_count": 0,
            "occurred_at": "2026-04-02T12:10:00+00:00",
        },
    )


@pytest.fixture
def ctx(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    async def _build() -> dict:
        competencia_db = str(tmp_path / "competencia.db")
        resultados_db = str(tmp_path / "resultados.db")
        torneo_db = str(tmp_path / "torneo.db")
        await _init_event_db(competencia_db)
        await _init_event_db(resultados_db)
        monkeypatch.setenv("RESULTADOS_DB_PATH", resultados_db)
        monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)
        monkeypatch.setenv("COMPETENCIA_DB_PATH", competencia_db)
        return {
            "torneo_id": uuid4(),
            "competencia_store": SQLiteEventStore(competencia_db),
            "torneo_repo": SQLiteTorneoRepository(torneo_db),
            "competencias": {},
            "llamadas": [],
            "overall_existente": False,
        }

    class FakeRankingHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, command) -> None:
            ctx_data["llamadas"].append(("ranking", command.disciplina.value))

    class FakeOverallHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, _command) -> None:
            if ctx_data["overall_existente"]:
                return
            ctx_data["llamadas"].append(("overall", "torneo"))
            ctx_data["overall_existente"] = True

    ctx_data = asyncio.run(_build())
    monkeypatch.setattr(app_module, "CalcularRankingHandler", FakeRankingHandler)
    monkeypatch.setattr(app_module, "CalcularOverallHandler", FakeOverallHandler)
    return ctx_data


@given("un torneo con una sola disciplina STA y competencia asociada")
def given_torneo_una_disciplina(ctx: dict) -> None:
    async def _run() -> None:
        await _seed_torneo(ctx["torneo_repo"], ctx["torneo_id"], {Disciplina.STA})
        competencia_id = uuid4()
        ctx["competencias"]["STA"] = competencia_id
        await _append_competencia(
            ctx["competencia_store"], competencia_id, ctx["torneo_id"], Disciplina.STA, True
        )

    asyncio.run(_run())


@given("un torneo con disciplinas STA y DNF")
def given_torneo_dos_disciplinas(ctx: dict) -> None:
    async def _run() -> None:
        await _seed_torneo(ctx["torneo_repo"], ctx["torneo_id"], {Disciplina.STA, Disciplina.DNF})
        competencia_sta = uuid4()
        competencia_dnf = uuid4()
        ctx["competencias"]["STA"] = competencia_sta
        ctx["competencias"]["DNF"] = competencia_dnf
        await _append_competencia(
            ctx["competencia_store"], competencia_sta, ctx["torneo_id"], Disciplina.STA, False
        )
        await _append_competencia(
            ctx["competencia_store"], competencia_dnf, ctx["torneo_id"], Disciplina.DNF, False
        )

    asyncio.run(_run())


@given("la disciplina DNF aun no finalizo")
def given_dnf_no_finalizo(ctx: dict) -> None:
    pass


@given("la disciplina STA ya finalizo con ranking calculado")
def given_sta_ya_finalizo(ctx: dict) -> None:
    async def _run() -> None:
        await _append_finalizacion(
            ctx["competencia_store"], ctx["competencias"]["STA"], Disciplina.STA
        )

    asyncio.run(_run())


@given("una competencia standalone sin torneo_id")
def given_competencia_standalone(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = uuid4()
        ctx["competencias"]["STA"] = competencia_id
        await _append_competencia(
            ctx["competencia_store"], competencia_id, None, Disciplina.STA, True
        )

    asyncio.run(_run())


@given("un torneo cuyo overall ya fue calculado")
def given_overall_ya_calculado(ctx: dict) -> None:
    asyncio.run(_seed_torneo(ctx["torneo_repo"], ctx["torneo_id"], {Disciplina.STA}))
    ctx["competencias"]["STA"] = uuid4()
    asyncio.run(
        _append_competencia(
            ctx["competencia_store"],
            ctx["competencias"]["STA"],
            ctx["torneo_id"],
            Disciplina.STA,
            True,
        )
    )
    ctx["llamadas"].append(("overall", "torneo"))
    ctx["overall_existente"] = True


@when("la competencia STA finaliza")
def when_finaliza_sta(ctx: dict) -> None:
    callback = app_module.build_on_finalizada_callback(ctx["competencia_store"])
    asyncio.run(callback(ctx["competencias"]["STA"], Disciplina.STA, ctx.get("torneo_id")))


@when("la competencia DNF finaliza")
def when_finaliza_dnf(ctx: dict) -> None:
    async def _run() -> None:
        await _append_finalizacion(
            ctx["competencia_store"], ctx["competencias"]["DNF"], Disciplina.DNF
        )
        callback = app_module.build_on_finalizada_callback(ctx["competencia_store"])
        await callback(ctx["competencias"]["DNF"], Disciplina.DNF, ctx["torneo_id"])

    asyncio.run(_run())


@when("la competencia finaliza")
def when_finaliza_standalone(ctx: dict) -> None:
    callback = app_module.build_on_finalizada_callback(ctx["competencia_store"])
    asyncio.run(callback(ctx["competencias"]["STA"], Disciplina.STA, None))


@when("se recibe otra finalizacion para una disciplina del mismo torneo")
def when_repite_finalizacion(ctx: dict) -> None:
    callback = app_module.build_on_finalizada_callback(ctx["competencia_store"])
    asyncio.run(callback(ctx["competencias"]["STA"], Disciplina.STA, ctx["torneo_id"]))


@then("P-08 calcula el ranking de STA")
def then_ranking_sta(ctx: dict) -> None:
    assert ("ranking", "STA") in ctx["llamadas"]


@then("P-08 calcula el ranking de DNF")
def then_ranking_dnf(ctx: dict) -> None:
    assert ("ranking", "DNF") in ctx["llamadas"]


@then("P-08 calcula el ranking de la competencia")
def then_ranking_competencia(ctx: dict) -> None:
    assert any(llamada[0] == "ranking" for llamada in ctx["llamadas"])


@then("P-09 calcula el overall del torneo")
def then_overall(ctx: dict) -> None:
    assert ("overall", "torneo") in ctx["llamadas"]


@then("P-09 no calcula el overall del torneo")
def then_no_overall(ctx: dict) -> None:
    assert ("overall", "torneo") not in ctx["llamadas"]


@then("P-09 no se activa")
def then_no_activa_p09(ctx: dict) -> None:
    assert ("overall", "torneo") not in ctx["llamadas"]


@then("no se persiste un segundo evento de ranking overall calculado")
def then_no_segundo_overall(ctx: dict) -> None:
    assert ctx["llamadas"].count(("overall", "torneo")) == 1
