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
    if torneo_id is not None:
        await SQLiteCompetenciasPorTorneo().guardar(competencia_id, disciplina.value, torneo_id)
    if finalizada:
        await store.append(
            stream_id=stream_id,
            event_type="CompetenciaFinalizada",
            payload={
                "competencia_id": str(competencia_id),
                "disciplina": disciplina.value,
                "total_performances": 1,
                "ejecutadas": 1,
                "dns_count": 0,
                "occurred_at": "2026-04-02T12:10:00+00:00",
            },
        )


@pytest.fixture
async def callback_ctx(tmp_path, monkeypatch: pytest.MonkeyPatch) -> dict:
    competencia_db = str(tmp_path / "competencia.db")
    resultados_db = str(tmp_path / "resultados.db")
    torneo_db = str(tmp_path / "torneo.db")
    await _init_event_db(competencia_db)
    await _init_event_db(resultados_db)
    monkeypatch.setenv("RESULTADOS_DB_PATH", resultados_db)
    monkeypatch.setenv("TORNEO_DB_PATH", torneo_db)
    monkeypatch.setenv("COMPETENCIA_DB_PATH", competencia_db)
    return {
        "competencia_store": SQLiteEventStore(competencia_db),
        "torneo_repo": SQLiteTorneoRepository(torneo_db),
    }


@pytest.mark.asyncio
async def test_callback_dispara_overall_si_todas_finalizaron(
    callback_ctx: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llamadas: list[tuple[str, object]] = []
    torneo_id = uuid4()
    competencia_sta = uuid4()
    competencia_dnf = uuid4()

    await _seed_torneo(callback_ctx["torneo_repo"], torneo_id, {Disciplina.STA, Disciplina.DNF})
    await _append_competencia(
        callback_ctx["competencia_store"], competencia_sta, torneo_id, Disciplina.STA, True
    )
    await _append_competencia(
        callback_ctx["competencia_store"], competencia_dnf, torneo_id, Disciplina.DNF, True
    )

    class FakeRankingHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, command) -> None:
            llamadas.append(("ranking", command.competencia_id))

    class FakeOverallHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, command) -> None:
            llamadas.append(("overall", command.torneo_id))

    monkeypatch.setattr(app_module, "CalcularRankingHandler", FakeRankingHandler)
    monkeypatch.setattr(app_module, "CalcularOverallHandler", FakeOverallHandler)

    callback = app_module.build_on_finalizada_callback(callback_ctx["competencia_store"])
    await callback(competencia_dnf, Disciplina.DNF, torneo_id)

    assert ("ranking", competencia_dnf) in llamadas
    assert ("overall", torneo_id) in llamadas


@pytest.mark.asyncio
async def test_callback_no_dispara_overall_si_falta_otra_disciplina(
    callback_ctx: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llamadas: list[str] = []
    torneo_id = uuid4()
    competencia_sta = uuid4()
    competencia_dnf = uuid4()

    await _seed_torneo(callback_ctx["torneo_repo"], torneo_id, {Disciplina.STA, Disciplina.DNF})
    await _append_competencia(
        callback_ctx["competencia_store"], competencia_sta, torneo_id, Disciplina.STA, True
    )
    await _append_competencia(
        callback_ctx["competencia_store"], competencia_dnf, torneo_id, Disciplina.DNF, False
    )

    class FakeRankingHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, _command) -> None:
            llamadas.append("ranking")

    class FakeOverallHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, _command) -> None:
            llamadas.append("overall")

    monkeypatch.setattr(app_module, "CalcularRankingHandler", FakeRankingHandler)
    monkeypatch.setattr(app_module, "CalcularOverallHandler", FakeOverallHandler)

    callback = app_module.build_on_finalizada_callback(callback_ctx["competencia_store"])
    await callback(competencia_sta, Disciplina.STA, torneo_id)

    assert llamadas == ["ranking"]


@pytest.mark.asyncio
async def test_callback_standalone_no_activa_p09(
    callback_ctx: dict,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    llamadas: list[str] = []
    competencia_id = uuid4()

    class FakeRankingHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, _command) -> None:
            llamadas.append("ranking")

    class FakeOverallHandler:
        def __init__(self, *_args, **_kwargs) -> None:
            pass

        async def handle(self, _command) -> None:
            llamadas.append("overall")

    monkeypatch.setattr(app_module, "CalcularRankingHandler", FakeRankingHandler)
    monkeypatch.setattr(app_module, "CalcularOverallHandler", FakeOverallHandler)

    callback = app_module.build_on_finalizada_callback(callback_ctx["competencia_store"])
    await callback(competencia_id, Disciplina.STA, None)

    assert llamadas == ["ranking"]
