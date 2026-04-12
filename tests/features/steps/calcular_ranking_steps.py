"""Step definitions BDD — US-2.4.2: Calcular Ranking.

Verifica RF-PM-03: ranking automático al finalizar una disciplina,
con reglas de empate, podio, DNS y tarjeta roja.

pytest-bdd no soporta async steps nativamente — se usa asyncio.run() como wrapper.
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app import app
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
from competencia.domain.value_objects.motivo_dq import MotivoDQ
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
    RankingCategoriaDTO,
    RankingEntradaDTO,
)
from resultados.api.router import get_ranking_store
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)

scenarios("../US-2.4.2-calcular-ranking.feature")

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

OT_BASE = datetime(2026, 3, 22, 10, 30, 0)
OT_OFFSETS = [
    datetime(2026, 3, 22, 10, 30, 0),
    datetime(2026, 3, 22, 10, 33, 0),
    datetime(2026, 3, 22, 10, 36, 0),
    datetime(2026, 3, 22, 10, 39, 0),
    datetime(2026, 3, 22, 10, 42, 0),
]


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _init_db(db_path: str) -> None:
    async with aiosqlite.connect(db_path) as db:
        await db.execute(CREATE_EVENTS_TABLE)
        await db.commit()


async def _performance_ejecutada(
    store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
    cid: UUID,
    pid: UUID,
    rp_valor: str,
    disciplina: Disciplina,
    ot: datetime,
    tarjeta: TipoTarjeta = TipoTarjeta.Blanca,
    motivo: str | None = None,
) -> None:
    unidad = UnidadMedida.Segundos if disciplina.es_tiempo() else UnidadMedida.Metros

    await RegistrarAPHandler(
        event_store=store, competencia_estado=stub, disciplina_descriptor=descriptor
    ).handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            valor_ap=Decimal(rp_valor),
            unidad=unidad,
        )
    )
    await LlamarAtletaHandler(event_store=store, competencia_estado=stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            posicion_grilla=1,
            ot_programado=ot,
        )
    )
    await RegistrarResultadoHandler(event_store=store, disciplina_descriptor=descriptor).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            valor_rp=Decimal(rp_valor),
            unidad=unidad,
            registrado_por="juez-001",
        )
    )
    _MOTIVO_DQ_MAP: dict[str, MotivoDQ] = {
        "BO": MotivoDQ.PROTOCOLO_SUPERFICIE,
        "black-out": MotivoDQ.BKO_SUPERFICIE,
    }
    motivo_dq = _MOTIVO_DQ_MAP.get(motivo or "", MotivoDQ.PROTOCOLO_SUPERFICIE) if tarjeta == TipoTarjeta.Roja else None
    motivo_texto = motivo if tarjeta == TipoTarjeta.Amarilla else None
    await AsignarTarjetaHandler(event_store=store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            tipo=tarjeta,
            asignada_por="juez-001",
            motivo_dq=motivo_dq,
            motivo_texto=motivo_texto,
        )
    )


async def _performance_dns(
    store: SQLiteEventStore,
    stub: StubCompetenciaEstadoAdapter,
    descriptor: DisciplinaDescriptorAdapter,
    cid: UUID,
    pid: UUID,
    disciplina: Disciplina,
) -> None:
    unidad = UnidadMedida.Segundos if disciplina.es_tiempo() else UnidadMedida.Metros

    await RegistrarAPHandler(
        event_store=store, competencia_estado=stub, disciplina_descriptor=descriptor
    ).handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            valor_ap=Decimal("200"),
            unidad=unidad,
        )
    )
    await LlamarAtletaHandler(event_store=store, competencia_estado=stub).handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            posicion_grilla=1,
            ot_programado=OT_BASE,
        )
    )
    await RegistrarDNSHandler(event_store=store).handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=disciplina,
            registrado_por="juez-001",
        )
    )


# ── Fixtures compartidas (contexto de los escenarios) ────────────────────────


@pytest.fixture
def ctx() -> dict:
    """Diccionario mutable compartido entre steps del mismo escenario."""
    return {}


# ── Background: competencia STA con 4 performances ───────────────────────────


@given("una competencia STA finalizada con 4 performances")
def setup_competencia_sta(ctx: dict) -> None:
    async def _run() -> None:
        comp_dir = tempfile.mkdtemp()
        rank_dir = tempfile.mkdtemp()
        comp_db = comp_dir + "/competencia.db"
        rank_db = rank_dir + "/resultados.db"

        await _init_db(comp_db)
        await _init_db(rank_db)

        ctx["comp_store"] = SQLiteEventStore(comp_db)
        ctx["ranking_store"] = SQLiteEventStore(rank_db)
        ctx["cid"] = uuid4()
        ctx["stub"] = StubCompetenciaEstadoAdapter()
        ctx["descriptor"] = DisciplinaDescriptorAdapter()

        # Atletas C=310, A=295, D=295, B=DNS
        ctx["pid_C"] = uuid4()
        ctx["pid_A"] = uuid4()
        ctx["pid_D"] = uuid4()
        ctx["pid_B"] = uuid4()

    asyncio.run(_run())


@given(parsers.parse("los resultados son: C=310s blanca, A=295s blanca, D=295s blanca, B=DNS"))
def seed_performances_sta(ctx: dict) -> None:
    async def _run() -> None:
        store = ctx["comp_store"]
        stub = ctx["stub"]
        desc = ctx["descriptor"]
        cid = ctx["cid"]

        await _performance_ejecutada(
            store, stub, desc, cid, ctx["pid_C"], "310", Disciplina.STA, OT_OFFSETS[0]
        )
        await _performance_ejecutada(
            store, stub, desc, cid, ctx["pid_A"], "295", Disciplina.STA, OT_OFFSETS[1]
        )
        await _performance_ejecutada(
            store, stub, desc, cid, ctx["pid_D"], "295", Disciplina.STA, OT_OFFSETS[2]
        )
        await _performance_dns(store, stub, desc, cid, ctx["pid_B"], Disciplina.STA)

    asyncio.run(_run())


# ── When ──────────────────────────────────────────────────────────────────────


@when("el sistema calcula el ranking")
def calcular_ranking(ctx: dict) -> None:
    async def _run() -> None:
        acl = ResultadosCompetenciaAdapter(ctx["comp_store"])
        handler = CalcularRankingHandler(
            ranking_store=ctx["ranking_store"],
            resultados_port=acl,
            descriptor=ctx["descriptor"],
        )
        await handler.handle(
            CalcularRankingCommand(competencia_id=ctx["cid"], disciplina=Disciplina.STA)
        )

        qh = ObtenerRankingHandler(ctx["ranking_store"])
        ctx["entries"] = await qh.handle(
            ObtenerRankingQuery(competencia_id=ctx["cid"], disciplina=Disciplina.STA)
        )

    asyncio.run(_run())


# ── Then — ResultadosCalculados persiste ─────────────────────────────────────


@then("el evento ResultadosCalculados persiste")
def evento_persiste(ctx: dict) -> None:
    async def _check() -> None:
        stream_id = f"ranking-{ctx['cid']}-STA"
        events = await ctx["ranking_store"].load(stream_id)
        assert len(events) == 1
        assert events[0]["event_type"] == "ResultadosCalculados"

    asyncio.run(_check())


# ── Then — posiciones ─────────────────────────────────────────────────────────


def _all_entries(ctx: dict) -> list[RankingEntradaDTO]:
    entries = ctx["entries"]
    if entries and isinstance(entries[0], RankingCategoriaDTO):
        return [entry for grupo in entries for entry in grupo.entradas]
    return entries


def _entry_by_pid(ctx: dict, key: str) -> RankingEntradaDTO:
    pid = str(ctx[key])
    for e in _all_entries(ctx):
        if e.atleta_id == pid:
            return e
    raise AssertionError(f"No entry for {key}={pid}")


@then(parsers.parse("el ranking es posición {pos:d} para C con {rp}s"))
def ranking_posicion_C(ctx: dict, pos: int, rp: str) -> None:
    entry = _entry_by_pid(ctx, "pid_C")
    assert entry.posicion == pos, f"Expected pos {pos}, got {entry.posicion}"
    assert entry.rp == rp


@then(parsers.parse("el ranking es posición {pos:d} para A con {rp}s"))
def ranking_posicion_A(ctx: dict, pos: int, rp: str) -> None:
    entry = _entry_by_pid(ctx, "pid_A")
    assert entry.posicion == pos


@then(parsers.parse("el ranking es posición {pos:d} para D con {rp}s"))
def ranking_posicion_D(ctx: dict, pos: int, rp: str) -> None:
    entry = _entry_by_pid(ctx, "pid_D")
    assert entry.posicion == pos


@then(parsers.parse("B aparece en posición {pos:d} como DNS"))
def b_en_posicion_dns(ctx: dict, pos: int) -> None:
    entry = _entry_by_pid(ctx, "pid_B")
    assert entry.posicion == pos
    assert entry.es_dns is True


# ── Then — podio ──────────────────────────────────────────────────────────────


@then(parsers.parse("{letra} tiene en_podio igual a True"))
def tiene_en_podio_true(ctx: dict, letra: str) -> None:
    key = f"pid_{letra}"
    entry = _entry_by_pid(ctx, key)
    assert entry.en_podio is True, f"{letra} debería estar en podio"


@then(parsers.parse("{letra} tiene en_podio igual a False"))
def tiene_en_podio_false(ctx: dict, letra: str) -> None:
    key = f"pid_{letra}"
    entry = _entry_by_pid(ctx, key)
    assert entry.en_podio is False, f"{letra} no debería estar en podio"


# ── Then — empate ─────────────────────────────────────────────────────────────


@then("A y D tienen posición 2")
def a_y_d_posicion_2(ctx: dict) -> None:
    entry_a = _entry_by_pid(ctx, "pid_A")
    entry_d = _entry_by_pid(ctx, "pid_D")
    assert entry_a.posicion == 2
    assert entry_d.posicion == 2


@then("no existe entrada con posición 3")
def no_existe_posicion_3(ctx: dict) -> None:
    pos3 = [e for e in _all_entries(ctx) if e.posicion == 3]
    assert len(pos3) == 0, f"No debería existir posición 3, encontrados: {pos3}"


@then("B tiene posición 4")
def b_posicion_4(ctx: dict) -> None:
    entry = _entry_by_pid(ctx, "pid_B")
    assert entry.posicion == 4


# ── Then — DNS sin marca ──────────────────────────────────────────────────────


@then("B aparece después de todas las performances válidas")
def b_al_final(ctx: dict) -> None:
    entries = _all_entries(ctx)
    pid_b = str(ctx["pid_B"])
    validas = [e for e in entries if not e.es_dns and e.tarjeta not in (None, "Roja")]
    b_idx = next(i for i, e in enumerate(entries) if e.atleta_id == pid_b)
    for e in validas:
        idx = entries.index(e)
        assert idx < b_idx, f"Válida {e.atleta_id} debería aparecer antes que B"


@then("B no tiene marca numérica")
def b_sin_marca(ctx: dict) -> None:
    entry = _entry_by_pid(ctx, "pid_B")
    assert entry.rp is None


# ── Scenario: Tarjeta roja va al final ───────────────────────────────────────


@given(parsers.parse("además el atleta E recibió tarjeta roja con RP {rp}s"))
def agregar_atleta_e_roja(ctx: dict, rp: str) -> None:
    async def _run() -> None:
        ctx["pid_E"] = uuid4()
        await _performance_ejecutada(
            ctx["comp_store"],
            ctx["stub"],
            ctx["descriptor"],
            ctx["cid"],
            ctx["pid_E"],
            rp,
            Disciplina.STA,
            OT_OFFSETS[4],
            tarjeta=TipoTarjeta.Roja,
            motivo="BO",
        )

    asyncio.run(_run())


@then("E aparece después de C, A y D")
def e_al_final(ctx: dict) -> None:
    entries = _all_entries(ctx)
    pid_e = str(ctx["pid_E"])
    e_idx = next(i for i, e in enumerate(entries) if e.atleta_id == pid_e)
    for key in ("pid_C", "pid_A", "pid_D"):
        pid = str(ctx[key])
        idx = next(i for i, e in enumerate(entries) if e.atleta_id == pid)
        assert idx < e_idx


@then("E tiene en_podio igual a False")
def e_sin_podio(ctx: dict) -> None:
    entry = _entry_by_pid(ctx, "pid_E")
    assert entry.en_podio is False


# ── Scenario: REST endpoint ───────────────────────────────────────────────────


@given("el ranking fue calculado para la competencia")
def ranking_calculado(ctx: dict) -> None:
    """El ranking ya fue calculado en el Background."""
    asyncio.run(_run_calcular(ctx))


async def _run_calcular(ctx: dict) -> None:
    acl = ResultadosCompetenciaAdapter(ctx["comp_store"])
    handler = CalcularRankingHandler(
        ranking_store=ctx["ranking_store"],
        resultados_port=acl,
        descriptor=ctx["descriptor"],
    )
    await handler.handle(
        CalcularRankingCommand(competencia_id=ctx["cid"], disciplina=Disciplina.STA)
    )


@when(parsers.parse("se consulta GET /resultados/{id}/ranking con disciplina STA"))
def consultar_ranking_api(ctx: dict) -> None:
    ranking_store = ctx["ranking_store"]
    app.dependency_overrides[get_ranking_store] = lambda: ranking_store
    client = TestClient(app)
    cid = ctx["cid"]
    ctx["response"] = client.get(f"/resultados/{cid}/ranking?disciplina=STA")


@then(parsers.parse("la respuesta tiene status {status:d}"))
def respuesta_status(ctx: dict, status: int) -> None:
    assert ctx["response"].status_code == status
    app.dependency_overrides.clear()


@then("la respuesta incluye posición, atleta_id, rp y tarjeta para cada entrada")
def respuesta_incluye_campos(ctx: dict) -> None:
    data = ctx["response"].json()
    assert "rankings" in data
    for grupo in data["rankings"]:
        assert "categoria" in grupo
        assert "entradas" in grupo
        for entry in grupo["entradas"]:
            assert "posicion" in entry
            assert "atleta_id" in entry
            assert "rp" in entry or entry.get("rp") is None
            assert "tarjeta" in entry or entry.get("tarjeta") is None


# ── Scenario: DNF ─────────────────────────────────────────────────────────────


@given("una competencia DNF finalizada con 3 performances")
def setup_competencia_dnf(ctx: dict) -> None:
    async def _run() -> None:
        comp_dir = tempfile.mkdtemp()
        rank_dir = tempfile.mkdtemp()
        comp_db = comp_dir + "/competencia.db"
        rank_db = rank_dir + "/resultados.db"

        await _init_db(comp_db)
        await _init_db(rank_db)

        ctx["comp_store_dnf"] = SQLiteEventStore(comp_db)
        ctx["ranking_store_dnf"] = SQLiteEventStore(rank_db)
        ctx["cid_dnf"] = uuid4()
        ctx["stub_dnf"] = StubCompetenciaEstadoAdapter()
        ctx["descriptor_dnf"] = DisciplinaDescriptorAdapter()

    asyncio.run(_run())


@given(parsers.parse("los resultados DNF son: X=85m blanca, Y=92m blanca, Z=DNS"))
def seed_performances_dnf(ctx: dict) -> None:
    async def _run() -> None:
        store = ctx["comp_store_dnf"]
        stub = ctx["stub_dnf"]
        desc = ctx["descriptor_dnf"]
        cid = ctx["cid_dnf"]

        ctx["pid_X"] = uuid4()
        ctx["pid_Y"] = uuid4()
        ctx["pid_Z"] = uuid4()

        await _performance_ejecutada(
            store, stub, desc, cid, ctx["pid_X"], "85", Disciplina.DNF, OT_OFFSETS[0]
        )
        await _performance_ejecutada(
            store, stub, desc, cid, ctx["pid_Y"], "92", Disciplina.DNF, OT_OFFSETS[1]
        )
        await _performance_dns(store, stub, desc, cid, ctx["pid_Z"], Disciplina.DNF)

    asyncio.run(_run())


@when("el sistema calcula el ranking DNF")
def calcular_ranking_dnf(ctx: dict) -> None:
    async def _run() -> None:
        acl = ResultadosCompetenciaAdapter(ctx["comp_store_dnf"])
        handler = CalcularRankingHandler(
            ranking_store=ctx["ranking_store_dnf"],
            resultados_port=acl,
            descriptor=ctx["descriptor_dnf"],
        )
        await handler.handle(
            CalcularRankingCommand(competencia_id=ctx["cid_dnf"], disciplina=Disciplina.DNF)
        )

        qh = ObtenerRankingHandler(ctx["ranking_store_dnf"])
        ctx["entries_dnf"] = await qh.handle(
            ObtenerRankingQuery(competencia_id=ctx["cid_dnf"], disciplina=Disciplina.DNF)
        )

    asyncio.run(_run())


@then(parsers.parse("el orden DNF es posición {pos:d} para Y con {rp}m"))
def orden_dnf_y(ctx: dict, pos: int, rp: str) -> None:
    pid_y = str(ctx["pid_Y"])
    entry = next(e for e in _all_entries({"entries": ctx["entries_dnf"]}) if e.atleta_id == pid_y)
    assert entry.posicion == pos
    assert entry.rp == rp


@then(parsers.parse("el orden DNF es posición {pos:d} para X con {rp}m"))
def orden_dnf_x(ctx: dict, pos: int, rp: str) -> None:
    pid_x = str(ctx["pid_X"])
    entry = next(e for e in _all_entries({"entries": ctx["entries_dnf"]}) if e.atleta_id == pid_x)
    assert entry.posicion == pos
    assert entry.rp == rp


@then(parsers.parse("Z aparece en posición {pos:d} como DNS en DNF"))
def z_dns_dnf(ctx: dict, pos: int) -> None:
    pid_z = str(ctx["pid_Z"])
    entry = next(e for e in _all_entries({"entries": ctx["entries_dnf"]}) if e.atleta_id == pid_z)
    assert entry.posicion == pos
    assert entry.es_dns is True
