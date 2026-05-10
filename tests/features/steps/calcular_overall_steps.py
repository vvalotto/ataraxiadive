"""Step definitions BDD — US-3.5.1: Calcular Overall."""

from __future__ import annotations

import asyncio
import tempfile
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from resultados.domain.aggregates.ranking_overall import RankingOverall
from resultados.domain.exceptions import DisciplinasNoFinalizadas
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

scenarios("../US-3.5.1-ranking-overall.feature")
scenarios("../US-6.4.2-proyeccion-overall.feature")

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

_CATEGORIA = "SENIOR_MASCULINO"


async def _init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _append_competencia(ctx: dict, disciplina: Disciplina) -> UUID:
    competencia_id = uuid4()
    await ctx["competencia_store"].append(
        stream_id=f"competencia-{competencia_id}",
        event_type="IntervaloOTConfigurado",
        payload={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "intervalo_minutos": 3,
            "configurado_por": "organizador",
            "torneo_id": str(ctx["torneo_id"]),
            "occurred_at": "2026-04-02T12:00:00+00:00",
        },
    )
    await ctx["competencias_por_torneo"].guardar(
        competencia_id,
        disciplina.value,
        ctx["torneo_id"],
    )
    return competencia_id


async def _append_ranking(
    ctx: dict, competencia_id: UUID, disciplina: Disciplina, entries: list[dict]
) -> None:
    await ctx["ranking_store"].append(
        stream_id=f"ranking-{competencia_id}-{disciplina.value}",
        event_type="ResultadosCalculados",
        payload={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "total": len(entries),
            "entries": entries,
            "calculado_en": "2026-04-02T12:05:00+00:00",
            "occurred_at": "2026-04-02T12:05:00+00:00",
        },
    )


def _entry(atleta_id: UUID, posicion: int, rp: str, unidad: str, puntos: str) -> dict:
    return {
        "posicion": posicion,
        "atleta_id": str(atleta_id),
        "categoria": _CATEGORIA,
        "rp": rp,
        "unidad": unidad,
        "tarjeta": "Blanca",
        "es_dns": False,
        "en_podio": posicion <= 3,
        "puntos": puntos,
    }


@pytest.fixture
def ctx() -> dict:
    async def _build() -> dict:
        competencia_dir = tempfile.mkdtemp()
        resultados_dir = tempfile.mkdtemp()
        competencia_db = competencia_dir + "/competencia.db"
        resultados_db = resultados_dir + "/resultados.db"
        await _init_db(competencia_db)
        await _init_db(resultados_db)
        return {
            "torneo_id": uuid4(),
            "competencia_store": SQLiteEventStore(competencia_db),
            "competencias_por_torneo": SQLiteCompetenciasPorTorneo(competencia_db),
            "ranking_store": SQLiteEventStore(resultados_db),
            "athletes": {"A": uuid4(), "B": uuid4(), "C": uuid4()},
            "exc": None,
        }

    return asyncio.run(_build())


@given("rankings del torneo con STA: A=1, B=2, C=3")
def given_sta_abc(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = await _append_competencia(ctx, Disciplina.STA)
        ctx["competencia_sta"] = competencia_id
        await _append_ranking(
            ctx,
            competencia_id,
            Disciplina.STA,
            [
                _entry(ctx["athletes"]["A"], 1, "310", "Segundos", "20.00"),
                _entry(ctx["athletes"]["B"], 2, "300", "Segundos", "10.00"),
                _entry(ctx["athletes"]["C"], 3, "280", "Segundos", "5.00"),
            ],
        )

    asyncio.run(_run())


@given("rankings del torneo con DNF: A=2, B=1, C=3")
def given_dnf_abc(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = await _append_competencia(ctx, Disciplina.DNF)
        ctx["competencia_dnf"] = competencia_id
        await _append_ranking(
            ctx,
            competencia_id,
            Disciplina.DNF,
            [
                _entry(ctx["athletes"]["A"], 2, "80", "Metros", "10.00"),
                _entry(ctx["athletes"]["B"], 1, "90", "Metros", "20.00"),
                _entry(ctx["athletes"]["C"], 3, "70", "Metros", "5.00"),
            ],
        )

    asyncio.run(_run())


@given("rankings del torneo con STA: A=1, B=2")
def given_sta_ab(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = await _append_competencia(ctx, Disciplina.STA)
        ctx["competencia_sta"] = competencia_id
        await _append_ranking(
            ctx,
            competencia_id,
            Disciplina.STA,
            [
                _entry(ctx["athletes"]["A"], 1, "310", "Segundos", "20.00"),
                _entry(ctx["athletes"]["B"], 2, "300", "Segundos", "10.00"),
            ],
        )

    asyncio.run(_run())


@given("rankings del torneo con DNF: solo B participa con posicion 1")
def given_dnf_only_b(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = await _append_competencia(ctx, Disciplina.DNF)
        ctx["competencia_dnf"] = competencia_id
        await _append_ranking(
            ctx,
            competencia_id,
            Disciplina.DNF,
            [
                _entry(ctx["athletes"]["B"], 1, "90", "Metros", "10.00"),
            ],
        )

    asyncio.run(_run())


@given("la disciplina DNF del torneo aun no tiene ranking calculado")
def given_dnf_sin_ranking(ctx: dict) -> None:
    async def _run() -> None:
        ctx["competencia_dnf"] = await _append_competencia(ctx, Disciplina.DNF)

    asyncio.run(_run())


@given("un torneo sin rankings calculados")
def given_torneo_sin_rankings(ctx: dict) -> None:
    async def _run() -> None:
        await _append_competencia(ctx, Disciplina.STA)

    asyncio.run(_run())


@given("un torneo con competencias registradas en la proyeccion competencias_por_torneo")
def given_competencias_en_proyeccion(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = await _append_competencia(ctx, Disciplina.STA)
        ctx["competencia_sta"] = competencia_id
        await _append_ranking(
            ctx,
            competencia_id,
            Disciplina.STA,
            [_entry(ctx["athletes"]["A"], 1, "310", "Segundos", "20.00")],
        )
        ctx["competencias_por_torneo"].listar_por_torneo = AsyncMock(
            wraps=ctx["competencias_por_torneo"].listar_por_torneo
        )
        ctx["competencia_store"].load_all_streams_with_prefix = AsyncMock()

    asyncio.run(_run())


@given("un torneo con competencias finalizadas y rankings calculados por disciplina")
def given_competencias_finalizadas_con_rankings(ctx: dict) -> None:
    given_sta_abc(ctx)
    given_dnf_abc(ctx)


@given("un torneo sin competencias registradas en la proyeccion competencias_por_torneo")
def given_torneo_sin_competencias_materializadas(ctx: dict) -> None:
    ctx["competencias_por_torneo"].listar_por_torneo = AsyncMock(
        wraps=ctx["competencias_por_torneo"].listar_por_torneo
    )


@given("rankings del torneo con DNF: A=2, B=1")
def given_dnf_ab(ctx: dict) -> None:
    async def _run() -> None:
        competencia_id = await _append_competencia(ctx, Disciplina.DNF)
        ctx["competencia_dnf"] = competencia_id
        await _append_ranking(
            ctx,
            competencia_id,
            Disciplina.DNF,
            [
                _entry(ctx["athletes"]["A"], 2, "80", "Metros", "10.00"),
                _entry(ctx["athletes"]["B"], 1, "90", "Metros", "20.00"),
            ],
        )

    asyncio.run(_run())


@when("el sistema calcula el overall del torneo")
def when_calcula_overall(ctx: dict) -> None:
    async def _run() -> None:
        try:
            handler = CalcularOverallHandler(
                ctx["ranking_store"],
                ctx["competencias_por_torneo"],
            )
            await handler.handle(
                CalcularOverallCommand(
                    torneo_id=ctx["torneo_id"],
                    disciplinas=[Disciplina.STA, Disciplina.DNF],
                )
            )
            events = await ctx["ranking_store"].load(f"ranking-overall-{ctx['torneo_id']}")
            ctx["overall"] = RankingOverall.reconstitute(ctx["torneo_id"], events)
        except DisciplinasNoFinalizadas as exc:
            ctx["exc"] = exc

    asyncio.run(_run())


@when("el sistema calcula el overall solo con STA")
def when_calcula_overall_solo_sta(ctx: dict) -> None:
    async def _run() -> None:
        handler = CalcularOverallHandler(
            ctx["ranking_store"],
            ctx["competencias_por_torneo"],
        )
        await handler.handle(
            CalcularOverallCommand(
                torneo_id=ctx["torneo_id"],
                disciplinas=[Disciplina.STA],
            )
        )
        events = await ctx["ranking_store"].load(f"ranking-overall-{ctx['torneo_id']}")
        ctx["overall"] = RankingOverall.reconstitute(ctx["torneo_id"], events)

    asyncio.run(_run())


@when("se ejecuta CalcularOverallCommand para ese torneo")
def when_ejecuta_calcular_overall_para_torneo(ctx: dict) -> None:
    async def _run() -> None:
        handler = CalcularOverallHandler(
            ctx["ranking_store"],
            ctx["competencias_por_torneo"],
        )
        ctx["entries"] = await handler.handle(
            CalcularOverallCommand(
                torneo_id=ctx["torneo_id"],
                disciplinas=[Disciplina.STA, Disciplina.DNF],
            )
        )
        events = await ctx["ranking_store"].load(f"ranking-overall-{ctx['torneo_id']}")
        ctx["overall"] = RankingOverall.reconstitute(ctx["torneo_id"], events)

    asyncio.run(_run())


@when("se ejecuta CalcularOverallCommand usando la proyeccion materializada")
def when_ejecuta_calcular_overall_con_proyeccion(ctx: dict) -> None:
    when_ejecuta_calcular_overall_para_torneo(ctx)


@then("el handler consulta competencias_por_torneo.listar_por_torneo una sola vez")
def then_consulta_proyeccion_una_vez(ctx: dict) -> None:
    ctx["competencias_por_torneo"].listar_por_torneo.assert_awaited_once_with(ctx["torneo_id"])


@then("no llama a load_all_streams_with_prefix sobre el event store de competencia")
def then_no_escanea_event_store_competencia(ctx: dict) -> None:
    ctx["competencia_store"].load_all_streams_with_prefix.assert_not_called()


@then("los entries del ranking overall conservan puntajes y posiciones esperadas")
def then_entries_overall_esperados(ctx: dict) -> None:
    by_id = {entry.atleta_id: entry for entry in ctx["overall"].entries}
    assert by_id[ctx["athletes"]["A"]].puntos_overall == 30
    assert by_id[ctx["athletes"]["A"]].posicion == 1
    assert by_id[ctx["athletes"]["B"]].puntos_overall == 30
    assert by_id[ctx["athletes"]["B"]].posicion == 1
    assert by_id[ctx["athletes"]["C"]].puntos_overall == 10
    assert by_id[ctx["athletes"]["C"]].posicion == 3


@then("el handler retorna una lista vacia")
def then_retorna_lista_vacia(ctx: dict) -> None:
    assert ctx["entries"] == []


@then("no persiste un evento RankingOverallCalculado")
def then_no_persiste_ranking_overall(ctx: dict) -> None:
    assert ctx["overall"].entries == []


@then(parsers.parse("{atleta} tiene puntaje overall {puntaje:d} y posicion {posicion:d}"))
def then_puntaje_posicion(ctx: dict, atleta: str, puntaje: int, posicion: int) -> None:
    entry = next(
        entry for entry in ctx["overall"].entries if entry.atleta_id == ctx["athletes"][atleta]
    )
    assert entry.puntos_overall == puntaje
    assert entry.posicion == posicion


@then("A y B tienen en_podio overall igual a True")
def then_a_b_podio(ctx: dict) -> None:
    atleta_a = next(
        entry for entry in ctx["overall"].entries if entry.atleta_id == ctx["athletes"]["A"]
    )
    atleta_b = next(
        entry for entry in ctx["overall"].entries if entry.atleta_id == ctx["athletes"]["B"]
    )
    assert atleta_a.en_podio is True
    assert atleta_b.en_podio is True


@then("A recibe penalizacion por ausencia en DNF")
def then_a_penalizado(ctx: dict) -> None:
    atleta_a = next(
        entry for entry in ctx["overall"].entries if entry.atleta_id == ctx["athletes"]["A"]
    )
    assert "DNF" not in atleta_a.detalle


@then("el overall se calcula solo con STA")
def then_solo_sta(ctx: dict) -> None:
    for entry in ctx["overall"].entries:
        assert list(entry.detalle) == ["STA"]


@then("el sistema rechaza con DisciplinasNoFinalizadas")
def then_disciplinas_no_finalizadas(ctx: dict) -> None:
    assert isinstance(ctx["exc"], DisciplinasNoFinalizadas)


@then("A y B tienen la misma posicion overall")
def then_empate_posicion(ctx: dict) -> None:
    atleta_a = next(
        entry for entry in ctx["overall"].entries if entry.atleta_id == ctx["athletes"]["A"]
    )
    atleta_b = next(
        entry for entry in ctx["overall"].entries if entry.atleta_id == ctx["athletes"]["B"]
    )
    assert atleta_a.posicion == atleta_b.posicion


@then("no existe entrada overall con posicion 2")
def then_no_posicion_2(ctx: dict) -> None:
    assert all(entry.posicion != 2 for entry in ctx["overall"].entries)
