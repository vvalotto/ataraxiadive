"""Tests de integracion — corregir resultado tras DNS."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from app import app
from competencia.api.router import get_event_store
from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.corregir_resultado_tras_dns import (
    CorregirResultadoTrasDNSCommand,
    CorregirResultadoTrasDNSHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import EstadoInvalidoParaCorregirResultadoTrasDNS
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from identidad.api.dependencies import get_current_user

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
    db_path = str(tmp_path / "competencia_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def client(event_store: SQLiteEventStore) -> TestClient:
    app.dependency_overrides[get_event_store] = lambda: event_store
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "juez-001",
        "email": "juez@test.com",
        "rol": "JUEZ",
    }
    yield TestClient(app)
    app.dependency_overrides.clear()


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
def dns_handler(event_store: SQLiteEventStore) -> RegistrarDNSHandler:
    return RegistrarDNSHandler(event_store=event_store)


@pytest.fixture
def corregir_handler(event_store: SQLiteEventStore) -> CorregirResultadoTrasDNSHandler:
    return CorregirResultadoTrasDNSHandler(event_store=event_store)


@pytest.fixture
def tarjeta_handler(event_store: SQLiteEventStore) -> AsignarTarjetaHandler:
    return AsignarTarjetaHandler(event_store=event_store)


async def _setup_performance_en_dns(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    dns_handler: RegistrarDNSHandler,
    cid: object,
    pid: object,
) -> None:
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
    await dns_handler.handle(
        RegistrarDNSCommand(
            competencia_id=cid,  # type: ignore[arg-type]
            participante_id=pid,  # type: ignore[arg-type]
            disciplina=Disciplina.DNF,
            registrado_por="juez-001",
        )
    )


async def test_flujo_dns_corregido_permanece_apto_para_tarjeta(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    dns_handler: RegistrarDNSHandler,
    corregir_handler: CorregirResultadoTrasDNSHandler,
    tarjeta_handler: AsignarTarjetaHandler,
    event_store: SQLiteEventStore,
) -> None:
    cid = uuid4()
    pid = uuid4()
    await _setup_performance_en_dns(registrar_ap_handler, llamar_handler, dns_handler, cid, pid)

    await corregir_handler.handle(
        CorregirResultadoTrasDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("50.25"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-002",
            motivo_correccion="DNS cargado por error",
        )
    )
    await tarjeta_handler.handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-002",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.DNF.value}"
    events = await event_store.load(stream_id)
    assert [event["event_type"] for event in events] == [
        "APRegistrado",
        "AtletaLlamado",
        "DNSRegistrado",
        "ResultadoCorregidoTrasDNS",
        "TarjetaAsignada",
    ]
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance.Ejecutada
    assert performance.rp == Decimal("50.25")


async def test_corregir_resultado_tras_dns_no_cierra_competencia_por_p08(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    dns_handler: RegistrarDNSHandler,
    corregir_handler: CorregirResultadoTrasDNSHandler,
    event_store: SQLiteEventStore,
) -> None:
    cid = uuid4()
    pid = uuid4()
    await _setup_performance_en_dns(registrar_ap_handler, llamar_handler, dns_handler, cid, pid)

    await corregir_handler.handle(
        CorregirResultadoTrasDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("50.25"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-002",
            motivo_correccion="DNS cargado por error",
        )
    )

    stream_id = f"performance-{cid}-{pid}-{Disciplina.DNF.value}"
    events = await event_store.load(stream_id)
    assert events[-1]["event_type"] == "ResultadoCorregidoTrasDNS"
    assert all(event["event_type"] != "CompetenciaFinalizada" for event in events)


async def test_corregir_resultado_tras_dns_desde_llamada_lanza_error(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    corregir_handler: CorregirResultadoTrasDNSHandler,
) -> None:
    cid = uuid4()
    pid = uuid4()
    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal("50"),
            unidad=UnidadMedida.Metros,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )

    with pytest.raises(EstadoInvalidoParaCorregirResultadoTrasDNS):
        await corregir_handler.handle(
            CorregirResultadoTrasDNSCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.DNF,
                valor_rp=Decimal("50.25"),
                unidad=UnidadMedida.Metros,
                registrado_por="juez-002",
                motivo_correccion="DNS cargado por error",
            )
        )


@pytest.mark.asyncio
async def test_api_corrige_resultado_tras_dns(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    dns_handler: RegistrarDNSHandler,
    event_store: SQLiteEventStore,
    client: TestClient,
) -> None:
    cid = uuid4()
    pid = uuid4()
    performance_id = uuid4()
    await _setup_performance_en_dns(registrar_ap_handler, llamar_handler, dns_handler, cid, pid)

    response = client.post(
        f"/competencia/{cid}/performances/{performance_id}/corregir-resultado-tras-dns",
        json={
            "participante_id": str(pid),
            "disciplina": Disciplina.DNF.value,
            "valor_rp": "50.25",
            "unidad": UnidadMedida.Metros.value,
            "motivo_correccion": "DNS cargado por error",
        },
    )

    assert response.status_code == 204
    stream_id = f"performance-{cid}-{pid}-{Disciplina.DNF.value}"
    events = await event_store.load(stream_id)
    assert events[-1]["event_type"] == "ResultadoCorregidoTrasDNS"
    assert events[-1]["payload"]["registrado_por"] == "juez@test.com"


@pytest.mark.asyncio
async def test_api_corregir_resultado_tras_dns_desde_llamada_retorna_409(
    registrar_ap_handler: RegistrarAPHandler,
    llamar_handler: LlamarAtletaHandler,
    client: TestClient,
) -> None:
    cid = uuid4()
    pid = uuid4()
    performance_id = uuid4()
    await registrar_ap_handler.handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal("50"),
            unidad=UnidadMedida.Metros,
        )
    )
    await llamar_handler.handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=Disciplina.DNF,
            ot_programado=OT,
            posicion_grilla=1,
        )
    )

    response = client.post(
        f"/competencia/{cid}/performances/{performance_id}/corregir-resultado-tras-dns",
        json={
            "participante_id": str(pid),
            "disciplina": Disciplina.DNF.value,
            "valor_rp": "50.25",
            "unidad": UnidadMedida.Metros.value,
            "motivo_correccion": "DNS cargado por error",
        },
    )

    assert response.status_code == 409
