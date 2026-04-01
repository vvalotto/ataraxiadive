"""Test de integración E2E — US-1.4.2: Flujo completo AP → Tarjeta.

Verifica el DoD de SP1: 5 performances ejecutadas desde el celular,
Event Store con traza completa, Read Models consistentes.

Atletas del escenario:
  A: AP 60m → Llamar → Resultado 60m → Tarjeta blanca
  B: AP 40m → Llamar → DNS
  C: AP 80m → Llamar → Resultado 72m → Tarjeta amarilla
  D: AP 50m → Llamar → Resultado 55m → Tarjeta blanca → Corregir 53m
  E: AP 90m → Llamar → Resultado 90m → Tarjeta roja (black-out, distancia 45m)
"""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from app import app
from competencia.api.router import get_event_store
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
from competencia.application.commands.registrar_dns import RegistrarDNSCommand, RegistrarDNSHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

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

_DISCIPLINA = Disciplina.STA
_JUEZ = "juez-001"
_OT = datetime.now(timezone.utc)


@pytest.fixture
async def store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    db_path = str(tmp_path / "e2e_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def client(store: SQLiteEventStore) -> TestClient:
    app.dependency_overrides[get_event_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


# ── Helpers para ejecutar el flujo ─────────────────────────────────────────


async def _ap(store: SQLiteEventStore, cid: UUID, pid: UUID, valor: str) -> None:
    await RegistrarAPHandler(
        store, StubCompetenciaEstadoAdapter(), DisciplinaDescriptorAdapter()
    ).handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Segundos,
        )
    )


async def _llamar(store: SQLiteEventStore, cid: UUID, pid: UUID, pos: int) -> None:
    await LlamarAtletaHandler(store, StubCompetenciaEstadoAdapter()).handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            ot_programado=_OT,
            posicion_grilla=pos,
        )
    )


async def _resultado(store: SQLiteEventStore, cid: UUID, pid: UUID, valor: str) -> None:
    await RegistrarResultadoHandler(store, DisciplinaDescriptorAdapter()).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
        )
    )


async def _tarjeta_blanca(store: SQLiteEventStore, cid: UUID, pid: UUID) -> None:
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Blanca,
            asignada_por=_JUEZ,
        )
    )


async def _tarjeta_amarilla(store: SQLiteEventStore, cid: UUID, pid: UUID) -> None:
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Amarilla,
            asignada_por=_JUEZ,
            motivo="sin superficie",
        )
    )


async def _tarjeta_blackout(store: SQLiteEventStore, cid: UUID, pid: UUID, distancia: str) -> None:
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            tipo=TipoTarjeta.Roja,
            asignada_por=_JUEZ,
            motivo="black-out",
            distancia_blackout=Decimal(distancia),
        )
    )


async def _dns(store: SQLiteEventStore, cid: UUID, pid: UUID) -> None:
    await RegistrarDNSHandler(store).handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            registrado_por=_JUEZ,
        )
    )


async def _corregir(store: SQLiteEventStore, cid: UUID, pid: UUID, valor: str, motivo: str) -> None:
    await CorregirResultadoHandler(store).handle(
        CorregirResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Segundos,
            registrado_por=_JUEZ,
            motivo=motivo,
        )
    )


async def _ejecutar_flujo_completo(
    store: SQLiteEventStore,
) -> tuple[UUID, UUID, UUID, UUID, UUID, UUID]:
    """Ejecuta el flujo DoD SP1 con 5 atletas y retorna (cid, pid_a, pid_b, pid_c, pid_d, pid_e)."""
    cid = uuid4()
    pid_a, pid_b, pid_c, pid_d, pid_e = [uuid4() for _ in range(5)]

    # Registrar APs
    await _ap(store, cid, pid_a, "60")
    await _ap(store, cid, pid_b, "40")
    await _ap(store, cid, pid_c, "80")
    await _ap(store, cid, pid_d, "50")
    await _ap(store, cid, pid_e, "90")

    # A: flujo completo → tarjeta blanca
    await _llamar(store, cid, pid_a, 1)
    await _resultado(store, cid, pid_a, "60")
    await _tarjeta_blanca(store, cid, pid_a)

    # B: DNS
    await _llamar(store, cid, pid_b, 2)
    await _dns(store, cid, pid_b)

    # C: tarjeta amarilla
    await _llamar(store, cid, pid_c, 3)
    await _resultado(store, cid, pid_c, "72")
    await _tarjeta_amarilla(store, cid, pid_c)

    # D: tarjeta blanca + corrección de resultado
    await _llamar(store, cid, pid_d, 4)
    await _resultado(store, cid, pid_d, "55")
    await _tarjeta_blanca(store, cid, pid_d)
    await _corregir(store, cid, pid_d, "53", "error de lectura")

    # E: black-out con distancia
    await _llamar(store, cid, pid_e, 5)
    await _resultado(store, cid, pid_e, "90")
    await _tarjeta_blackout(store, cid, pid_e, "45")

    return cid, pid_a, pid_b, pid_c, pid_d, pid_e


# ── Tests ──────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_events_retorna_traza_completa(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid, *_ = await _ejecutar_flujo_completo(store)

    response = client.get(f"/competencia/{cid}/events")

    assert response.status_code == 200
    data = response.json()
    assert data["competencia_id"] == str(cid)
    assert data["total_events"] >= 15
    assert len(data["events"]) == data["total_events"]


@pytest.mark.asyncio
async def test_get_events_orden_de_secuencia(store: SQLiteEventStore, client: TestClient) -> None:
    cid, *_ = await _ejecutar_flujo_completo(store)

    response = client.get(f"/competencia/{cid}/events")
    events = response.json()["events"]

    sequences = [e["sequence"] for e in events]
    assert sequences == sorted(sequences), "Los eventos deben estar en orden de secuencia"


@pytest.mark.asyncio
async def test_get_events_campos_obligatorios(store: SQLiteEventStore, client: TestClient) -> None:
    cid, *_ = await _ejecutar_flujo_completo(store)

    response = client.get(f"/competencia/{cid}/events")
    events = response.json()["events"]

    for event in events:
        assert "sequence" in event
        assert "event_type" in event
        assert "performance_id" in event
        assert "occurred_at" in event
        assert "data" in event


@pytest.mark.asyncio
async def test_get_events_incluye_tipos_esperados(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid, *_ = await _ejecutar_flujo_completo(store)

    response = client.get(f"/competencia/{cid}/events")
    event_types = {e["event_type"] for e in response.json()["events"]}

    assert "APRegistrado" in event_types
    assert "AtletaLlamado" in event_types
    assert "ResultadoRegistrado" in event_types
    assert "TarjetaAsignada" in event_types
    assert "DNSRegistrado" in event_types
    assert "ResultadoCorregido" in event_types


@pytest.mark.asyncio
async def test_progreso_consistente_con_event_store(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid, *_ = await _ejecutar_flujo_completo(store)

    r_progreso = client.get(f"/competencia/{cid}/progreso")
    assert r_progreso.status_code == 200
    progreso = r_progreso.json()

    assert progreso["total"] == 5
    assert progreso["ejecutadas"] == 4  # A, C, D, E (B es DNS)
    assert progreso["dns_count"] == 1
    assert progreso["completadas"] == 5


@pytest.mark.asyncio
async def test_blackout_con_distancia_en_event_store(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid, _, _, _, _, pid_e = await _ejecutar_flujo_completo(store)

    response = client.get(f"/competencia/{cid}/events")
    events = response.json()["events"]

    blackout_events = [
        e
        for e in events
        if e["event_type"] == "TarjetaAsignada" and e["data"].get("motivo") == "black-out"
    ]
    # stream_id = "performance-{competencia_id}-{participante_id}-{disciplina}"
    # performance_id en el DTO es "{participante_id}-{disciplina}" (sufijo post-prefijo)
    assert len(blackout_events) == 1
    assert blackout_events[0]["data"]["distancia_blackout"] == "45"
    assert blackout_events[0]["performance_id"].startswith(str(pid_e))


@pytest.mark.asyncio
async def test_get_events_sin_eventos_retorna_lista_vacia(
    store: SQLiteEventStore, client: TestClient
) -> None:
    cid = uuid4()

    response = client.get(f"/competencia/{cid}/events")

    assert response.status_code == 200
    data = response.json()
    assert data["total_events"] == 0
    assert data["events"] == []
