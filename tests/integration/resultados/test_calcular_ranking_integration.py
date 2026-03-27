"""Tests de integración — CalcularRankingHandler + ObtenerRankingHandler (US-2.4.2)."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

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
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
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


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
async def comp_store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    """Event Store del BC Competencia (BD temporal)."""
    db_path = str(tmp_path / "competencia.db")
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()
    return SQLiteEventStore(db_path)


@pytest.fixture
async def ranking_store(tmp_path: pytest.TempPathFactory) -> SQLiteEventStore:
    """Event Store del BC Resultados (BD temporal)."""
    db_path = str(tmp_path / "resultados.db")
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


# ── Helpers de setup ──────────────────────────────────────────────────────────


async def _performance_ejecutada(
    comp_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
    cid: UUID,
    pid: UUID,
    rp_valor: str,
    disciplina: Disciplina = Disciplina.STA,
    ot: datetime = OT_A,
    tarjeta: TipoTarjeta = TipoTarjeta.Blanca,
    motivo: str | None = None,
) -> None:
    """Lleva una Performance hasta Ejecutada (TarjetaAsignada)."""
    unidad = UnidadMedida.Segundos if disciplina.es_tiempo() else UnidadMedida.Metros

    await RegistrarAPHandler(
        event_store=comp_store, competencia_estado=stub, disciplina_descriptor=descriptor
    ).handle(RegistrarAPCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=disciplina, valor_ap=Decimal(rp_valor), unidad=unidad,
    ))
    await LlamarAtletaHandler(
        event_store=comp_store, competencia_estado=stub
    ).handle(LlamarAtletaCommand(
        competencia_id=cid, participante_id=pid, disciplina=disciplina,
        posicion_grilla=1, ot_programado=ot,
    ))
    await RegistrarResultadoHandler(
        event_store=comp_store, disciplina_descriptor=descriptor
    ).handle(RegistrarResultadoCommand(
        competencia_id=cid, participante_id=pid, disciplina=disciplina,
        valor_rp=Decimal(rp_valor), unidad=unidad, registrado_por="juez-001",
    ))
    await AsignarTarjetaHandler(event_store=comp_store).handle(AsignarTarjetaCommand(
        competencia_id=cid, participante_id=pid, disciplina=disciplina,
        tipo=tarjeta, asignada_por="juez-001", motivo=motivo,
    ))


async def _performance_dns(
    comp_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
    cid: UUID,
    pid: UUID,
    disciplina: Disciplina = Disciplina.STA,
) -> None:
    """Lleva una Performance hasta DNS."""
    unidad = UnidadMedida.Segundos if disciplina.es_tiempo() else UnidadMedida.Metros

    await RegistrarAPHandler(
        event_store=comp_store, competencia_estado=stub, disciplina_descriptor=descriptor
    ).handle(RegistrarAPCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=disciplina, valor_ap=Decimal("200"), unidad=unidad,
    ))
    await LlamarAtletaHandler(
        event_store=comp_store, competencia_estado=stub
    ).handle(LlamarAtletaCommand(
        competencia_id=cid, participante_id=pid, disciplina=disciplina,
        posicion_grilla=1, ot_programado=OT_A,
    ))
    await RegistrarDNSHandler(event_store=comp_store).handle(RegistrarDNSCommand(
        competencia_id=cid, participante_id=pid,
        disciplina=disciplina, registrado_por="juez-001",
    ))


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_calcular_ranking_persiste_y_query_devuelve_orden_correcto(
    comp_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """Flujo completo: 3 performances → ranking calculado → query retorna orden."""
    cid = uuid4()
    pid_1 = uuid4()  # 330s — debe quedar 1°
    pid_2 = uuid4()  # 200s — debe quedar 2°
    pid_3 = uuid4()  # 150s — debe quedar 3°

    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_1, "330", ot=OT_A)
    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_2, "200", ot=OT_B)
    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_3, "150", ot=OT_C)

    acl = ResultadosCompetenciaAdapter(comp_store)
    handler = CalcularRankingHandler(
        ranking_store=ranking_store, resultados_port=acl, descriptor=descriptor
    )
    await handler.handle(CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA))

    query_handler = ObtenerRankingHandler(ranking_store=ranking_store)
    entries = await query_handler.handle(
        ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.STA)
    )

    assert len(entries) == 3
    assert entries[0].atleta_id == str(pid_1)
    assert entries[0].posicion == 1
    assert entries[0].en_podio is True
    assert entries[1].atleta_id == str(pid_2)
    assert entries[1].posicion == 2
    assert entries[2].atleta_id == str(pid_3)
    assert entries[2].posicion == 3


@pytest.mark.asyncio
async def test_calcular_ranking_dns_va_al_final(
    comp_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """DNS aparece al final del ranking, sin marca."""
    cid = uuid4()
    pid_valido = uuid4()
    pid_dns = uuid4()

    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_valido, "300", ot=OT_A)
    await _performance_dns(comp_store, stub, descriptor, cid, pid_dns)

    acl = ResultadosCompetenciaAdapter(comp_store)
    handler = CalcularRankingHandler(
        ranking_store=ranking_store, resultados_port=acl, descriptor=descriptor
    )
    await handler.handle(CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA))

    query_handler = ObtenerRankingHandler(ranking_store=ranking_store)
    entries = await query_handler.handle(
        ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.STA)
    )

    assert len(entries) == 2
    assert entries[0].atleta_id == str(pid_valido)
    assert entries[0].posicion == 1
    assert entries[1].atleta_id == str(pid_dns)
    assert entries[1].es_dns is True
    assert entries[1].rp is None
    assert entries[1].en_podio is False


@pytest.mark.asyncio
async def test_calcular_ranking_tarjeta_roja_va_al_final(
    comp_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """Tarjeta roja aparece al final del ranking."""
    cid = uuid4()
    pid_blanca = uuid4()
    pid_roja = uuid4()

    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_blanca, "300", ot=OT_A)
    await _performance_ejecutada(
        comp_store, stub, descriptor, cid, pid_roja, "250", ot=OT_B,
        tarjeta=TipoTarjeta.Roja, motivo="BO",
    )

    acl = ResultadosCompetenciaAdapter(comp_store)
    handler = CalcularRankingHandler(
        ranking_store=ranking_store, resultados_port=acl, descriptor=descriptor
    )
    await handler.handle(CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA))

    query_handler = ObtenerRankingHandler(ranking_store=ranking_store)
    entries = await query_handler.handle(
        ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.STA)
    )

    assert entries[0].atleta_id == str(pid_blanca)
    assert entries[0].tarjeta == "Blanca"
    assert entries[1].atleta_id == str(pid_roja)
    assert entries[1].tarjeta == "Roja"
    assert entries[1].en_podio is False


@pytest.mark.asyncio
async def test_calcular_ranking_empate_posicion_compartida(
    comp_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """Dos atletas con el mismo RP comparten posición y el siguiente salta."""
    cid = uuid4()
    pid_1a = uuid4()
    pid_1b = uuid4()
    pid_3 = uuid4()

    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_1a, "300", ot=OT_A)
    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_1b, "300", ot=OT_B)
    await _performance_ejecutada(comp_store, stub, descriptor, cid, pid_3, "200", ot=OT_C)

    acl = ResultadosCompetenciaAdapter(comp_store)
    handler = CalcularRankingHandler(
        ranking_store=ranking_store, resultados_port=acl, descriptor=descriptor
    )
    await handler.handle(CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.STA))

    query_handler = ObtenerRankingHandler(ranking_store=ranking_store)
    entries = await query_handler.handle(
        ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.STA)
    )

    pos_1_entries = [e for e in entries if e.posicion == 1]
    pos_3_entries = [e for e in entries if e.posicion == 3]
    pos_2_entries = [e for e in entries if e.posicion == 2]

    assert len(pos_1_entries) == 2
    assert len(pos_2_entries) == 0  # posición 2 omitida
    assert len(pos_3_entries) == 1
    assert pos_3_entries[0].atleta_id == str(pid_3)


@pytest.mark.asyncio
async def test_obtener_ranking_sin_calcular_devuelve_lista_vacia(
    ranking_store: SQLiteEventStore,
) -> None:
    """ObtenerRankingHandler devuelve lista vacía si no se calculó aún."""
    query_handler = ObtenerRankingHandler(ranking_store=ranking_store)
    entries = await query_handler.handle(
        ObtenerRankingQuery(competencia_id=uuid4(), disciplina=Disciplina.STA)
    )
    assert entries == []


@pytest.mark.asyncio
async def test_calcular_ranking_disciplina_dnf(
    comp_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
) -> None:
    """El ranking funciona para disciplinas de distancia (DNF, unidad=Metros)."""
    cid = uuid4()
    pid_1 = uuid4()  # 75m — 1°
    pid_2 = uuid4()  # 50m — 2°

    await _performance_ejecutada(
        comp_store, stub, descriptor, cid, pid_1, "75", disciplina=Disciplina.DNF, ot=OT_A
    )
    await _performance_ejecutada(
        comp_store, stub, descriptor, cid, pid_2, "50", disciplina=Disciplina.DNF, ot=OT_B
    )

    acl = ResultadosCompetenciaAdapter(comp_store)
    handler = CalcularRankingHandler(
        ranking_store=ranking_store, resultados_port=acl, descriptor=descriptor
    )
    await handler.handle(CalcularRankingCommand(competencia_id=cid, disciplina=Disciplina.DNF))

    query_handler = ObtenerRankingHandler(ranking_store=ranking_store)
    entries = await query_handler.handle(
        ObtenerRankingQuery(competencia_id=cid, disciplina=Disciplina.DNF)
    )

    assert len(entries) == 2
    assert entries[0].atleta_id == str(pid_1)
    assert entries[0].posicion == 1
    assert entries[0].unidad == "Metros"
    assert entries[1].atleta_id == str(pid_2)
    assert entries[1].posicion == 2
