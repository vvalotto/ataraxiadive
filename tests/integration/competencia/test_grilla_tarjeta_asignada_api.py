"""Tests de integración API — tarjeta_asignada en /grilla."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

import aiosqlite
import pytest
from fastapi.testclient import TestClient

from app import app
from competencia.api.router import get_event_store
from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
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

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000721")
ATLETA_CON_TARJETA = UUID("00000000-0000-0000-0000-000000000731")
ATLETA_SIN_TARJETA = UUID("00000000-0000-0000-0000-000000000732")
OT_INICIO = datetime(2026, 4, 19, 10, 0, tzinfo=timezone.utc)


@pytest.fixture
async def store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    db_path = str(tmp_path / "competencia_test.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
def client(store: SQLiteEventStore) -> TestClient:
    app.dependency_overrides[get_event_store] = lambda: store
    yield TestClient(app)
    app.dependency_overrides.clear()


async def _registrar_ap(store: SQLiteEventStore, atleta_id: UUID, valor: str) -> None:
    await RegistrarAPHandler(
        store,
        StubCompetenciaEstadoAdapter(),
        DisciplinaDescriptorAdapter(),
    ).handle(
        RegistrarAPCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Metros,
        )
    )


async def _seed_grilla(store: SQLiteEventStore) -> None:
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=Disciplina.DNF,
            intervalo_minutos=8,
            configurado_por="org",
        )
    )
    await _registrar_ap(store, ATLETA_CON_TARJETA, "50")
    await _registrar_ap(store, ATLETA_SIN_TARJETA, "60")
    await GenerarGrillaHandler(
        store,
        PerformancesAPAdapter(store),
        DisciplinaDescriptorAdapter(),
    ).handle(
        GenerarGrillaCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=Disciplina.DNF,
            ot_inicio=OT_INICIO,
        )
    )


async def _ejecutar_con_tarjeta(store: SQLiteEventStore) -> None:
    await LlamarAtletaHandler(store, StubCompetenciaEstadoAdapter()).handle(
        LlamarAtletaCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=ATLETA_CON_TARJETA,
            disciplina=Disciplina.DNF,
            ot_programado=OT_INICIO,
            posicion_grilla=1,
        )
    )
    await RegistrarResultadoHandler(store, DisciplinaDescriptorAdapter()).handle(
        RegistrarResultadoCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=ATLETA_CON_TARJETA,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("48"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez",
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=ATLETA_CON_TARJETA,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez",
        )
    )


@pytest.mark.asyncio
async def test_get_grilla_serializa_tarjeta_asignada(
    store: SQLiteEventStore,
    client: TestClient,
) -> None:
    await _seed_grilla(store)
    await _ejecutar_con_tarjeta(store)

    response = client.get(f"/competencia/{COMPETENCIA_ID}/grilla?disciplina=DNF")

    assert response.status_code == 200
    por_atleta = {item["atleta_id"]: item for item in response.json()}
    assert por_atleta[str(ATLETA_CON_TARJETA)]["tarjeta_asignada"] == "Blanca"
    assert por_atleta[str(ATLETA_SIN_TARJETA)]["tarjeta_asignada"] is None
