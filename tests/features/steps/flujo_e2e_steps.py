"""Step definitions BDD — US-1.4.2: Flujo Completo E2E: AP → Tarjeta."""
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
from competencia.domain.aggregates.performance import Performance
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

scenarios("../US-1.4.2-flujo-e2e.feature")

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

_DISCIPLINA = Disciplina.STA
_JUEZ = "juez-001"
_OT = datetime(2026, 3, 23, 10, 0, 0, tzinfo=timezone.utc)

# Mapping de nombre de atleta a posición en grilla
_POSICION_GRILLA = {"atleta-A": 1, "atleta-B": 2, "atleta-C": 3, "atleta-D": 4, "atleta-E": 5}


# ── Helpers async ────────────────────────────────────────────────────────────


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


async def _ap_async(store: SQLiteEventStore, cid: UUID, pid: UUID, valor: str) -> None:
    await RegistrarAPHandler(store, StubCompetenciaEstadoAdapter()).handle(
        RegistrarAPCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Metros,
        )
    )


async def _llamar_async(store: SQLiteEventStore, cid: UUID, pid: UUID, pos: int) -> None:
    await LlamarAtletaHandler(store, StubCompetenciaEstadoAdapter()).handle(
        LlamarAtletaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            ot_programado=_OT,
            posicion_grilla=pos,
        )
    )


async def _resultado_async(store: SQLiteEventStore, cid: UUID, pid: UUID, valor: str) -> None:
    await RegistrarResultadoHandler(store).handle(
        RegistrarResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Metros,
            registrado_por=_JUEZ,
        )
    )


async def _tarjeta_async(
    store: SQLiteEventStore,
    cid: UUID,
    pid: UUID,
    tipo: TipoTarjeta,
    motivo: str | None = None,
    distancia_blackout: Decimal | None = None,
) -> None:
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            tipo=tipo,
            asignada_por=_JUEZ,
            motivo=motivo,
            distancia_blackout=distancia_blackout,
        )
    )


async def _dns_async(store: SQLiteEventStore, cid: UUID, pid: UUID) -> None:
    await RegistrarDNSHandler(store).handle(
        RegistrarDNSCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            registrado_por=_JUEZ,
        )
    )


async def _corregir_async(
    store: SQLiteEventStore, cid: UUID, pid: UUID, valor: str, motivo: str
) -> None:
    await CorregirResultadoHandler(store).handle(
        CorregirResultadoCommand(
            competencia_id=cid,
            participante_id=pid,
            disciplina=_DISCIPLINA,
            valor_rp=Decimal(valor),
            unidad=UnidadMedida.Metros,
            registrado_por=_JUEZ,
            motivo=motivo,
        )
    )


def _stream_id(ctx: dict, nombre: str) -> str:  # type: ignore[type-arg]
    pid = ctx["participantes"][nombre]
    return f"performance-{ctx['cid']}-{pid}-{_DISCIPLINA.value}"


async def _get_performance(ctx: dict, nombre: str) -> Performance:  # type: ignore[type-arg]
    stream = await ctx["store"].load(_stream_id(ctx, nombre))
    return Performance.reconstitute(stream)


async def _ejecutar_flujo_completo_async(ctx: dict) -> None:  # type: ignore[type-arg]
    """Ejecuta el flujo DoD SP1 completo sobre el contexto existente."""
    store, cid = ctx["store"], ctx["cid"]
    p = ctx["participantes"]

    # A: AP → Llamar → Resultado 60m → Blanca
    await _llamar_async(store, cid, p["atleta-A"], 1)
    await _resultado_async(store, cid, p["atleta-A"], "60")
    await _tarjeta_async(store, cid, p["atleta-A"], TipoTarjeta.Blanca)

    # B: AP → Llamar → DNS
    await _llamar_async(store, cid, p["atleta-B"], 2)
    await _dns_async(store, cid, p["atleta-B"])

    # C: AP → Llamar → Resultado 72m → Amarilla
    await _llamar_async(store, cid, p["atleta-C"], 3)
    await _resultado_async(store, cid, p["atleta-C"], "72")
    await _tarjeta_async(store, cid, p["atleta-C"], TipoTarjeta.Amarilla, motivo="sin superficie")

    # D: AP → Llamar → Resultado 55m → Blanca → Corregir 53m
    await _llamar_async(store, cid, p["atleta-D"], 4)
    await _resultado_async(store, cid, p["atleta-D"], "55")
    await _tarjeta_async(store, cid, p["atleta-D"], TipoTarjeta.Blanca)
    await _corregir_async(store, cid, p["atleta-D"], "53", "error de lectura")

    # E: AP → Llamar → Resultado 90m → Roja black-out distancia 45m
    await _llamar_async(store, cid, p["atleta-E"], 5)
    await _resultado_async(store, cid, p["atleta-E"], "90")
    await _tarjeta_async(
        store, cid, p["atleta-E"], TipoTarjeta.Roja,
        motivo="black-out", distancia_blackout=Decimal("45"),
    )


# ── Background ────────────────────────────────────────────────────────────────


@given(parsers.parse('una competencia activa con id "{comp_id}"'), target_fixture="ctx_e2e")
def step_competencia_activa(comp_id: str):
    """Crea el store, la competencia y los 5 participantes."""
    db_file = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    db_path = db_file.name
    db_file.close()

    async def _setup() -> dict:  # type: ignore[type-arg]
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

        store = SQLiteEventStore(db_path)
        cid = uuid4()
        participantes = {f"atleta-{c}": uuid4() for c in ("A", "B", "C", "D", "E")}
        aps = {"atleta-A": "60", "atleta-B": "40", "atleta-C": "80", "atleta-D": "50", "atleta-E": "90"}

        for nombre, pid in participantes.items():
            await _ap_async(store, cid, pid, aps[nombre])

        http_client = TestClient(app)
        app.dependency_overrides[get_event_store] = lambda: store
        return {
            "store": store,
            "cid": cid,
            "participantes": participantes,
            "client": http_client,
            "exception": None,
            "response": None,
        }

    return _run(_setup())


@given("5 performances con AP registrado en la grilla")
def step_performances_con_ap(ctx_e2e: dict) -> None:  # type: ignore[type-arg]
    """Los APs ya fueron registrados en el step anterior del Background."""


# ── Given ─────────────────────────────────────────────────────────────────────


@given(parsers.parse('el atleta "{nombre}" tiene AP de {valor} metros en estado AnunciadaAP'))
def step_atleta_en_anunciada_ap(ctx_e2e: dict, nombre: str, valor: str) -> None:  # type: ignore[type-arg]
    """AP ya registrado en el Background — verifica que el atleta está en AnunciadaAP."""
    performance = _run(_get_performance(ctx_e2e, nombre))
    assert performance.estado == EstadoPerformance.AnunciadaAP


@given(parsers.parse('el atleta "{nombre}" está en estado Llamada'))
def step_atleta_en_llamada(ctx_e2e: dict, nombre: str) -> None:  # type: ignore[type-arg]
    pid = ctx_e2e["participantes"][nombre]
    pos = _POSICION_GRILLA[nombre]
    _run(_llamar_async(ctx_e2e["store"], ctx_e2e["cid"], pid, pos))


@given(parsers.parse('el atleta "{nombre}" tiene AP de {valor} metros en estado Llamada'))
def step_atleta_ap_en_llamada(ctx_e2e: dict, nombre: str, valor: str) -> None:  # type: ignore[type-arg]
    """AP ya registrado en Background; llama al atleta para ponerlo en estado Llamada."""
    pid = ctx_e2e["participantes"][nombre]
    pos = _POSICION_GRILLA[nombre]
    _run(_llamar_async(ctx_e2e["store"], ctx_e2e["cid"], pid, pos))


@given(
    parsers.parse(
        'el atleta "{nombre}" tiene tarjeta blanca asignada con resultado {valor} metros'
    )
)
def step_atleta_con_tarjeta_blanca(ctx_e2e: dict, nombre: str, valor: str) -> None:  # type: ignore[type-arg]
    store, cid = ctx_e2e["store"], ctx_e2e["cid"]
    pid = ctx_e2e["participantes"][nombre]
    pos = _POSICION_GRILLA[nombre]
    _run(_llamar_async(store, cid, pid, pos))
    _run(_resultado_async(store, cid, pid, valor))
    _run(_tarjeta_async(store, cid, pid, TipoTarjeta.Blanca))


@given("el flujo completo de las 5 performances fue ejecutado")
def step_flujo_completo_ejecutado(ctx_e2e: dict) -> None:  # type: ignore[type-arg]
    _run(_ejecutar_flujo_completo_async(ctx_e2e))


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse('el juez llama al atleta "{nombre}"'))
def step_llamar_atleta(ctx_e2e: dict, nombre: str) -> None:  # type: ignore[type-arg]
    pid = ctx_e2e["participantes"][nombre]
    pos = _POSICION_GRILLA[nombre]
    _run(_llamar_async(ctx_e2e["store"], ctx_e2e["cid"], pid, pos))


@when(parsers.parse('el juez registra resultado de {valor} metros para "{nombre}"'))
def step_registrar_resultado(ctx_e2e: dict, valor: str, nombre: str) -> None:  # type: ignore[type-arg]
    pid = ctx_e2e["participantes"][nombre]
    _run(_resultado_async(ctx_e2e["store"], ctx_e2e["cid"], pid, valor))


@when(parsers.parse('el juez asigna tarjeta blanca a "{nombre}"'))
def step_asignar_blanca(ctx_e2e: dict, nombre: str) -> None:  # type: ignore[type-arg]
    pid = ctx_e2e["participantes"][nombre]
    _run(_tarjeta_async(ctx_e2e["store"], ctx_e2e["cid"], pid, TipoTarjeta.Blanca))


@when(parsers.parse('el juez registra DNS para el atleta "{nombre}"'))
def step_registrar_dns(ctx_e2e: dict, nombre: str) -> None:  # type: ignore[type-arg]
    pid = ctx_e2e["participantes"][nombre]
    _run(_dns_async(ctx_e2e["store"], ctx_e2e["cid"], pid))


@when(
    parsers.parse(
        'el juez corrige el resultado a {valor} metros con motivo "{motivo}"'
    )
)
def step_corregir_resultado(ctx_e2e: dict, valor: str, motivo: str) -> None:  # type: ignore[type-arg]
    # Busca el atleta en estado Ejecutada para corregir
    for nombre, pid in ctx_e2e["participantes"].items():
        stream_id = _stream_id(ctx_e2e, nombre)
        events = _run(ctx_e2e["store"].load(stream_id))
        if events:
            perf = Performance.reconstitute(events)
            if perf.estado == EstadoPerformance.Ejecutada:
                _run(_corregir_async(ctx_e2e["store"], ctx_e2e["cid"], pid, valor, motivo))
                return


@when(
    parsers.parse(
        'el juez asigna tarjeta roja con motivo "black-out" y distancia {distancia} metros a "{nombre}"'
    )
)
def step_asignar_blackout(ctx_e2e: dict, distancia: str, nombre: str) -> None:  # type: ignore[type-arg]
    pid = ctx_e2e["participantes"][nombre]
    _run(
        _tarjeta_async(
            ctx_e2e["store"], ctx_e2e["cid"], pid, TipoTarjeta.Roja,
            motivo="black-out", distancia_blackout=Decimal(distancia),
        )
    )


@when(parsers.parse("el juez consulta GET /competencia/{comp_id}/events"))
def step_get_events(ctx_e2e: dict, comp_id: str) -> None:  # type: ignore[type-arg]
    ctx_e2e["response"] = ctx_e2e["client"].get(f"/competencia/{ctx_e2e['cid']}/events")


@when(parsers.parse("el juez consulta GET /competencia/{comp_id}/progreso"))
def step_get_progreso(ctx_e2e: dict, comp_id: str) -> None:  # type: ignore[type-arg]
    ctx_e2e["response"] = ctx_e2e["client"].get(f"/competencia/{ctx_e2e['cid']}/progreso")


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('la performance de "{nombre}" está en estado {estado}'))
def step_performance_en_estado(ctx_e2e: dict, nombre: str, estado: str) -> None:  # type: ignore[type-arg]
    performance = _run(_get_performance(ctx_e2e, nombre))
    assert performance.estado.value == estado


@then(parsers.parse('el evento {event_type} existe en el Event Store para "{nombre}"'))
def step_evento_existe(ctx_e2e: dict, event_type: str, nombre: str) -> None:  # type: ignore[type-arg]
    events = _run(ctx_e2e["store"].load(_stream_id(ctx_e2e, nombre)))
    tipos = [e["event_type"] for e in events]
    assert event_type in tipos, f"{event_type} no encontrado en {tipos}"


@then(parsers.parse("el evento TarjetaAsignada contiene distancia_blackout {distancia} para \"{nombre}\""))
def step_tarjeta_contiene_distancia(ctx_e2e: dict, distancia: str, nombre: str) -> None:  # type: ignore[type-arg]
    events = _run(ctx_e2e["store"].load(_stream_id(ctx_e2e, nombre)))
    tarjeta = next(e for e in events if e["event_type"] == "TarjetaAsignada")
    assert tarjeta["payload"]["distancia_blackout"] == distancia


@then("la respuesta tiene status 200")
def step_status_200(ctx_e2e: dict) -> None:  # type: ignore[type-arg]
    assert ctx_e2e["response"].status_code == 200


@then(parsers.parse("la respuesta contiene al menos {n} eventos en orden de secuencia"))
def step_contiene_eventos(ctx_e2e: dict, n: str) -> None:  # type: ignore[type-arg]
    data = ctx_e2e["response"].json()
    assert data["total_events"] >= int(n)
    sequences = [e["sequence"] for e in data["events"]]
    assert sequences == sorted(sequences)


@then("todos los eventos tienen campo event_type y occurred_at")
def step_eventos_campos(ctx_e2e: dict) -> None:  # type: ignore[type-arg]
    for event in ctx_e2e["response"].json()["events"]:
        assert "event_type" in event
        assert "occurred_at" in event


@then(parsers.parse("el Read Model de progreso refleja {n} performance completada"))
def step_progreso_n_completadas(ctx_e2e: dict, n: str) -> None:  # type: ignore[type-arg]
    response = ctx_e2e["client"].get(f"/competencia/{ctx_e2e['cid']}/progreso")
    assert response.json()["completadas"] >= int(n)


@then(parsers.parse("ejecutadas es {ejecutadas} y total es {total} y dns es {dns}"))
def step_progreso_completo(ctx_e2e: dict, ejecutadas: str, total: str, dns: str) -> None:  # type: ignore[type-arg]
    data = ctx_e2e["response"].json()
    assert data["total"] == int(total)
    assert data["ejecutadas"] == int(ejecutadas)
    assert data["dns_count"] == int(dns)
