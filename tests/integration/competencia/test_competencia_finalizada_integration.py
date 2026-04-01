"""Tests de integración — CompetenciaFinalizada + P-08 (US-2.4.1)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.exceptions import CompetenciaNoFinalizable
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_estado_adapter import (
    PerformancesEstadoAdapter,
)
from competencia.domain.aggregates.competencia import Competencia

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
    cid: object,
    pid: object,
    ot: datetime,
    posicion: int,
) -> None:
    handler = LlamarAtletaHandler(event_store=store, competencia_estado=stub)
    await handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            ot_programado=ot,
            posicion_grilla=posicion,
            andarivel=posicion,
        )
    )


async def _registrar_resultado(
    store: SQLiteEventStore,
    descriptor: DisciplinaDescriptorAdapter,
    cid: object,
    pid: object,
) -> None:
    handler = RegistrarResultadoHandler(event_store=store, disciplina_descriptor=descriptor)
    await handler.handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_rp=Decimal("295"),
            unidad=UnidadMedida.Segundos,
            registrado_por="juez",
        )
    )


async def _asignar_tarjeta(
    store: SQLiteEventStore,
    cid: object,
    pid: object,
    performances_estado: PerformancesEstadoAdapter | None = None,
) -> None:
    handler = AsignarTarjetaHandler(store, performances_estado)
    await handler.handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez",
        )
    )


async def _registrar_dns(
    store: SQLiteEventStore,
    cid: object,
    pid: object,
    performances_estado: PerformancesEstadoAdapter | None = None,
) -> None:
    handler = RegistrarDNSHandler(store, performances_estado)
    await handler.handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            registrado_por="juez",
        )
    )


async def _get_estado_competencia(store: SQLiteEventStore, cid: object) -> EstadoCompetencia:
    """Carga y reconstituye la Competencia para leer su estado."""
    events = await store.load(f"competencia-{cid}")
    if not events:
        return EstadoCompetencia.Preparacion
    from competencia.domain.aggregates.competencia import Competencia

    competencia = Competencia.reconstitute(
        competencia_id=cid, disciplina=Disciplina.STA, events=events
    )
    return competencia.estado


async def _tiene_evento_en_stream(store: SQLiteEventStore, stream_id: str, event_type: str) -> bool:
    events = await store.load(stream_id)
    return any(e["event_type"] == event_type for e in events)


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_tarjeta_ultimo_atleta_dispara_competencia_finalizada(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """P-08: asignar tarjeta al último atleta emite CompetenciaFinalizada."""
    cid = uuid4()
    pid_a, pid_b = uuid4(), uuid4()
    performances_estado = PerformancesEstadoAdapter(event_store)

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _registrar_ap(event_store, stub, descriptor, cid, pid_b)

    await _llamar(event_store, stub, cid, pid_a, OT_A, 1)
    await _llamar(event_store, stub, cid, pid_b, OT_B, 2)

    await _registrar_resultado(event_store, descriptor, cid, pid_a)
    await _registrar_resultado(event_store, descriptor, cid, pid_b)

    # Tarjeta a A — no es la última
    await _asignar_tarjeta(event_store, cid, pid_a, performances_estado)
    assert not await _tiene_evento_en_stream(
        event_store, f"competencia-{cid}", "CompetenciaFinalizada"
    )

    # Tarjeta a B — es la última
    await _asignar_tarjeta(event_store, cid, pid_b, performances_estado)
    assert await _tiene_evento_en_stream(event_store, f"competencia-{cid}", "CompetenciaFinalizada")


@pytest.mark.asyncio
async def test_dns_ultimo_atleta_dispara_competencia_finalizada(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """P-08 via DNS: cuando el último atleta registra DNS, emite CompetenciaFinalizada."""
    cid = uuid4()
    pid_a, pid_b = uuid4(), uuid4()
    performances_estado = PerformancesEstadoAdapter(event_store)

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _registrar_ap(event_store, stub, descriptor, cid, pid_b)

    await _llamar(event_store, stub, cid, pid_a, OT_A, 1)
    await _llamar(event_store, stub, cid, pid_b, OT_B, 2)

    await _registrar_resultado(event_store, descriptor, cid, pid_a)
    await _asignar_tarjeta(event_store, cid, pid_a, performances_estado)

    # DNS de B — es la última
    await _registrar_dns(event_store, cid, pid_b, performances_estado)
    assert await _tiene_evento_en_stream(event_store, f"competencia-{cid}", "CompetenciaFinalizada")


@pytest.mark.asyncio
async def test_sin_port_no_emite_competencia_finalizada(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """Sin PerformancesEstadoPort, P-08 no se ejecuta — backward compat."""
    cid = uuid4()
    pid_a = uuid4()

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _llamar(event_store, stub, cid, pid_a, OT_A, 1)
    await _registrar_resultado(event_store, descriptor, cid, pid_a)
    await _asignar_tarjeta(event_store, cid, pid_a, performances_estado=None)

    assert not await _tiene_evento_en_stream(
        event_store, f"competencia-{cid}", "CompetenciaFinalizada"
    )


@pytest.mark.asyncio
async def test_competencia_finalizada_payload_correcto(
    event_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """El payload de CompetenciaFinalizada contiene los campos requeridos por la spec."""
    cid = uuid4()
    pid_a, pid_b = uuid4(), uuid4()
    performances_estado = PerformancesEstadoAdapter(event_store)

    await _registrar_ap(event_store, stub, descriptor, cid, pid_a)
    await _registrar_ap(event_store, stub, descriptor, cid, pid_b)
    await _llamar(event_store, stub, cid, pid_a, OT_A, 1)
    await _llamar(event_store, stub, cid, pid_b, OT_B, 2)
    await _registrar_resultado(event_store, descriptor, cid, pid_a)
    await _asignar_tarjeta(event_store, cid, pid_a, performances_estado)
    await _registrar_dns(event_store, cid, pid_b, performances_estado)

    events = await event_store.load(f"competencia-{cid}")
    import json

    cf_events = [e for e in events if e["event_type"] == "CompetenciaFinalizada"]
    assert len(cf_events) == 1

    payload = (
        json.loads(cf_events[0]["payload"])
        if isinstance(cf_events[0]["payload"], str)
        else cf_events[0]["payload"]
    )
    assert payload["competencia_id"] == str(cid)
    assert payload["disciplina"] == Disciplina.STA.value
    assert payload["total_performances"] == 2
    assert payload["ejecutadas"] == 1
    assert payload["dns_count"] == 1
