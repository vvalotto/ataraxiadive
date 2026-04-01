"""Tests de integración — CorregirResultadoHandler con SQLiteEventStore real."""

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
from competencia.application.commands.corregir_resultado import (
    CorregirResultadoCommand,
    CorregirResultadoHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import EstadoInvalidoParaCorregirResultado, MotivoObligatorio
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

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
    return RegistrarAPHandler(
        event_store=event_store,
        competencia_estado=stub,
        disciplina_descriptor=DisciplinaDescriptorAdapter(),
    )


@pytest.fixture
def llamar_handler(
    event_store: SQLiteEventStore, stub: StubCompetenciaEstadoAdapter
) -> LlamarAtletaHandler:
    return LlamarAtletaHandler(event_store=event_store, competencia_estado=stub)


@pytest.fixture
def registrar_resultado_handler(event_store: SQLiteEventStore) -> RegistrarResultadoHandler:
    return RegistrarResultadoHandler(
        event_store=event_store, disciplina_descriptor=DisciplinaDescriptorAdapter()
    )


@pytest.fixture
def asignar_tarjeta_handler(event_store: SQLiteEventStore) -> AsignarTarjetaHandler:
    return AsignarTarjetaHandler(event_store=event_store)


@pytest.fixture
def corregir_resultado_handler(event_store: SQLiteEventStore) -> CorregirResultadoHandler:
    return CorregirResultadoHandler(event_store=event_store)


async def _setup_performance_en_ejecutada(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    registrar_resultado_handler: RegistrarResultadoHandler,
    asignar_tarjeta_handler: AsignarTarjetaHandler,
    cid: object,
    pid: object,
) -> None:
    """Lleva una Performance hasta el estado Ejecutada."""
    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.STA,
            valor_ap=Decimal("90"),
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
    await registrar_resultado_handler.handle(
        RegistrarResultadoCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.STA,
            valor_rp=Decimal("89.5"),
            unidad=UnidadMedida.Segundos,
            registrado_por="juez-001",
        )
    )
    await asignar_tarjeta_handler.handle(
        AsignarTarjetaCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.STA,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-001",
        )
    )


# ── Flujo completo ────────────────────────────────────────────────────────────


async def test_flujo_completo_hasta_correccion(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    registrar_resultado_handler: RegistrarResultadoHandler,
    asignar_tarjeta_handler: AsignarTarjetaHandler,
    corregir_resultado_handler: CorregirResultadoHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Flujo completo: AP → Llamada → Resultado → Tarjeta → CorregirResultado."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_en_ejecutada(
        registrar_ap_handler,
        llamar_handler,
        registrar_resultado_handler,
        asignar_tarjeta_handler,
        cid,
        pid,
    )

    await corregir_resultado_handler.handle(
        CorregirResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_rp=Decimal("90.0"),
            unidad=UnidadMedida.Segundos,
            registrado_por="juez-001",
            motivo="Error de lectura en planilla",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.STA.value}"
    events = await event_store.load(stream_id)
    assert len(events) == 5
    assert events[4]["event_type"] == "ResultadoCorregido"

    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.Ejecutada
    assert performance.rp == Decimal("90.0")


async def test_correccion_payload_correcto(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    registrar_resultado_handler: RegistrarResultadoHandler,
    asignar_tarjeta_handler: AsignarTarjetaHandler,
    corregir_resultado_handler: CorregirResultadoHandler,
    event_store: SQLiteEventStore,
) -> None:
    """El payload de ResultadoCorregido contiene los campos correctos."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_en_ejecutada(
        registrar_ap_handler,
        llamar_handler,
        registrar_resultado_handler,
        asignar_tarjeta_handler,
        cid,
        pid,
    )

    await corregir_resultado_handler.handle(
        CorregirResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_rp=Decimal("90.0"),
            unidad=UnidadMedida.Segundos,
            registrado_por="juez-007",
            motivo="Corrección confirmada por árbitro",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.STA.value}"
    events = await event_store.load(stream_id)
    payload = events[4]["payload"]
    assert payload["valor_rp_anterior"] == "89.5"
    assert payload["valor_rp_nuevo"] == "90.0"
    assert payload["motivo"] == "Corrección confirmada por árbitro"
    assert payload["registrado_por"] == "juez-007"


# ── INV-P-12/13 ───────────────────────────────────────────────────────────────


async def test_correccion_desde_anunciada_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    corregir_resultado_handler: CorregirResultadoHandler,
) -> None:
    """INV-P-12: EstadoInvalidoParaCorregirResultado si Performance en AnunciadaAP."""
    cid = uuid4()
    pid = uuid4()

    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.STA,
            valor_ap=Decimal("90"),
            unidad=UnidadMedida.Segundos,
        )
    )

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        await corregir_resultado_handler.handle(
            CorregirResultadoCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.STA,
                valor_rp=Decimal("90.0"),
                unidad=UnidadMedida.Segundos,
                registrado_por="juez-001",
                motivo="motivo",
            )
        )


async def test_correccion_sin_motivo_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    registrar_resultado_handler: RegistrarResultadoHandler,
    asignar_tarjeta_handler: AsignarTarjetaHandler,
    corregir_resultado_handler: CorregirResultadoHandler,
) -> None:
    """INV-P-12: MotivoObligatorio si motivo está vacío."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_en_ejecutada(
        registrar_ap_handler,
        llamar_handler,
        registrar_resultado_handler,
        asignar_tarjeta_handler,
        cid,
        pid,
    )

    with pytest.raises(MotivoObligatorio):
        await corregir_resultado_handler.handle(
            CorregirResultadoCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.STA,
                valor_rp=Decimal("90.0"),
                unidad=UnidadMedida.Segundos,
                registrado_por="juez-001",
                motivo="",
            )
        )
