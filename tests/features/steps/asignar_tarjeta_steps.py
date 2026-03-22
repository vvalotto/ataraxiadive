"""Step definitions BDD — US-1.2.4: Asignar Tarjeta.

pytest-bdd no soporta async steps nativamente. Los steps que requieren
operaciones async usan asyncio.run() como wrapper síncrono.
"""
from __future__ import annotations

import asyncio
from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import tempfile

import aiosqlite
import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.domain.aggregates.performance import (
    EstadoInvalidoParaAsignarTarjeta,
    MotivoObligatorio,
    Performance,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

scenarios("../US-1.2.4-asignar-tarjeta.feature")

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

OT = datetime(2026, 3, 22, 10, 30, 0)

_TARJETA_MAP = {
    "blanca": TipoTarjeta.Blanca,
    "amarilla": TipoTarjeta.Amarilla,
    "roja": TipoTarjeta.Roja,
}


def _make_event_store(tmp_path: str) -> SQLiteEventStore:
    db_path = f"{tmp_path}/bdd_tarjeta.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


# ── Fixture de contexto por escenario ─────────────────────────────────────────


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


# ── Background ────────────────────────────────────────────────────────────────


@given(parsers.parse('una competencia activa con id "{cid}" en estado "EnEjecucion"'))
def step_competencia_activa_tarjeta(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["competencia_id"] = uuid4()


@given(parsers.parse('un atleta con id "{pid}" en disciplina "DNF"'))
def step_atleta_dnf_tarjeta(ctx: dict) -> None:  # type: ignore[type-arg]
    ctx["participante_id"] = uuid4()
    ctx["disciplina"] = Disciplina.DNF


@given(
    parsers.parse(
        'la performance del atleta tiene AP registrado de {valor:d} metros y RP de {rp:f} metros'
    )
)
def step_ap_y_resultado_registrado(ctx: dict, valor: int, rp: float) -> None:  # type: ignore[type-arg]
    """Lleva la performance hasta ResultadoRegistrado."""
    es = ctx["event_store"]
    sp = ctx["estado_port"]
    cid = ctx["competencia_id"]
    pid = ctx["participante_id"]
    disc = ctx["disciplina"]

    asyncio.run(
        RegistrarAPHandler(es, sp).handle(
            RegistrarAPCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=disc, valor_ap=Decimal(str(valor)), unidad=UnidadMedida.Metros,
            )
        )
    )
    asyncio.run(
        LlamarAtletaHandler(es, sp).handle(
            LlamarAtletaCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=disc, ot_programado=OT, posicion_grilla=1,
            )
        )
    )
    asyncio.run(
        RegistrarResultadoHandler(es).handle(
            RegistrarResultadoCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=disc, valor_rp=Decimal(str(rp)),
                unidad=UnidadMedida.Metros, registrado_por="juez-001",
            )
        )
    )


@given('la performance está en estado "ResultadoRegistrado"')
def step_performance_resultado_registrado(ctx: dict) -> None:  # type: ignore[type-arg]
    pass  # Background ya dejó la performance en ResultadoRegistrado


# ── Given (específicos de escenario) ──────────────────────────────────────────


@given('la performance del atleta está en estado "Llamada"')
def step_performance_en_llamada(ctx: dict) -> None:  # type: ignore[type-arg]
    """Resetea el contexto y lleva la performance solo hasta el estado Llamada.

    Se requiere un event store nuevo porque el Background ya configuró un stream
    hasta ResultadoRegistrado. Este step crea nuevos IDs y una nueva DB.
    """
    # Nuevo store e IDs para este escenario específico
    fresh_store = _make_event_store(tempfile.mkdtemp())
    cid = uuid4()
    pid = uuid4()
    ctx["event_store"] = fresh_store
    ctx["competencia_id"] = cid
    ctx["participante_id"] = pid
    sp = ctx["estado_port"]
    disc = ctx["disciplina"]

    asyncio.run(
        RegistrarAPHandler(fresh_store, sp).handle(
            RegistrarAPCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=disc, valor_ap=Decimal("50"), unidad=UnidadMedida.Metros,
            )
        )
    )
    asyncio.run(
        LlamarAtletaHandler(fresh_store, sp).handle(
            LlamarAtletaCommand(
                competencia_id=cid, participante_id=pid,
                disciplina=disc, ot_programado=OT, posicion_grilla=1,
            )
        )
    )


# ── When ──────────────────────────────────────────────────────────────────────


def _ejecutar_asignar_tarjeta(
    ctx: dict,  # type: ignore[type-arg]
    tipo: TipoTarjeta,
    asignada_por: str,
    motivo: str | None,
) -> None:
    handler = AsignarTarjetaHandler(ctx["event_store"])
    cmd = AsignarTarjetaCommand(
        competencia_id=ctx["competencia_id"],
        participante_id=ctx["participante_id"],
        disciplina=ctx["disciplina"],
        tipo=tipo,
        asignada_por=asignada_por,
        motivo=motivo,
    )
    try:
        ctx["result"] = asyncio.run(handler.handle(cmd))
        ctx["tipo_tarjeta"] = tipo
        ctx["motivo_tarjeta"] = motivo
    except Exception as exc:
        ctx["error"] = exc


@when(
    parsers.parse('el juez asigna tarjeta blanca sin motivo asignada_por="{juez}"')
)
def step_asignar_blanca(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_asignar_tarjeta(ctx, TipoTarjeta.Blanca, juez, None)


@when(
    parsers.parse(
        'el juez asigna tarjeta amarilla con motivo="{motivo}" asignada_por="{juez}"'
    )
)
def step_asignar_amarilla_con_motivo(ctx: dict, motivo: str, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_asignar_tarjeta(ctx, TipoTarjeta.Amarilla, juez, motivo)


@when(
    parsers.parse(
        'el juez asigna tarjeta roja con motivo="{motivo}" asignada_por="{juez}"'
    )
)
def step_asignar_roja_con_motivo(ctx: dict, motivo: str, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_asignar_tarjeta(ctx, TipoTarjeta.Roja, juez, motivo)


@when(
    parsers.parse('el juez intenta asignar tarjeta amarilla sin motivo asignada_por="{juez}"')
)
def step_intentar_amarilla_sin_motivo(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_asignar_tarjeta(ctx, TipoTarjeta.Amarilla, juez, None)


@when(
    parsers.parse('el juez intenta asignar tarjeta roja sin motivo asignada_por="{juez}"')
)
def step_intentar_roja_sin_motivo(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_asignar_tarjeta(ctx, TipoTarjeta.Roja, juez, None)


@when(
    parsers.parse('el juez intenta asignar tarjeta blanca sin motivo asignada_por="{juez}"')
)
def step_intentar_blanca_estado_invalido(ctx: dict, juez: str) -> None:  # type: ignore[type-arg]
    _ejecutar_asignar_tarjeta(ctx, TipoTarjeta.Blanca, juez, None)


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse('la performance pasa al estado "{estado}"'))
def step_estado_tarjeta(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    performance = Performance.reconstitute(events)
    assert performance.estado == EstadoPerformance(estado)


@then('el evento TarjetaAsignada persiste en el event stream')
def step_evento_tarjeta_en_stream(ctx: dict) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    assert any(e["event_type"] == "TarjetaAsignada" for e in events)


@then(
    parsers.parse(
        'el evento contiene tipo="{tipo}", motivo=null y asignadaPor="{juez}"'
    )
)
def step_payload_blanca_correcto(ctx: dict, tipo: str, juez: str) -> None:  # type: ignore[type-arg]
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    tarjeta_ev = next(e for e in events if e["event_type"] == "TarjetaAsignada")
    payload = tarjeta_ev["payload"]
    assert payload["tipo"] == tipo
    assert payload["motivo"] is None
    assert payload["asignada_por"] == juez


@then(
    parsers.parse(
        'el evento contiene tipo="{tipo}", motivo="{motivo}" y asignadaPor="{juez}"'
    )
)
def step_payload_con_motivo_correcto(
    ctx: dict, tipo: str, motivo: str, juez: str  # type: ignore[type-arg]
) -> None:
    stream_id = (
        f"performance-{ctx['competencia_id']}"
        f"-{ctx['participante_id']}"
        f"-{ctx['disciplina'].value}"
    )
    events = asyncio.run(ctx["event_store"].load(stream_id))
    tarjeta_ev = next(e for e in events if e["event_type"] == "TarjetaAsignada")
    payload = tarjeta_ev["payload"]
    assert payload["tipo"] == tipo
    assert payload["motivo"] == motivo
    assert payload["asignada_por"] == juez


@then(parsers.parse('el sistema rechaza la operación con error "{error_type}"'))
def step_error_esperado_tarjeta(ctx: dict, error_type: str) -> None:  # type: ignore[type-arg]
    error_map = {
        "MotivoObligatorio": MotivoObligatorio,
        "EstadoInvalidoParaAsignarTarjeta": EstadoInvalidoParaAsignarTarjeta,
    }
    assert ctx["error"] is not None, "Se esperaba un error pero no hubo ninguno"
    expected = error_map[error_type]
    assert isinstance(ctx["error"], expected), (
        f"Error esperado: {error_type}, obtenido: {type(ctx['error']).__name__}"
    )


@then(parsers.parse('la performance permanece en estado "{estado}"'))
def step_estado_permanece_tarjeta(ctx: dict, estado: str) -> None:  # type: ignore[type-arg]
    assert ctx["error"] is not None
