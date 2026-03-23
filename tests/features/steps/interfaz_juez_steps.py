"""Step definitions BDD — US-1.3.1: Interfaz del Juez.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""
from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import aiosqlite
import pytest
from fastapi.testclient import TestClient
from pytest_bdd import given, parsers, scenarios, then, when

from app import app
from competencia.api.router import get_event_store
from competencia.application.commands.asignar_tarjeta import AsignarTarjetaCommand, AsignarTarjetaHandler
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

scenarios("../US-1.3.1-interfaz-juez.feature")

_CREATE_TABLE = """
    CREATE TABLE events (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        stream_id   TEXT    NOT NULL,
        event_type  TEXT    NOT NULL,
        payload     TEXT    NOT NULL,
        version     INTEGER NOT NULL,
        occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
        UNIQUE (stream_id, version)
    )
"""

OT = datetime(2026, 3, 23, 10, 30, 0, tzinfo=timezone.utc)


def _make_store() -> SQLiteEventStore:
    db_path = f"{tempfile.mkdtemp()}/bdd_juez.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


# ── Fixture de contexto ────────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict:  # type: ignore[type-arg]
    store = _make_store()
    app.dependency_overrides[get_event_store] = lambda: store
    client = TestClient(app)
    return {
        "store": store,
        "client": client,
        "estado_port": StubCompetenciaEstadoAdapter(),
        "competencias": {},   # "C001" -> UUID
        "participantes": {},  # "P001" -> UUID
        "response": None,
    }


@pytest.fixture(autouse=True)
def cleanup_overrides() -> None:  # type: ignore[return]
    yield
    app.dependency_overrides.clear()


# ── Helpers ────────────────────────────────────────────────────────────────────


def _get_cid(ctx: dict, key: str = "C001") -> UUID:  # type: ignore[type-arg]
    if key not in ctx["competencias"]:
        ctx["competencias"][key] = uuid4()
    return ctx["competencias"][key]


def _get_pid(ctx: dict, key: str) -> UUID:  # type: ignore[type-arg]
    if key not in ctx["participantes"]:
        ctx["participantes"][key] = uuid4()
    return ctx["participantes"][key]


def _registrar_ap(
    ctx: dict, cid: UUID, pid: UUID, valor: str = "50", unidad: UnidadMedida = UnidadMedida.Metros  # type: ignore[type-arg]
) -> None:
    asyncio.run(
        RegistrarAPHandler(ctx["store"], ctx["estado_port"]).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.DNF,
                valor_ap=Decimal(valor),
                unidad=unidad,
            )
        )
    )


def _llamar(ctx: dict, cid: UUID, pid: UUID, posicion: int) -> None:  # type: ignore[type-arg]
    asyncio.run(
        LlamarAtletaHandler(ctx["store"], ctx["estado_port"]).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.DNF,
                ot_programado=OT,
                posicion_grilla=posicion,
            )
        )
    )


def _ejecutar(ctx: dict, cid: UUID, pid: UUID) -> None:  # type: ignore[type-arg]
    asyncio.run(
        RegistrarResultadoHandler(ctx["store"]).handle(
            RegistrarResultadoCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.DNF,
                valor_rp=Decimal("48"),
                unidad=UnidadMedida.Metros,
                registrado_por="juez-001",
            )
        )
    )
    asyncio.run(
        AsignarTarjetaHandler(ctx["store"]).handle(
            AsignarTarjetaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.DNF,
                tipo=TipoTarjeta.Blanca,
                asignada_por="juez-001",
            )
        )
    )


def _dns(ctx: dict, cid: UUID, pid: UUID) -> None:  # type: ignore[type-arg]
    asyncio.run(
        RegistrarDNSHandler(ctx["store"]).handle(
            RegistrarDNSCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.DNF,
                registrado_por="juez-001",
            )
        )
    )


# ── Given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('una competencia con id "{cid}"'))
def step_competencia(ctx: dict, cid: str) -> None:  # type: ignore[type-arg]
    _get_cid(ctx, cid)


@given(parsers.parse('una competencia con id "{cid}" sin performances registradas'))
def step_competencia_sin_performances(ctx: dict, cid: str) -> None:  # type: ignore[type-arg]
    _get_cid(ctx, cid)


@given(
    parsers.parse(
        'la competencia tiene una performance de "{pid}" en disciplina "DNF" con AP {valor:d} metros'
    )
)
def step_performance_ap(ctx: dict, pid: str, valor: int) -> None:  # type: ignore[type-arg]
    cid = _get_cid(ctx)
    p = _get_pid(ctx, pid)
    _registrar_ap(ctx, cid, p, str(valor))


@given(
    parsers.parse(
        'la competencia tiene performances registradas de "{lista}" en disciplina "DNF" con AP {valor:d} metros'
    )
)
def step_multiples_performances(ctx: dict, lista: str, valor: int) -> None:  # type: ignore[type-arg]
    cid = _get_cid(ctx)
    for pid_key in [p.strip().strip('"') for p in lista.split(",")]:
        p = _get_pid(ctx, pid_key)
        _registrar_ap(ctx, cid, p, str(valor))


@given(parsers.parse('la performance de "{pid}" fue llamada en andarivel {andarivel:d}'))
def step_llamar(ctx: dict, pid: str, andarivel: int) -> None:  # type: ignore[type-arg]
    cid = _get_cid(ctx)
    p = _get_pid(ctx, pid)
    _llamar(ctx, cid, p, andarivel)


@given(
    parsers.parse(
        'la competencia tiene una performance de "{pid}" en disciplina "STA" con AP {valor:d} segundos ejecutada con tarjeta blanca'
    )
)
def step_performance_ejecutada(ctx: dict, pid: str, valor: int) -> None:  # type: ignore[type-arg]
    cid = _get_cid(ctx)
    p = _get_pid(ctx, pid)
    asyncio.run(
        RegistrarAPHandler(ctx["store"], ctx["estado_port"]).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                valor_ap=Decimal(str(valor)),
                unidad=UnidadMedida.Segundos,
            )
        )
    )
    asyncio.run(
        LlamarAtletaHandler(ctx["store"], ctx["estado_port"]).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                ot_programado=OT,
                posicion_grilla=1,
            )
        )
    )
    asyncio.run(
        RegistrarResultadoHandler(ctx["store"]).handle(
            RegistrarResultadoCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                valor_rp=Decimal(str(valor - 10)),
                unidad=UnidadMedida.Segundos,
                registrado_por="juez-001",
            )
        )
    )
    asyncio.run(
        AsignarTarjetaHandler(ctx["store"]).handle(
            AsignarTarjetaCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                tipo=TipoTarjeta.Blanca,
                asignada_por="juez-001",
            )
        )
    )


@given(
    parsers.parse(
        'la competencia tiene una performance de "{pid}" en disciplina "STA" con AP {valor:d} segundos con DNS registrado'
    )
)
def step_performance_dns(ctx: dict, pid: str, valor: int) -> None:  # type: ignore[type-arg]
    cid = _get_cid(ctx)
    p = _get_pid(ctx, pid)
    asyncio.run(
        RegistrarAPHandler(ctx["store"], ctx["estado_port"]).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                valor_ap=Decimal(str(valor)),
                unidad=UnidadMedida.Segundos,
            )
        )
    )
    asyncio.run(
        LlamarAtletaHandler(ctx["store"], ctx["estado_port"]).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                ot_programado=OT,
                posicion_grilla=1,
            )
        )
    )
    asyncio.run(
        RegistrarDNSHandler(ctx["store"]).handle(
            RegistrarDNSCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                registrado_por="juez-001",
            )
        )
    )


@given(
    parsers.parse(
        'la competencia tiene una performance de "{pid}" en disciplina "STA" con AP {valor:d} segundos en estado Llamada'
    )
)
def step_performance_llamada_sta(ctx: dict, pid: str, valor: int) -> None:  # type: ignore[type-arg]
    cid = _get_cid(ctx)
    p = _get_pid(ctx, pid)
    asyncio.run(
        RegistrarAPHandler(ctx["store"], ctx["estado_port"]).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                valor_ap=Decimal(str(valor)),
                unidad=UnidadMedida.Segundos,
            )
        )
    )
    asyncio.run(
        LlamarAtletaHandler(ctx["store"], ctx["estado_port"]).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=p,
                disciplina=Disciplina.STA,
                ot_programado=OT,
                posicion_grilla=1,
            )
        )
    )


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse("el juez consulta GET /competencia/{cid}/performance/actual"))
def step_get_actual(ctx: dict, cid: str) -> None:  # type: ignore[type-arg]
    competencia_id = ctx["competencias"].get(cid, uuid4())
    ctx["response"] = ctx["client"].get(f"/competencia/{competencia_id}/performance/actual")


@when(parsers.parse("el juez consulta GET /competencia/{cid}/performance/proximas"))
def step_get_proximas(ctx: dict, cid: str) -> None:  # type: ignore[type-arg]
    competencia_id = ctx["competencias"].get(cid, uuid4())
    ctx["response"] = ctx["client"].get(f"/competencia/{competencia_id}/performance/proximas")


@when(parsers.parse("el juez consulta GET /competencia/{cid}/progreso"))
def step_get_progreso(ctx: dict, cid: str) -> None:  # type: ignore[type-arg]
    competencia_id = ctx["competencias"].get(cid, uuid4())
    ctx["response"] = ctx["client"].get(f"/competencia/{competencia_id}/progreso")


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("la respuesta tiene status {code:d}"))
def step_status(ctx: dict, code: int) -> None:  # type: ignore[type-arg]
    assert ctx["response"].status_code == code, (
        f"Esperado {code}, obtenido {ctx['response'].status_code}: {ctx['response'].text}"
    )


@then(parsers.parse('la performance actual corresponde al participante "{pid}"'))
def step_participante_actual(ctx: dict, pid: str) -> None:  # type: ignore[type-arg]
    data = ctx["response"].json()
    assert data is not None
    expected_prefix = str(ctx["participantes"][pid])[:8]
    assert expected_prefix in data["nombre_atleta"]


@then(parsers.parse('el estado de la performance actual es "{estado}"'))
def step_estado_actual(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["estado"] == estado


@then(parsers.parse("el andarivel de la performance actual es {andarivel:d}"))
def step_andarivel_actual(ctx: dict, andarivel: int) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["andarivel"] == andarivel


@then(parsers.parse('el AP declarado es "{valor}"'))
def step_ap_declarado(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["ap_declarado"] == valor


@then(parsers.parse("la respuesta contiene exactamente {n:d} proximos atletas"))
def step_n_proximos(ctx: dict, n: int) -> None:  # type: ignore[type-arg]
    assert len(ctx["response"].json()) == n


@then(parsers.parse('los proximos atletas no incluyen a "{p1}" ni a "{p2}"'))
def step_proximos_no_incluyen(ctx: dict, p1: str, p2: str) -> None:  # type: ignore[type-arg]
    data = ctx["response"].json()
    excluidos = {str(ctx["participantes"][p1])[:8], str(ctx["participantes"][p2])[:8]}
    for atleta in data:
        for excluido in excluidos:
            assert excluido not in atleta["nombre_atleta"]


@then(parsers.parse('los proximos atletas incluyen a "{p1}", "{p2}" y "{p3}"'))
def step_proximos_incluyen(ctx: dict, p1: str, p2: str, p3: str) -> None:  # type: ignore[type-arg]
    data = ctx["response"].json()
    nombres = [a["nombre_atleta"] for a in data]
    for pid_key in [p1, p2, p3]:
        prefix = str(ctx["participantes"][pid_key])[:8]
        assert any(prefix in n for n in nombres), f"Atleta {pid_key} no encontrado en {nombres}"


@then(parsers.parse("el total de performances es {total:d}"))
def step_total(ctx: dict, total: int) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["total"] == total


@then(parsers.parse("las ejecutadas son {n:d}"))
def step_ejecutadas(ctx: dict, n: int) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["ejecutadas"] == n


@then(parsers.parse("los dns son {n:d}"))
def step_dns(ctx: dict, n: int) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["dns_count"] == n


@then(parsers.parse("las completadas son {n:d}"))
def step_completadas(ctx: dict, n: int) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json()["completadas"] == n


@then("la performance actual es null")
def step_actual_null(ctx: dict) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json() is None


@then("la lista de proximas esta vacia")
def step_proximas_vacias(ctx: dict) -> None:  # type: ignore[type-arg]
    assert ctx["response"].json() == []
