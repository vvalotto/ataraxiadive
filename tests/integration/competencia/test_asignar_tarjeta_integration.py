"""Tests de integración — AsignarTarjetaHandler con SQLiteEventStore real."""
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
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import (
    EstadoInvalidoParaAsignarTarjeta,
    MotivoObligatorio,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
OT = datetime(2026, 3, 22, 10, 30, 0)

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
def resultado_handler(event_store: SQLiteEventStore) -> RegistrarResultadoHandler:
    return RegistrarResultadoHandler(event_store=event_store, disciplina_descriptor=DisciplinaDescriptorAdapter())


@pytest.fixture
def tarjeta_handler(event_store: SQLiteEventStore) -> AsignarTarjetaHandler:
    return AsignarTarjetaHandler(event_store=event_store)


async def _setup_performance_con_resultado(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    cid: object,
    pid: object,
) -> None:
    """Lleva una Performance hasta el estado ResultadoRegistrado."""
    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.DNF,
            valor_ap=Decimal("50"),
            unidad=UnidadMedida.Metros,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.DNF,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )
    await resultado_handler.handle(
        RegistrarResultadoCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("50.5"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-001",
        )
    )


# ── Flujo completo ────────────────────────────────────────────────────────────


async def test_flujo_completo_hasta_ejecutada(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    tarjeta_handler: AsignarTarjetaHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Flujo completo: RegistrarAP → LlamarAtleta → RegistrarResultado → AsignarTarjeta(Blanca)."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_con_resultado(
        registrar_ap_handler, llamar_handler, resultado_handler, cid, pid
    )

    await tarjeta_handler.handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-001",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.DNF.value}"
    events = await event_store.load(stream_id)
    assert len(events) == 4
    assert events[3]["event_type"] == "TarjetaAsignada"

    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.Ejecutada
    assert performance.tarjeta == TipoTarjeta.Blanca


async def test_tarjeta_asignada_payload_correcto(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    tarjeta_handler: AsignarTarjetaHandler,
    event_store: SQLiteEventStore,
) -> None:
    """El payload de TarjetaAsignada contiene tipo, motivo y asignadaPor correctos."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_con_resultado(
        registrar_ap_handler, llamar_handler, resultado_handler, cid, pid
    )

    await tarjeta_handler.handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Roja,
            asignada_por="juez-007",
            motivo="tiempo excedido",
        )
    )

    stream_id = f"performance-{cid}-{pid}-DNF"
    events = await event_store.load(stream_id)
    payload = events[3]["payload"]
    assert payload["tipo"] == "Roja"
    assert payload["motivo"] == "tiempo excedido"
    assert payload["asignada_por"] == "juez-007"


# ── INV-P-07 ──────────────────────────────────────────────────────────────────


async def test_asignar_tarjeta_desde_llamada_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    tarjeta_handler: AsignarTarjetaHandler,
) -> None:
    """INV-P-07: EstadoInvalidoParaAsignarTarjeta si Performance en Llamada."""
    cid = uuid4()
    pid = uuid4()

    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, valor_ap=Decimal("50"), unidad=UnidadMedida.Metros,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, ot_programado=OT, posicion_grilla=1,
        )
    )

    with pytest.raises(EstadoInvalidoParaAsignarTarjeta):
        await tarjeta_handler.handle(
            AsignarTarjetaCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF, tipo=TipoTarjeta.Blanca, asignada_por="juez-001",
            )
        )


# ── INV-P-11 ──────────────────────────────────────────────────────────────────


async def test_tarjeta_amarilla_sin_motivo_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    tarjeta_handler: AsignarTarjetaHandler,
) -> None:
    """INV-P-11: MotivoObligatorio si tarjeta Amarilla sin motivo."""
    cid = uuid4()
    pid = uuid4()

    await _setup_performance_con_resultado(
        registrar_ap_handler, llamar_handler, resultado_handler, cid, pid
    )

    with pytest.raises(MotivoObligatorio):
        await tarjeta_handler.handle(
            AsignarTarjetaCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF, tipo=TipoTarjeta.Amarilla, asignada_por="juez-001",
            )
        )


# ── US-1.4.1: black-out con distancia ────────────────────────────────────────


@pytest.mark.asyncio
async def test_blackout_persiste_y_reconstitye_distancia(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    tarjeta_handler: AsignarTarjetaHandler,
    event_store: SQLiteEventStore,
) -> None:
    """Black-out con distancia se persiste en SQLite y se reconstituye correctamente."""
    from competencia.domain.aggregates.performance import DistanciaBlackoutObligatoria

    cid = uuid4()
    pid = uuid4()

    await _setup_performance_con_resultado(
        registrar_ap_handler, llamar_handler, resultado_handler, cid, pid
    )
    await tarjeta_handler.handle(
        AsignarTarjetaCommand(
            competencia_id=cid, participante_id=pid,
            disciplina=Disciplina.DNF, tipo=TipoTarjeta.Roja,
            asignada_por="juez-001", motivo="black-out",
            distancia_blackout=Decimal("45.5"),
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.DNF.value}"
    events = await event_store.load(stream_id)
    performance = Performance.reconstitute(events)

    assert performance.estado == EstadoPerformance.Ejecutada
    assert performance.distancia_blackout == Decimal("45.5")
    assert performance.tarjeta == TipoTarjeta.Roja


@pytest.mark.asyncio
async def test_blackout_sin_distancia_rechazado_en_integracion(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    resultado_handler: RegistrarResultadoHandler,
    tarjeta_handler: AsignarTarjetaHandler,
) -> None:
    """Black-out sin distancia es rechazado — no persiste ningún evento extra."""
    from competencia.domain.aggregates.performance import DistanciaBlackoutObligatoria

    cid = uuid4()
    pid = uuid4()

    await _setup_performance_con_resultado(
        registrar_ap_handler, llamar_handler, resultado_handler, cid, pid
    )

    with pytest.raises(DistanciaBlackoutObligatoria):
        await tarjeta_handler.handle(
            AsignarTarjetaCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=Disciplina.DNF, tipo=TipoTarjeta.Roja,
                asignada_por="juez-001", motivo="black-out",
            )
        )
