"""Tests de integración — GenerarGrilla con DisciplinaDescriptorAdapter real (US-2.2.1)."""
from __future__ import annotations

from datetime import datetime, timezone
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
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter

_CREATE_TABLE = """
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

OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
A001 = UUID("00000000-0000-0000-0000-000000000011")
A002 = UUID("00000000-0000-0000-0000-000000000012")
A003 = UUID("00000000-0000-0000-0000-000000000013")


@pytest.fixture
async def event_store(tmp_path: Any) -> SQLiteEventStore:
    db_path = str(tmp_path / "test_descriptor.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(_CREATE_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


async def _seed_competencia(
    store: SQLiteEventStore,
    competencia_id: UUID,
    disciplina: Disciplina,
    aps: list[tuple[UUID, Decimal, UnidadMedida]],
) -> None:
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
            intervalo_minutos=9,
            configurado_por="org",
        )
    )
    for atleta_id, valor, unidad in aps:
        await RegistrarAPHandler(store, StubCompetenciaEstadoAdapter()).handle(
            RegistrarAPCommand(
                competencia_id=competencia_id,
                participante_id=atleta_id,
                disciplina=disciplina,
                valor_ap=valor,
                unidad=unidad,
            )
        )


class TestGrillaSTAOrdenDescendente:
    @pytest.mark.asyncio
    async def test_grilla_sta_mayor_ap_primero(self, event_store: SQLiteEventStore) -> None:
        """STA: AP mayor→menor (primero 300s, último 120s)."""
        comp_id = UUID("00000000-0000-0000-0000-000000000001")
        await _seed_competencia(
            event_store,
            comp_id,
            Disciplina.STA,
            [
                (A001, Decimal("120"), UnidadMedida.Segundos),
                (A002, Decimal("300"), UnidadMedida.Segundos),
                (A003, Decimal("180"), UnidadMedida.Segundos),
            ],
        )
        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=comp_id,
                disciplina=Disciplina.STA,
                ot_inicio=OT_INICIO,
            )
        )

        from competencia.domain.aggregates.competencia import Competencia
        stream_id = f"competencia-{comp_id}"
        events = await event_store.load(stream_id)
        comp = Competencia.reconstitute(comp_id, Disciplina.STA, events)

        atletas = [str(e.atleta_id) for e in comp.grilla]
        assert atletas == [str(A002), str(A003), str(A001)]  # 300, 180, 120


class TestGrillaDNFOrdenAscendente:
    @pytest.mark.asyncio
    async def test_grilla_dnf_menor_ap_primero(self, event_store: SQLiteEventStore) -> None:
        """DNF: AP menor→mayor (primero 40m, último 80m)."""
        comp_id = UUID("00000000-0000-0000-0000-000000000002")
        await _seed_competencia(
            event_store,
            comp_id,
            Disciplina.DNF,
            [
                (A001, Decimal("80"), UnidadMedida.Metros),
                (A002, Decimal("40"), UnidadMedida.Metros),
                (A003, Decimal("60"), UnidadMedida.Metros),
            ],
        )
        adapter = PerformancesAPAdapter(event_store)
        handler = GenerarGrillaHandler(event_store, adapter, DisciplinaDescriptorAdapter())
        await handler.handle(
            GenerarGrillaCommand(
                competencia_id=comp_id,
                disciplina=Disciplina.DNF,
                ot_inicio=OT_INICIO,
            )
        )

        from competencia.domain.aggregates.competencia import Competencia
        stream_id = f"competencia-{comp_id}"
        events = await event_store.load(stream_id)
        comp = Competencia.reconstitute(comp_id, Disciplina.DNF, events)

        atletas = [str(e.atleta_id) for e in comp.grilla]
        assert atletas == [str(A002), str(A003), str(A001)]  # 40, 60, 80
