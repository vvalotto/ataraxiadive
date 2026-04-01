"""Tests de integración — ConfirmarGrillaHandler e IniciarCompetenciaHandler con SQLiteEventStore real."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import aiosqlite
import pytest

from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import CompetenciaNoConfirmada, GrillaYaConfirmada
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter

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

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000005")
DISCIPLINA = Disciplina.STA
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
STREAM_ID = f"competencia-{COMPETENCIA_ID}"

A001 = UUID("00000000-0000-0000-0000-000000000011")
A002 = UUID("00000000-0000-0000-0000-000000000012")


@pytest.fixture
async def event_store(tmp_path: Any) -> SQLiteEventStore:
    db_path = str(tmp_path / "test_confirmar.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


async def _seed_grilla(store: SQLiteEventStore) -> None:
    """Seed: intervalo + 2 APs + grilla generada."""
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            intervalo_minutos=9,
            configurado_por="org",
        )
    )
    stub = StubCompetenciaEstadoAdapter()
    handler_ap = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    for atleta_id, valor in [(A001, "300"), (A002, "240")]:
        await handler_ap.handle(
            RegistrarAPCommand(
                competencia_id=COMPETENCIA_ID,
                participante_id=atleta_id,
                disciplina=DISCIPLINA,
                valor_ap=Decimal(valor),
                unidad=UnidadMedida.Segundos,
            )
        )
    adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter()).handle(
        GenerarGrillaCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            ot_inicio=OT_INICIO,
        )
    )


class TestConfirmarGrillaIntegracion:
    @pytest.mark.asyncio
    async def test_confirmar_persiste_grilla_confirmada_en_stream(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_grilla(event_store)
        await ConfirmarGrillaHandler(event_store).handle(
            ConfirmarGrillaCommand(COMPETENCIA_ID, DISCIPLINA)
        )
        events = await event_store.load(STREAM_ID)
        event_types = [e["event_type"] for e in events]
        assert "GrillaConfirmada" in event_types

    @pytest.mark.asyncio
    async def test_reconstitution_refleja_estado_confirmada(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_grilla(event_store)
        await ConfirmarGrillaHandler(event_store).handle(
            ConfirmarGrillaCommand(COMPETENCIA_ID, DISCIPLINA)
        )
        events = await event_store.load(STREAM_ID)
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.estado == EstadoCompetencia.Confirmada
        assert c.grilla_confirmada is True

    @pytest.mark.asyncio
    async def test_confirmar_dos_veces_lanza_grilla_ya_confirmada(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_grilla(event_store)
        handler = ConfirmarGrillaHandler(event_store)
        await handler.handle(ConfirmarGrillaCommand(COMPETENCIA_ID, DISCIPLINA))
        with pytest.raises(GrillaYaConfirmada):
            await handler.handle(ConfirmarGrillaCommand(COMPETENCIA_ID, DISCIPLINA))

    @pytest.mark.asyncio
    async def test_iniciar_tras_confirmar_cambia_estado_a_en_ejecucion(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_grilla(event_store)
        await ConfirmarGrillaHandler(event_store).handle(
            ConfirmarGrillaCommand(COMPETENCIA_ID, DISCIPLINA)
        )
        await IniciarCompetenciaHandler(event_store).handle(
            IniciarCompetenciaCommand(COMPETENCIA_ID, DISCIPLINA, "juez-01")
        )
        events = await event_store.load(STREAM_ID)
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.estado == EstadoCompetencia.EnEjecucion

    @pytest.mark.asyncio
    async def test_iniciar_sin_confirmar_lanza_competencia_no_confirmada(
        self, event_store: SQLiteEventStore
    ) -> None:
        await _seed_grilla(event_store)  # grilla generada pero no confirmada
        with pytest.raises(CompetenciaNoConfirmada):
            await IniciarCompetenciaHandler(event_store).handle(
                IniciarCompetenciaCommand(COMPETENCIA_ID, DISCIPLINA, "juez-01")
            )

    @pytest.mark.asyncio
    async def test_flujo_completo_grilla_a_en_ejecucion(
        self, event_store: SQLiteEventStore
    ) -> None:
        """End-to-end: intervalo → generar → confirmar → iniciar."""
        await _seed_grilla(event_store)
        await ConfirmarGrillaHandler(event_store).handle(
            ConfirmarGrillaCommand(COMPETENCIA_ID, DISCIPLINA)
        )
        await IniciarCompetenciaHandler(event_store).handle(
            IniciarCompetenciaCommand(COMPETENCIA_ID, DISCIPLINA, "juez-01")
        )
        events = await event_store.load(STREAM_ID)
        event_types = [e["event_type"] for e in events]
        assert "GrillaConfirmada" in event_types
        assert "CompetenciaIniciada" in event_types
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.estado == EstadoCompetencia.EnEjecucion
