"""Integracion de P-09 en composition root — US-3.5.2."""

from __future__ import annotations

from datetime import date
from uuid import uuid4

import aiosqlite
import pytest

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


async def _append_competencia(
    store: SQLiteEventStore,
    competencia_id,
    torneo_id,
    disciplina: Disciplina,
) -> None:
    stream_id = f"competencia-{competencia_id}"
    await store.append(
        stream_id=stream_id,
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
    await SQLiteCompetenciasPorTorneo().guardar(competencia_id, disciplina.value, torneo_id)
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


async def _append_ranking(
    store: SQLiteEventStore,
    competencia_id,
    disciplina: Disciplina,
    atleta_a,
    atleta_b,
    pos_a: int,
    pos_b: int,
) -> None:
    unidad = "Segundos" if disciplina == Disciplina.STA else "Metros"
    await store.append(
        stream_id=f"ranking-{competencia_id}-{disciplina.value}",
        event_type="ResultadosCalculados",
        payload={
            "competencia_id": str(competencia_id),
            "disciplina": disciplina.value,
            "total": 2,
            "entries": [
                {
                    "posicion": pos_a,
                    "atleta_id": str(atleta_a),
                    "rp": "300",
                    "unidad": unidad,
                    "tarjeta": "Blanca",
                    "es_dns": False,
                    "en_podio": True,
                },
                {
                    "posicion": pos_b,
                    "atleta_id": str(atleta_b),
                    "rp": "290",
                    "unidad": unidad,
                    "tarjeta": "Blanca",
                    "es_dns": False,
                    "en_podio": True,
                },
            ],
            "calculado_en": "2026-04-02T12:05:00+00:00",
            "occurred_at": "2026-04-02T12:05:00+00:00",
        },
    )


@pytest.mark.asyncio
async def test_callback_persiste_overall_cuando_finaliza_ultima_disciplina(
    tmp_path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    competencia_db = str(tmp_path / "competencia.db")
    resultados_db = str(tmp_path / "resultados.db")
    torneo_db = str(tmp_path / "torneo.db")
    await _init_event_db(competencia_db)
    await _init_event_db(resultados_db)
    monkeypatch.setenv("RESULTADOS_DB_PATH", resultados_db)
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)
    monkeypatch.setenv("COMPETENCIA_DB_PATH", competencia_db)

    competencia_store = SQLiteEventStore(competencia_db)
    ranking_store = SQLiteEventStore(resultados_db)
    torneo_repo = SQLiteTorneoRepository(torneo_db)

    torneo_id = uuid4()
    competencia_sta = uuid4()
    competencia_dnf = uuid4()
    atleta_a = uuid4()
    atleta_b = uuid4()

    torneo = Torneo(
        torneo_id=torneo_id,
        nombre="Torneo test",
        descripcion="US-3.5.2",
        fecha_inicio=date(2026, 4, 2),
        fecha_fin=date(2026, 4, 3),
        sede=Sede(nombre="Piscina", ciudad="Cordoba", pais="AR"),
        entidad_organizadora=EntidadOrganizadora(nombre="AIDA", tipo="FEDERACION"),
    )
    torneo.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF}))
    await torneo_repo.save(torneo)

    await _append_competencia(competencia_store, competencia_sta, torneo_id, Disciplina.STA)
    await _append_competencia(competencia_store, competencia_dnf, torneo_id, Disciplina.DNF)
    await _append_ranking(
        ranking_store, competencia_sta, Disciplina.STA, atleta_a, atleta_b, 1, 2
    )

    class FakeRankingHandler:
        def __init__(self, *_args) -> None:
            pass

        async def handle(self, command) -> None:
            await _append_ranking(
                ranking_store,
                command.competencia_id,
                command.disciplina,
                atleta_a,
                atleta_b,
                2,
                1,
            )

    monkeypatch.setattr(app_module, "CalcularRankingHandler", FakeRankingHandler)

    callback = app_module.build_on_finalizada_callback(competencia_store)
    await callback(competencia_dnf, Disciplina.DNF, torneo_id)

    events = await ranking_store.load(f"ranking-overall-{torneo_id}")
    assert len(events) == 1
    assert events[0]["event_type"] == "RankingOverallCalculado"
