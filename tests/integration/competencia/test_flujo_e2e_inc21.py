"""Test de integración E2E — Inc 2.1: Juez avanza por la grilla atleta a atleta.

DoD observable de Inc 2.1:
  - Grilla generada con orden correcto (AP STA: mayor a menor)
  - Juez confirma grilla → inicia competencia → avanza atleta por atleta
  - CompetenciaEstadoAdapter REAL lee del Event Store (no stub)

Escenario: disciplina STA con 3 atletas
  Atleta A: AP 300s (5 min) → posición 1 (mayor AP primero en STA)
  Atleta B: AP 180s (3 min) → posición 2
  Atleta C: AP 120s (2 min) → posición 3
  Flujo: generar → confirmar → iniciar → llamar A → llamar B → llamar C
"""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest

from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.application.commands.llamar_atleta import (
    LlamarAtletaCommand,
    LlamarAtletaHandler,
)
from competencia.application.commands.registrar_ap import (
    RegistrarAPCommand,
    RegistrarAPHandler,
)
from competencia.application.queries.obtener_grilla import (
    ObtenerGrillaHandler,
    ObtenerGrillaQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.competencia_estado_adapter import (
    CompetenciaEstadoAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import DisciplinaDescriptorAdapter
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

_DISCIPLINA = Disciplina.STA
_INTERVALO_MINUTOS = 9
_OT_INICIO = datetime(2026, 4, 1, 10, 0, 0, tzinfo=timezone.utc)
_JUEZ = "juez-dod-inc21"


@pytest.fixture
async def store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    db_path = str(tmp_path / "e2e_inc21.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


async def _setup_grilla_generada(
    store: SQLiteEventStore,
    competencia_id: UUID,
    atleta_a: UUID,
    atleta_b: UUID,
    atleta_c: UUID,
) -> None:
    """Configura intervalo, registra APs y genera la grilla."""
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=competencia_id,
            disciplina=_DISCIPLINA,
            intervalo_minutos=_INTERVALO_MINUTOS,
            configurado_por="org-01",
        )
    )
    stub = StubCompetenciaEstadoAdapter()
    ap_handler = RegistrarAPHandler(store, stub)
    for atleta_id, ap_segundos in [(atleta_a, "300"), (atleta_b, "180"), (atleta_c, "120")]:
        await ap_handler.handle(
            RegistrarAPCommand(
                competencia_id=competencia_id,
                participante_id=atleta_id,
                disciplina=_DISCIPLINA,
                valor_ap=Decimal(ap_segundos),
                unidad=UnidadMedida.Segundos,
            )
        )
    adapter = PerformancesAPAdapter(store)
    await GenerarGrillaHandler(store, adapter, DisciplinaDescriptorAdapter()).handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=_DISCIPLINA,
            ot_inicio=_OT_INICIO,
        )
    )


@pytest.mark.asyncio
async def test_grilla_generada_con_orden_correcto_sta(store: SQLiteEventStore) -> None:
    """STA ordena AP mayor a menor: A(300s) → B(180s) → C(120s)."""
    cid = uuid4()
    atleta_a, atleta_b, atleta_c = uuid4(), uuid4(), uuid4()

    await _setup_grilla_generada(store, cid, atleta_a, atleta_b, atleta_c)

    entradas = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid, disciplina=_DISCIPLINA)
    )

    assert len(entradas) == 3
    assert entradas[0].posicion == 1
    assert entradas[1].posicion == 2
    assert entradas[2].posicion == 3
    # STA: mayor AP primero → A(300s) en posición 1
    assert str(atleta_a) in entradas[0].atleta_id
    assert str(atleta_b) in entradas[1].atleta_id
    assert str(atleta_c) in entradas[2].atleta_id


@pytest.mark.asyncio
async def test_ots_calculados_con_intervalo_correcto(store: SQLiteEventStore) -> None:
    """Cada OT debe ser OT_inicio + (posición - 1) * intervalo."""
    from datetime import timedelta

    cid = uuid4()
    atleta_a, atleta_b, atleta_c = uuid4(), uuid4(), uuid4()

    await _setup_grilla_generada(store, cid, atleta_a, atleta_b, atleta_c)

    entradas = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid, disciplina=_DISCIPLINA)
    )

    expected_ots = [
        _OT_INICIO + timedelta(minutes=_INTERVALO_MINUTOS * 0),
        _OT_INICIO + timedelta(minutes=_INTERVALO_MINUTOS * 1),
        _OT_INICIO + timedelta(minutes=_INTERVALO_MINUTOS * 2),
    ]
    for i, entrada in enumerate(entradas):
        ot_actual = datetime.fromisoformat(entrada.ot_programado)
        assert ot_actual == expected_ots[i], f"Posición {i + 1}: OT incorrecto"


@pytest.mark.asyncio
async def test_juez_avanza_grilla_atleta_por_atleta_con_adapter_real(
    store: SQLiteEventStore,
) -> None:
    """DoD observable: grilla generada → confirmar → iniciar → juez llama 3 atletas en orden.

    Usa CompetenciaEstadoAdapter REAL (no stub) para verificar que LlamarAtletaHandler
    consulta el Event Store correctamente tras IniciarCompetencia.
    """
    cid = uuid4()
    atleta_a, atleta_b, atleta_c = uuid4(), uuid4(), uuid4()

    # 1. Setup: intervalo + APs + grilla generada
    await _setup_grilla_generada(store, cid, atleta_a, atleta_b, atleta_c)

    # 2. Obtener grilla para conocer orden y OTs reales
    entradas = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid, disciplina=_DISCIPLINA)
    )
    assert len(entradas) == 3

    # 3. Confirmar grilla
    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(competencia_id=cid, disciplina=_DISCIPLINA)
    )

    # 4. Iniciar competencia — persiste CompetenciaIniciada en el stream
    await IniciarCompetenciaHandler(store).handle(
        IniciarCompetenciaCommand(
            competencia_id=cid,
            disciplina=_DISCIPLINA,
            juez_id=_JUEZ,
        )
    )

    # 5. Adapter REAL: verifica que is_en_ejecucion lee el stream correctamente
    adapter = CompetenciaEstadoAdapter(store)
    assert await adapter.is_en_ejecucion(cid) is True
    assert await adapter.is_grilla_confirmada(cid, _DISCIPLINA) is True

    # 6. Juez avanza atleta por atleta usando el adapter real
    llamar_handler = LlamarAtletaHandler(store, adapter)
    for entrada in entradas:
        atleta_id = UUID(entrada.atleta_id)
        ot = datetime.fromisoformat(entrada.ot_programado)
        await llamar_handler.handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=atleta_id,
                disciplina=_DISCIPLINA,
                ot_programado=ot,
                posicion_grilla=entrada.posicion,
            )
        )

    # 7. Verificar que los 3 AtletaLlamado están en el stream de cada performance
    stream_competencia = f"competencia-{cid}"
    comp_events = await store.load(stream_competencia)
    comp_event_types = [e["event_type"] for e in comp_events]

    assert "IntervaloOTConfigurado" in comp_event_types
    assert "GrillaDeSalidaGenerada" in comp_event_types
    assert "GrillaConfirmada" in comp_event_types
    assert "CompetenciaIniciada" in comp_event_types

    # Verificar AtletaLlamado en cada stream de performance
    for entrada in entradas:
        atleta_id = UUID(entrada.atleta_id)
        stream_perf = f"performance-{cid}-{atleta_id}-{_DISCIPLINA.value}"
        perf_events = await store.load(stream_perf)
        perf_event_types = [e["event_type"] for e in perf_events]
        assert "APRegistrado" in perf_event_types, f"AP faltante para {atleta_id}"
        assert "AtletaLlamado" in perf_event_types, f"Llamado faltante para {atleta_id}"


@pytest.mark.asyncio
async def test_llamar_atleta_falla_si_competencia_no_iniciada(
    store: SQLiteEventStore,
) -> None:
    """LlamarAtleta rechazado si la competencia no fue iniciada (adapter real)."""
    from competencia.application.commands.llamar_atleta import CompetenciaNoEnEjecucion

    cid = uuid4()
    atleta_a, atleta_b, atleta_c = uuid4(), uuid4(), uuid4()

    await _setup_grilla_generada(store, cid, atleta_a, atleta_b, atleta_c)
    await ConfirmarGrillaHandler(store).handle(
        ConfirmarGrillaCommand(competencia_id=cid, disciplina=_DISCIPLINA)
    )
    # No se llama a IniciarCompetencia → adapter real retorna False

    entradas = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=cid, disciplina=_DISCIPLINA)
    )
    adapter = CompetenciaEstadoAdapter(store)
    llamar_handler = LlamarAtletaHandler(store, adapter)

    with pytest.raises(CompetenciaNoEnEjecucion):
        primera = entradas[0]
        await llamar_handler.handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=UUID(primera.atleta_id),
                disciplina=_DISCIPLINA,
                ot_programado=datetime.fromisoformat(primera.ot_programado),
                posicion_grilla=primera.posicion,
            )
        )
