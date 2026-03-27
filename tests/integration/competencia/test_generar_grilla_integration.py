"""Tests de integración — GenerarGrillaHandler con SQLiteEventStore real."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
    _build_stream_id,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import (
    IntervaloNoConfigurado,
    SinPerformancesParaGrilla,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
from competencia.infrastructure.repositories.performances_ap_adapter import (
    PerformancesAPAdapter,
)

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

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
DISCIPLINA = Disciplina.STA
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

A001 = UUID("00000000-0000-0000-0000-000000000011")
A002 = UUID("00000000-0000-0000-0000-000000000012")
A003 = UUID("00000000-0000-0000-0000-000000000013")


@pytest.fixture
async def event_store(tmp_path: Any) -> SQLiteEventStore:
    db_path = str(tmp_path / "test_grilla.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


async def _seed_intervalo(store: SQLiteEventStore) -> None:
    handler = ConfigurarIntervaloOTHandler(store)
    await handler.handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            intervalo_minutos=9,
            configurado_por="org",
        )
    )


async def _seed_ap(
    store: SQLiteEventStore, atleta_id: UUID, valor: str
) -> None:
    stub = StubCompetenciaEstadoAdapter()
    handler = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    await handler.handle(
        RegistrarAPCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=atleta_id,
            disciplina=DISCIPLINA,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Segundos,
        )
    )


class TestGenerarGrillaIntegracion:
    @pytest.mark.asyncio
    async def test_grilla_generada_persiste_en_stream(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_intervalo(event_store)
        await _seed_ap(event_store, A001, "330")

        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                ot_inicio=OT_INICIO,
            )
        )

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        event_types = [e["event_type"] for e in events]
        assert "GrillaDeSalidaGenerada" in event_types

    @pytest.mark.asyncio
    async def test_orden_sta_correcto_tres_atletas(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_intervalo(event_store)
        await _seed_ap(event_store, A001, "330")  # 5:30
        await _seed_ap(event_store, A002, "360")  # 6:00 — mayor, pos=1
        await _seed_ap(event_store, A003, "285")  # 4:45 — menor, pos=3

        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                ot_inicio=OT_INICIO,
            )
        )

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        grilla_event = next(e for e in events if e["event_type"] == "GrillaDeSalidaGenerada")
        perfs = grilla_event["payload"]["performances"]

        atletas_orden = [p["atleta_id"] for p in perfs]
        assert atletas_orden[0] == str(A002)  # mayor AP primero
        assert atletas_orden[2] == str(A003)  # menor AP último

    @pytest.mark.asyncio
    async def test_ot_calculados_correctamente(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_intervalo(event_store)
        await _seed_ap(event_store, A001, "330")
        await _seed_ap(event_store, A002, "360")

        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                ot_inicio=OT_INICIO,
            )
        )

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        grilla_event = next(e for e in events if e["event_type"] == "GrillaDeSalidaGenerada")
        perfs = grilla_event["payload"]["performances"]

        ot_pos1 = datetime.fromisoformat(perfs[0]["ot_programado"])
        ot_pos2 = datetime.fromisoformat(perfs[1]["ot_programado"])
        assert ot_pos2 - ot_pos1 == timedelta(minutes=9)

    @pytest.mark.asyncio
    async def test_reconstituyendo_grilla_desde_store(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_intervalo(event_store)
        await _seed_ap(event_store, A001, "330")

        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                ot_inicio=OT_INICIO,
            )
        )

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert len(c.grilla) == 1
        assert c.grilla[0].posicion == 1

    @pytest.mark.asyncio
    async def test_regeneracion_agrega_segundo_evento(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_intervalo(event_store)
        await _seed_ap(event_store, A001, "330")

        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        cmd = GenerarGrillaCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            ot_inicio=OT_INICIO,
        )
        await handler.handle(cmd)
        await handler.handle(cmd)

        stream_id = _build_stream_id(COMPETENCIA_ID)
        events = await event_store.load(stream_id)
        grilla_events = [e for e in events if e["event_type"] == "GrillaDeSalidaGenerada"]
        assert len(grilla_events) == 2

    @pytest.mark.asyncio
    async def test_sin_ap_registrado_lanza_excepcion(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_intervalo(event_store)
        # No se registran APs

        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        with pytest.raises(SinPerformancesParaGrilla):
            await handler.handle(
                GenerarGrillaCommand(
                    competencia_id=COMPETENCIA_ID,
                    disciplina=DISCIPLINA,
                    ot_inicio=OT_INICIO,
                )
            )
