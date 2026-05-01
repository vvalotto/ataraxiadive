"""Tests de integración del cálculo overall — US-3.5.1 / US-5.6.4."""

from __future__ import annotations

import tempfile
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest

from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from resultados.domain.aggregates.ranking_overall import RankingOverall
from resultados.domain.exceptions import DisciplinasNoFinalizadas
from shared.domain.value_objects.disciplina import Disciplina
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


async def _append_competencia(
    store: SQLiteEventStore, competencia_id, torneo_id, disciplina: Disciplina
) -> None:
    await store.append(
        stream_id=f"competencia-{competencia_id}",
        event_type="IntervaloOTConfigurado",
        payload={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "intervalo_minutos": 3,
            "configurado_por": "organizador",
            "torneo_id": str(torneo_id),
            "occurred_at": "2026-04-02T12:00:00+00:00",
        },
    )


async def _append_ranking(
    store: SQLiteEventStore, competencia_id, disciplina: Disciplina, entries: list[dict]
) -> None:
    await store.append(
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


def _ranking_entry(atleta_id, posicion: int, puntos: str) -> dict:
    return {
        "posicion": posicion,
        "atleta_id": str(atleta_id),
        "rp": "300",
        "unidad": "Segundos",
        "tarjeta": "Blanca",
        "es_dns": False,
        "en_podio": posicion <= 3,
        "puntos": puntos,
    }


@pytest.mark.asyncio
async def test_calcular_overall_persiste_y_reconstituye() -> None:
    """Overall suma puntos FAAS de cada disciplina y ordena DESC."""
    competencia_dir = tempfile.mkdtemp()
    resultados_dir = tempfile.mkdtemp()
    competencia_db = competencia_dir + "/competencia.db"
    resultados_db = resultados_dir + "/resultados.db"
    await _init_db(competencia_db)
    await _init_db(resultados_db)

    competencia_store = SQLiteEventStore(competencia_db)
    ranking_store = SQLiteEventStore(resultados_db)

    torneo_id = uuid4()
    competencia_sta = uuid4()
    competencia_dnf = uuid4()
    atleta_a = uuid4()
    atleta_b = uuid4()
    atleta_c = uuid4()

    await _append_competencia(competencia_store, competencia_sta, torneo_id, Disciplina.STA)
    await _append_competencia(competencia_store, competencia_dnf, torneo_id, Disciplina.DNF)

    # Atleta A: STA=100, DNF=80 → overall=180
    # Atleta B: STA=80, DNF=100 → overall=180 (empate)
    # Atleta C: STA=60, DNF=60 → overall=120
    await _append_ranking(
        ranking_store,
        competencia_sta,
        Disciplina.STA,
        [
            _ranking_entry(atleta_a, 1, "100.00"),
            _ranking_entry(atleta_b, 2, "80.00"),
            _ranking_entry(atleta_c, 3, "60.00"),
        ],
    )
    await _append_ranking(
        ranking_store,
        competencia_dnf,
        Disciplina.DNF,
        [
            _ranking_entry(atleta_b, 1, "100.00"),
            _ranking_entry(atleta_a, 2, "80.00"),
            _ranking_entry(atleta_c, 3, "60.00"),
        ],
    )

    handler = CalcularOverallHandler(ranking_store, competencia_store)
    await handler.handle(
        CalcularOverallCommand(torneo_id=torneo_id, disciplinas=[Disciplina.STA, Disciplina.DNF])
    )

    events = await ranking_store.load(f"ranking-overall-{torneo_id}")
    overall = RankingOverall.reconstitute(torneo_id, events)

    assert len(overall.entries) == 3
    by_id = {e.atleta_id: e for e in overall.entries}
    assert by_id[atleta_a].puntos_overall == Decimal("180.00")
    assert by_id[atleta_a].posicion == 1
    assert by_id[atleta_b].puntos_overall == Decimal("180.00")
    assert by_id[atleta_b].posicion == 1
    assert by_id[atleta_c].puntos_overall == Decimal("120.00")
    assert by_id[atleta_c].posicion == 3


@pytest.mark.asyncio
async def test_calcular_overall_rechaza_si_falta_ranking_de_disciplina() -> None:
    """INV-5.6.4-04: rechaza si alguna disciplina no tiene ranking calculado."""
    competencia_dir = tempfile.mkdtemp()
    resultados_dir = tempfile.mkdtemp()
    await _init_db(competencia_dir + "/comp.db")
    await _init_db(resultados_dir + "/res.db")

    competencia_store = SQLiteEventStore(competencia_dir + "/comp.db")
    ranking_store = SQLiteEventStore(resultados_dir + "/res.db")

    torneo_id = uuid4()
    competencia_sta = uuid4()
    competencia_dnf = uuid4()
    atleta_a = uuid4()

    await _append_competencia(competencia_store, competencia_sta, torneo_id, Disciplina.STA)
    await _append_competencia(competencia_store, competencia_dnf, torneo_id, Disciplina.DNF)
    await _append_ranking(
        ranking_store,
        competencia_sta,
        Disciplina.STA,
        [_ranking_entry(atleta_a, 1, "100.00")],
    )
    # DNF no tiene ranking calculado

    handler = CalcularOverallHandler(ranking_store, competencia_store)

    with pytest.raises(DisciplinasNoFinalizadas):
        await handler.handle(
            CalcularOverallCommand(
                torneo_id=torneo_id, disciplinas=[Disciplina.STA, Disciplina.DNF]
            )
        )
