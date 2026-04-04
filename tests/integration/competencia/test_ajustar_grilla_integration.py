"""Tests de integración — AjustarGrillaHandler con SQLiteEventStore real."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import aiosqlite
import pytest

from competencia.application.commands.ajustar_grilla import (
    AjustarGrillaCommand,
    AjustarGrillaHandler,
)
from competencia.application.commands._stream_ids import competencia_stream_id as _build_stream_id
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import GrillaNoGenerada, GrillaYaConfirmada
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina
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

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
DISCIPLINA = Disciplina.STA
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

A001 = UUID("00000000-0000-0000-0000-000000000011")
A002 = UUID("00000000-0000-0000-0000-000000000012")
A003 = UUID("00000000-0000-0000-0000-000000000013")


@pytest.fixture
async def event_store(tmp_path: Any) -> SQLiteEventStore:
    db_path = str(tmp_path / "test_ajustar.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


async def _seed_grilla(store: SQLiteEventStore) -> dict[str, UUID]:
    """Seed: intervalo + 3 APs + grilla generada. Retorna {atletaId: performanceId}."""
    handler_intervalo = ConfigurarIntervaloOTHandler(store)
    await handler_intervalo.handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            intervalo_minutos=9,
            configurado_por="org",
        )
    )
    stub = StubCompetenciaEstadoAdapter()
    handler_ap = RegistrarAPHandler(store, stub, DisciplinaDescriptorAdapter())
    for atleta_id, valor in [(A001, "330"), (A002, "360"), (A003, "285")]:
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
    handler_grilla = GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter())
    await handler_grilla.handle(
        GenerarGrillaCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            ot_inicio=OT_INICIO,
        )
    )

    # Recuperar performance_ids del stream
    events = await store.load(_build_stream_id(COMPETENCIA_ID))
    grilla_event = next(e for e in events if e["event_type"] == "GrillaDeSalidaGenerada")
    return {
        UUID(p["atleta_id"]): UUID(p["performance_id"])
        for p in grilla_event["payload"]["performances"]
    }


class TestAjustarGrillaIntegracion:
    @pytest.mark.asyncio
    async def test_ajuste_persiste_evento_en_stream(self, event_store: SQLiteEventStore) -> None:
        perf_ids = await _seed_grilla(event_store)
        p_a001 = perf_ids[A001]

        handler = AjustarGrillaHandler(event_store)
        await handler.handle(
            AjustarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                cambios=[CambioGrilla(performance_id=p_a001, campo="posicion", valor_nuevo=1)],
            )
        )

        events = await event_store.load(_build_stream_id(COMPETENCIA_ID))
        event_types = [e["event_type"] for e in events]
        assert "GrillaDeSalidaAjustada" in event_types

    @pytest.mark.asyncio
    async def test_reconstitucion_refleja_estado_ajustado(
        self, event_store: SQLiteEventStore
    ) -> None:
        perf_ids = await _seed_grilla(event_store)
        p_a001 = perf_ids[A001]

        handler = AjustarGrillaHandler(event_store)
        await handler.handle(
            AjustarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                cambios=[CambioGrilla(performance_id=p_a001, campo="posicion", valor_nuevo=1)],
            )
        )

        events = await event_store.load(_build_stream_id(COMPETENCIA_ID))
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        entry_a001 = next(e for e in c.grilla if e.performance_id == p_a001)
        assert entry_a001.posicion == 1
        assert entry_a001.ot_programado == OT_INICIO

    @pytest.mark.asyncio
    async def test_ajuste_acumulativo_dos_eventos_en_stream(
        self, event_store: SQLiteEventStore
    ) -> None:
        perf_ids = await _seed_grilla(event_store)
        p_a001 = perf_ids[A001]
        p_a002 = perf_ids[A002]

        handler = AjustarGrillaHandler(event_store)
        await handler.handle(
            AjustarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                cambios=[CambioGrilla(performance_id=p_a001, campo="posicion", valor_nuevo=1)],
            )
        )
        await handler.handle(
            AjustarGrillaCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                cambios=[CambioGrilla(performance_id=p_a002, campo="andarivel", valor_nuevo=2)],
            )
        )

        events = await event_store.load(_build_stream_id(COMPETENCIA_ID))
        ajuste_events = [e for e in events if e["event_type"] == "GrillaDeSalidaAjustada"]
        assert len(ajuste_events) == 2

    @pytest.mark.asyncio
    async def test_sin_grilla_generada_lanza_excepcion(self, event_store: SQLiteEventStore) -> None:
        handler_intervalo = ConfigurarIntervaloOTHandler(event_store)
        await handler_intervalo.handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=COMPETENCIA_ID,
                disciplina=DISCIPLINA,
                intervalo_minutos=9,
                configurado_por="org",
            )
        )
        handler = AjustarGrillaHandler(event_store)
        with pytest.raises(GrillaNoGenerada):
            await handler.handle(
                AjustarGrillaCommand(
                    competencia_id=COMPETENCIA_ID,
                    disciplina=DISCIPLINA,
                    cambios=[CambioGrilla(performance_id=uuid4(), campo="posicion", valor_nuevo=1)],
                )
            )
