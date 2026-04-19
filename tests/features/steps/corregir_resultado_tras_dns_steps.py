"""Step definitions BDD — US-ADJ-7.1: Corregir resultado tras DNS."""

from __future__ import annotations

import asyncio
import tempfile
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

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
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import (
    EstadoInvalidoParaCorregirResultadoTrasDNS,
    MotivoObligatorio,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

scenarios("../US-ADJ-7.1-corregir-resultado-tras-dns.feature")

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

OT = datetime(2026, 3, 23, 10, 30, 0)


def _make_event_store(tmp_path: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_corregir_resultado_tras_dns.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


def _stream_id(ctx: dict) -> str:  # type: ignore[type-arg]
    return (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )


async def _registrar_ap_y_llamar(ctx: dict, valor_ap: Decimal = Decimal("50")) -> None:  # type: ignore[type-arg]
    await RegistrarAPHandler(
        ctx["event_store"],
        ctx["estado_port"],
        DisciplinaDescriptorAdapter(),
    ).handle(
        RegistrarAPCommand(
            competencia_id=ctx["competencia_id"],
            participante_id=ctx["participante_id"],
            disciplina=ctx["disciplina"],
            valor_ap=valor_ap,
            unidad=UnidadMedida.Metros,
        )
    )
    await LlamarAtletaHandler(ctx["event_store"], ctx["estado_port"]).handle(
        LlamarAtletaCommand(
            competencia_id=ctx["competencia_id"],
            participante_id=ctx["participante_id"],
            disciplina=ctx["disciplina"],
            ot_programado=OT,
            posicion_grilla=1,
        )
    )


async def _registrar_resultado(ctx: dict, valor_rp: Decimal = Decimal("50")) -> None:  # type: ignore[type-arg]
    await RegistrarResultadoHandler(ctx["event_store"], DisciplinaDescriptorAdapter()).handle(
        RegistrarResultadoCommand(
            competencia_id=ctx["competencia_id"],
            participante_id=ctx["participante_id"],
            disciplina=ctx["disciplina"],
            valor_rp=valor_rp,
            unidad=UnidadMedida.Metros,
            registrado_por="juez-001",
        )
    )


async def _registrar_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    await RegistrarDNSHandler(ctx["event_store"]).handle(
        RegistrarDNSCommand(
            competencia_id=ctx["competencia_id"],
            participante_id=ctx["participante_id"],
            disciplina=ctx["disciplina"],
            registrado_por="juez-001",
        )
    )


def _reset_context(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["competencia_id"] = uuid4()
    ctx["participante_id"] = uuid4()
    ctx["disciplina"] = Disciplina.DNF
    ctx["event_store"] = _make_event_store(tempfile.mkdtemp())
    ctx["estado_port"] = StubCompetenciaEstadoAdapter()
    ctx["result"] = None
    ctx["error"] = None


@pytest.fixture
def ctx(tmp_path: pytest.TempPathFactory) -> dict:  # type: ignore[type-arg]
    return {
        "competencia_id": uuid4(),
        "participante_id": uuid4(),
        "disciplina": Disciplina.DNF,
        "event_store": _make_event_store(str(tmp_path)),
        "estado_port": StubCompetenciaEstadoAdapter(),
        "result": None,
        "error": None,
    }


@given("una competencia en ejecucion con una performance en estado DNS")
def step_performance_en_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    asyncio.run(_registrar_ap_y_llamar(ctx))
    asyncio.run(_registrar_dns(ctx))


@given("una performance en estado Ejecutada")
def step_performance_ejecutada(ctx: dict) -> None:  # type: ignore[type-arg]
    _reset_context(ctx)
    asyncio.run(_registrar_ap_y_llamar(ctx))
    asyncio.run(_registrar_resultado(ctx))
    asyncio.run(
        AsignarTarjetaHandler(ctx["event_store"]).handle(
            AsignarTarjetaCommand(
                competencia_id=ctx["competencia_id"],
                participante_id=ctx["participante_id"],
                disciplina=ctx["disciplina"],
                tipo=TipoTarjeta.Blanca,
                asignada_por="juez-001",
            )
        )
    )


@given("una performance en estado Llamada")
def step_performance_llamada(ctx: dict) -> None:  # type: ignore[type-arg]
    _reset_context(ctx)
    asyncio.run(_registrar_ap_y_llamar(ctx))


def _corregir_resultado_tras_dns(ctx: dict, valor_rp: Decimal, motivo: str) -> None:  # type: ignore[type-arg]
    try:
        ctx["result"] = asyncio.run(
            CorregirResultadoTrasDNSHandler(ctx["event_store"]).handle(
                CorregirResultadoTrasDNSCommand(
                    competencia_id=ctx["competencia_id"],
                    participante_id=ctx["participante_id"],
                    disciplina=ctx["disciplina"],
                    valor_rp=valor_rp,
                    unidad=UnidadMedida.Metros,
                    registrado_por="juez-001",
                    motivo_correccion=motivo,
                )
            )
        )
    except Exception as exc:
        ctx["error"] = exc


@when(parsers.parse('el juez corrige el DNS con valor RP {valor:d} metros y motivo "{motivo}"'))
def step_corrige_dns(ctx: dict, valor: int, motivo: str) -> None:  # type: ignore[type-arg]
    _corregir_resultado_tras_dns(ctx, Decimal(str(valor)), motivo)


@when("el juez intenta corregir el resultado tras DNS")
def step_intenta_corregir_tras_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    _corregir_resultado_tras_dns(ctx, Decimal("50"), "DNS registrado por error")


@when("el juez corrige el DNS sin motivo")
def step_corrige_dns_sin_motivo(ctx: dict) -> None:  # type: ignore[type-arg]
    _corregir_resultado_tras_dns(ctx, Decimal("50"), "")


@when("el juez asigna tarjeta blanca")
def step_asigna_tarjeta_blanca(ctx: dict) -> None:  # type: ignore[type-arg]
    asyncio.run(
        AsignarTarjetaHandler(ctx["event_store"]).handle(
            AsignarTarjetaCommand(
                competencia_id=ctx["competencia_id"],
                participante_id=ctx["participante_id"],
                disciplina=ctx["disciplina"],
                tipo=TipoTarjeta.Blanca,
                asignada_por="juez-001",
            )
        )
    )


@then(parsers.parse("la performance queda en estado {estado}"))
def step_estado_final(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    events = asyncio.run(ctx["event_store"].load(_stream_id(ctx)))
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance(estado)


@then("el event store contiene un evento ResultadoCorregidoTrasDNS")
def step_evento_correccion_tras_dns(ctx: dict) -> None:  # type: ignore[type-arg]
    events = asyncio.run(ctx["event_store"].load(_stream_id(ctx)))
    assert any(event["event_type"] == "ResultadoCorregidoTrasDNS" for event in events)


@then("se rechaza la operacion por estado invalido")
def step_error_estado_invalido(ctx: dict) -> None:  # type: ignore[type-arg]
    assert isinstance(ctx["error"], EstadoInvalidoParaCorregirResultadoTrasDNS)


@then("se rechaza la operacion por motivo obligatorio")
def step_error_motivo_obligatorio(ctx: dict) -> None:  # type: ignore[type-arg]
    assert isinstance(ctx["error"], MotivoObligatorio)


@then("el event store contiene ResultadoCorregidoTrasDNS antes de TarjetaAsignada")
def step_orden_eventos(ctx: dict) -> None:  # type: ignore[type-arg]
    events = asyncio.run(ctx["event_store"].load(_stream_id(ctx)))
    event_types = [event["event_type"] for event in events]
    assert event_types.index("ResultadoCorregidoTrasDNS") < event_types.index("TarjetaAsignada")
