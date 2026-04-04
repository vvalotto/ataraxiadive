"""Tests de integración — AndarivelesActivosAdapter + LlamarAtletaHandler (US-2.3.1)."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import aiosqlite
import pytest

from competencia.application.commands.llamar_atleta import (
    AndarivelesConflicto,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
)
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.application.queries.obtener_andariveles_activos import (
    ObtenerAndarivelesActivosHandler,
    ObtenerAndarivelesActivosQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from decimal import Decimal
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.andariveles_activos_adapter import (
    AndarivelesActivosAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

OT_A = datetime(2026, 3, 22, 10, 30, 0)
OT_B = datetime(2026, 3, 22, 10, 33, 0)
OT_C = datetime(2026, 3, 22, 10, 36, 0)

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


@pytest.fixture
async def event_store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    db_path = str(tmp_path / "test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def stub() -> StubCompetenciaEstadoAdapter:
    return StubCompetenciaEstadoAdapter()


@pytest.fixture
def descriptor() -> DisciplinaDescriptorAdapter:
    return DisciplinaDescriptorAdapter()


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _registrar_ap(
    store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
    cid: object,
    pid: object,
) -> None:
    handler = RegistrarAPHandler(
        event_store=store, competencia_estado=stub, disciplina_descriptor=descriptor
    )
    await handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_ap=Decimal("300"),
            unidad=UnidadMedida.Segundos,
        )
    )


async def _llamar(
    store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    adapter: AndarivelesActivosAdapter,
    cid: object,
    pid: object,
    andarivel: int,
    ot: datetime,
    posicion: int,
) -> None:
    handler = LlamarAtletaHandler(
        event_store=store, competencia_estado=stub, andariveles_activos=adapter
    )
    await handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            ot_programado=ot,
            posicion_grilla=posicion,
            andarivel=andarivel,
        )
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_dos_atletas_andariveles_distintos_sin_conflicto(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """Llamar A (andarivel 1) y B (andarivel 2) simultáneamente — ambos persisten."""
    cid = uuid4()
    pid_a, pid_b = uuid4(), uuid4()
    adapter = AndarivelesActivosAdapter(event_store)

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _registrar_ap(event_store, stub, descriptor, cid, pid_b)

    await _llamar(event_store, stub, adapter, cid, pid_a, andarivel=1, ot=OT_A, posicion=1)
    await _llamar(event_store, stub, adapter, cid, pid_b, andarivel=2, ot=OT_B, posicion=2)

    # Ambos activos
    result = await ObtenerAndarivelesActivosHandler(adapter).handle(
        ObtenerAndarivelesActivosQuery(competencia_id=cid, disciplina=Disciplina.STA, andariveles=2)
    )
    assert result[0].ocupado is True
    assert result[0].atleta_id == pid_a
    assert result[1].ocupado is True
    assert result[1].atleta_id == pid_b


@pytest.mark.asyncio
async def test_conflicto_andarivel_rechaza_llamada(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """INV-C-05: llamar C en andarivel 1 mientras A está en Llamada → AndarivelesConflicto."""
    cid = uuid4()
    pid_a, pid_c = uuid4(), uuid4()
    adapter = AndarivelesActivosAdapter(event_store)

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _registrar_ap(event_store, stub, descriptor, cid, pid_c)

    # Llamar A en andarivel 1
    await _llamar(event_store, stub, adapter, cid, pid_a, andarivel=1, ot=OT_A, posicion=1)

    # Intentar llamar C en andarivel 1 → conflicto
    with pytest.raises(AndarivelesConflicto):
        await _llamar(event_store, stub, adapter, cid, pid_c, andarivel=1, ot=OT_C, posicion=3)


@pytest.mark.asyncio
async def test_andarivel_liberado_tras_resultado(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """Tras registrar resultado de A, andarivel 1 queda libre — C puede llamarse."""
    cid = uuid4()
    pid_a, pid_c = uuid4(), uuid4()
    adapter = AndarivelesActivosAdapter(event_store)

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _registrar_ap(event_store, stub, descriptor, cid, pid_c)

    await _llamar(event_store, stub, adapter, cid, pid_a, andarivel=1, ot=OT_A, posicion=1)

    # Registrar resultado de A (andarivel 1 se libera)
    resultado_handler = RegistrarResultadoHandler(
        event_store=event_store,
        disciplina_descriptor=descriptor,
    )
    await resultado_handler.handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid_a,
            disciplina=Disciplina.STA,
            valor_rp=Decimal("295"),
            unidad=UnidadMedida.Segundos,
            registrado_por="juez",
        )
    )

    # Ahora C puede llamarse en andarivel 1
    await _llamar(event_store, stub, adapter, cid, pid_c, andarivel=1, ot=OT_C, posicion=3)

    result = await ObtenerAndarivelesActivosHandler(adapter).handle(
        ObtenerAndarivelesActivosQuery(competencia_id=cid, disciplina=Disciplina.STA, andariveles=2)
    )
    assert result[0].ocupado is True
    assert result[0].atleta_id == pid_c
