"""Tests de integración — RegistrarDNSHandler con SQLiteEventStore real."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest

from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import EstadoInvalidoParaRegistrarDNS
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
OT = datetime(2026, 3, 23, 10, 30, 0)

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
    """SQLiteEventStore sobre SQLite en disco temporal."""
    db_path = str(tmp_path / "competencia_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def stub() -> StubCompetenciaEstadoAdapter:
    return StubCompetenciaEstadoAdapter()


@pytest.fixture
def registrar_ap_handler(
    event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter
) -> RegistrarAPHandler:
    return RegistrarAPHandler(event_store=event_store, competencia_estado=stub, disciplina_descriptor=DisciplinaDescriptorAdapter())


@pytest.fixture
def llamar_handler(
    event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter
) -> LlamarAtletaHandler:
    return LlamarAtletaHandler(event_store=event_store, competencia_estado=stub)


@pytest.fixture
def dns_handler(event_store: SQLiteEventStore) -> RegistrarDNSHandler:
    return RegistrarDNSHandler(event_store=event_store)


async def _setup_performance_en_llamada(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    cid: object,
    pid: object,
) -> None:
    """Lleva una Performance hasta el estado Llamada."""
    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.STA,
            valor_ap=Decimal("330"),
            unidad=UnidadMedida.Segundos,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.STA,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )


# ── Flujo completo ────────────────────────────────────────────────────────────


async def test_flujo_completo_hasta_dns(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    dns_handler: RegistrarDNSHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Flujo completo: RegistrarAP → LlamarAtleta → RegistrarDNS."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_en_llamada(registrar_ap_handler, llamar_handler, cid, pid)

    await dns_handler.handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            registrado_por="juez-001",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.STA.value}"
    events = await event_store.load(stream_id)
    assert len(events) == 3
    assert events[2]["event_type"] == "DNSRegistrado"

    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.DNS


async def test_dns_payload_correcto(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    dns_handler: RegistrarDNSHandler,
    event_store: SQLiteEventStore,
) -> None:
    """El payload de DNSRegistrado contiene registradoPor y ot_programado correctos."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_en_llamada(registrar_ap_handler, llamar_handler, cid, pid)

    await dns_handler.handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            registrado_por="juez-007",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.STA.value}"
    events = await event_store.load(stream_id)
    payload = events[2]["payload"]
    assert payload["registrado_por"] == "juez-007"
    assert payload["ot_programado"] == OT.isoformat()


# ── INV-P-08 ──────────────────────────────────────────────────────────────────


async def test_dns_desde_anunciada_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    dns_handler: RegistrarDNSHandler,
) -> None:
    """INV-P-08: EstadoInvalidoParaRegistrarDNS si Performance en AnunciadaAP."""
    cid = uuid4()
    pid = uuid4()

    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_ap=Decimal("330"),
            unidad=UnidadMedida.Segundos,
        )
    )

    with pytest.raises(EstadoInvalidoParaRegistrarDNS):
        await dns_handler.handle(
            RegistrarDNSCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.STA,
                registrado_por="juez-001",
            )
        )
