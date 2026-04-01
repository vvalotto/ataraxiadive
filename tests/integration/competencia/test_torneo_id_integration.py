"""Tests de integración — torneo_id en Competencia con SQLiteEventStore real (US-3.3.1)."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
    _build_stream_id,
)
from competencia.application.queries.obtener_competencias_por_torneo import (
    ObtenerCompetenciasPorTorneoHandler,
    ObtenerCompetenciasPorTorneoQuery,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

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

TORNEO_A = UUID("00000000-0000-0000-0000-000000000010")
TORNEO_B = UUID("00000000-0000-0000-0000-000000000020")
COMP_1 = UUID("00000000-0000-0000-0000-000000000001")
COMP_2 = UUID("00000000-0000-0000-0000-000000000002")
COMP_3 = UUID("00000000-0000-0000-0000-000000000003")


@pytest.fixture
async def event_store(tmp_path: Any) -> SQLiteEventStore:
    db_path = str(tmp_path / "test_competencia.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


def _command(
    competencia_id: UUID,
    disciplina: Disciplina = Disciplina.STA,
    torneo_id: UUID | None = None,
) -> ConfigurarIntervaloOTCommand:
    return ConfigurarIntervaloOTCommand(
        competencia_id=competencia_id,
        disciplina=disciplina,
        intervalo_minutos=9,
        configurado_por="org-01",
        torneo_id=torneo_id,
    )


class TestTorneoIdPersistencia:
    @pytest.mark.asyncio
    async def test_torneo_id_persiste_en_payload(self, event_store: SQLiteEventStore) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(COMP_1, torneo_id=TORNEO_A))

        events = await event_store.load(_build_stream_id(COMP_1))
        assert events[0]["payload"]["torneo_id"] == str(TORNEO_A)

    @pytest.mark.asyncio
    async def test_sin_torneo_id_payload_tiene_none(self, event_store: SQLiteEventStore) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(COMP_1))

        events = await event_store.load(_build_stream_id(COMP_1))
        assert events[0]["payload"]["torneo_id"] is None

    @pytest.mark.asyncio
    async def test_reconstitute_desde_store_recupera_torneo_id(
        self, event_store: SQLiteEventStore
    ) -> None:
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(COMP_1, torneo_id=TORNEO_A))

        events = await event_store.load(_build_stream_id(COMP_1))
        c = Competencia.reconstitute(COMP_1, Disciplina.STA, events)
        assert c.torneo_id == TORNEO_A

    @pytest.mark.asyncio
    async def test_backward_compat_stream_sin_torneo_id(
        self, event_store: SQLiteEventStore
    ) -> None:
        """Stream SP1/SP2 sin torneo_id en payload se reconstituye correctamente."""
        handler = ConfigurarIntervaloOTHandler(event_store)
        await handler.handle(_command(COMP_1))  # sin torneo_id

        events = await event_store.load(_build_stream_id(COMP_1))
        c = Competencia.reconstitute(COMP_1, Disciplina.STA, events)
        assert c.torneo_id is None
        assert c.intervalo is not None


class TestObtenerCompetenciasPorTorneoIntegracion:
    @pytest.mark.asyncio
    async def test_lista_3_competencias_del_mismo_torneo(
        self, event_store: SQLiteEventStore
    ) -> None:
        handler_cmd = ConfigurarIntervaloOTHandler(event_store)
        await handler_cmd.handle(_command(COMP_1, Disciplina.STA, TORNEO_A))
        await handler_cmd.handle(_command(COMP_2, Disciplina.DNF, TORNEO_A))
        await handler_cmd.handle(_command(COMP_3, Disciplina.DYN, TORNEO_A))

        handler_qry = ObtenerCompetenciasPorTorneoHandler(event_store)
        result = await handler_qry.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        assert len(result) == 3

    @pytest.mark.asyncio
    async def test_filtra_por_torneo_id_correcto(self, event_store: SQLiteEventStore) -> None:
        handler_cmd = ConfigurarIntervaloOTHandler(event_store)
        await handler_cmd.handle(_command(COMP_1, Disciplina.STA, TORNEO_A))
        await handler_cmd.handle(_command(COMP_2, Disciplina.DNF, TORNEO_A))
        await handler_cmd.handle(_command(COMP_3, Disciplina.DYN, TORNEO_B))

        handler_qry = ObtenerCompetenciasPorTorneoHandler(event_store)
        result_a = await handler_qry.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        result_b = await handler_qry.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_B))
        assert len(result_a) == 2
        assert len(result_b) == 1
        assert result_b[0].competencia_id == COMP_3

    @pytest.mark.asyncio
    async def test_excluye_competencias_standalone(self, event_store: SQLiteEventStore) -> None:
        handler_cmd = ConfigurarIntervaloOTHandler(event_store)
        await handler_cmd.handle(_command(COMP_1, Disciplina.STA, TORNEO_A))
        await handler_cmd.handle(_command(COMP_2, Disciplina.DNF))  # standalone

        handler_qry = ObtenerCompetenciasPorTorneoHandler(event_store)
        result = await handler_qry.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=TORNEO_A))
        assert len(result) == 1
        assert result[0].competencia_id == COMP_1
