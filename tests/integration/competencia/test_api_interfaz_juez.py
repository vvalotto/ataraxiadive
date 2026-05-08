"""Tests de integración — API interfaz del juez con SQLiteEventStore real."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from app import app
from competencia.api.router import get_event_store, get_obtener_proximas_performances_handler
from competencia.application.queries.obtener_proximas_performances import (
    ObtenerProximasPerformancesHandler,
)
from tests.integration.competencia._stubs import StubAtletaNombrePort

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
async def store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    db_path = str(tmp_path / "competencia_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def client(store: SQLiteEventStore) -> TestClient:
    stub_nombre = StubAtletaNombrePort()
    app.dependency_overrides[get_event_store] = lambda: store
    app.dependency_overrides[get_obtener_proximas_performances_handler] = (
        lambda: ObtenerProximasPerformancesHandler(store, stub_nombre)
    )
    yield TestClient(app)
    app.dependency_overrides.clear()


async def _registrar_ap(
    store: SQLiteEventStore, competencia_id: UUID, participante_id: UUID
) -> UUID:
    handler = RegistrarAPHandler(
        store, StubCompetenciaEstadoAdapter(), DisciplinaDescriptorAdapter()
    )
    return await handler.handle(
        RegistrarAPCommand(
            competencia_id=competencia_id,
            participante_id=participante_id,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal("50"),
            unidad=UnidadMedida.Metros,
        )
    )


async def _llamar(
    store: SQLiteEventStore,
    competencia_id: UUID,
    participante_id: UUID,
    posicion: int,
) -> None:
    from datetime import datetime, timezone

    handler = LlamarAtletaHandler(store, StubCompetenciaEstadoAdapter())
    await handler.handle(
        LlamarAtletaCommand(
            competencia_id=competencia_id,
            participante_id=participante_id,
            disciplina=Disciplina.DNF,
            ot_programado=datetime.now(timezone.utc),
            posicion_grilla=posicion,
        )
    )


async def _ejecutar(store: SQLiteEventStore, competencia_id: UUID, participante_id: UUID) -> None:
    handler_r = RegistrarResultadoHandler(store, DisciplinaDescriptorAdapter())
    await handler_r.handle(
        RegistrarResultadoCommand(
            competencia_id=competencia_id,
            participante_id=participante_id,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("48"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-001",
        )
    )
    handler_t = AsignarTarjetaHandler(store)
    await handler_t.handle(
        AsignarTarjetaCommand(
            competencia_id=competencia_id,
            participante_id=participante_id,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez-001",
        )
    )


async def _dns(store: SQLiteEventStore, competencia_id: UUID, participante_id: UUID) -> None:
    handler = RegistrarDNSHandler(store)
    await handler.handle(
        RegistrarDNSCommand(
            competencia_id=competencia_id,
            participante_id=participante_id,
            disciplina=Disciplina.DNF,
            registrado_por="juez-001",
        )
    )


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_performance_actual_retorna_atleta_en_llamada(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid = uuid4()
    p1 = uuid4()
    p2 = uuid4()

    await _registrar_ap(store, cid, p1)
    await _registrar_ap(store, cid, p2)
    await _llamar(store, cid, p1, posicion=1)

    response = client.get(f"/competencia/{cid}/performance/actual")

    assert response.status_code == 200
    data = response.json()
    assert data is not None
    assert data["estado"] == "Llamada"
    assert data["andarivel"] == 1
    assert data["ap_declarado"] == "50"


@pytest.mark.asyncio
async def test_proximas_retorna_atletas_en_anunciada_ap(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid = uuid4()
    participantes = [uuid4() for _ in range(5)]

    for p in participantes:
        await _registrar_ap(store, cid, p)
    await _llamar(store, cid, participantes[0], posicion=1)
    await _llamar(store, cid, participantes[1], posicion=2)

    response = client.get(f"/competencia/{cid}/performance/proximas?disciplina=DNF")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    for item in data:
        assert "posicion" in item
        assert "nombre_atleta" in item
        assert "ap_declarado" in item


@pytest.mark.asyncio
async def test_progreso_conteo_correcto(store: SQLiteEventStore, client: TestClient) -> None:
    cid = uuid4()
    p1, p2, p3, p4 = [uuid4() for _ in range(4)]

    for p in [p1, p2, p3, p4]:
        await _registrar_ap(store, cid, p)
    await _llamar(store, cid, p1, 1)
    await _ejecutar(store, cid, p1)
    await _llamar(store, cid, p2, 2)
    await _ejecutar(store, cid, p2)
    await _llamar(store, cid, p3, 3)
    await _dns(store, cid, p3)

    response = client.get(f"/competencia/{cid}/progreso")

    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 4
    assert data["ejecutadas"] == 2
    assert data["dns_count"] == 1
    assert data["completadas"] == 3


@pytest.mark.asyncio
async def test_competencia_sin_performances_retorna_estructuras_vacias(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid = uuid4()

    r1 = client.get(f"/competencia/{cid}/performance/actual")
    assert r1.status_code == 200
    assert r1.json() is None

    r2 = client.get(f"/competencia/{cid}/performance/proximas?disciplina=DNF")
    assert r2.status_code == 200
    assert r2.json() == []

    r3 = client.get(f"/competencia/{cid}/progreso")
    assert r3.status_code == 200
    data = r3.json()
    assert data["total"] == 0
    assert data["completadas"] == 0
