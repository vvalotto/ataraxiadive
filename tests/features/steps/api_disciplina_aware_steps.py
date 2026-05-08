"""Step definitions BDD — US-2.2.2: API Disciplina-Aware.

Verifica validación de unidades y ordenamiento de grilla en los endpoints
de la interfaz del juez.

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
from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
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
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
    UnidadIncompatible,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from tests.features.steps._stubs import StubPerformancesAPPort

scenarios("../US-2.2.2-api-disciplina-aware.feature")

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

_OT = datetime(2026, 3, 27, 10, 0, 0, tzinfo=timezone.utc)
_JUEZ = "juez-001"
_DESCRIPTOR = DisciplinaDescriptorAdapter()
_ESTADO_STUB = StubCompetenciaEstadoAdapter()


# ── Store factory ─────────────────────────────────────────────────────────────


def _make_store() -> SQLiteEventStore:
    db_path = f"{tempfile.mkdtemp()}/bdd_222.db"

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
        # STA background competencia
        "sta_cid": uuid4(),
        "sta_p1": uuid4(),  # AP 120s
        "sta_p2": uuid4(),  # AP 180s
        "sta_p3": uuid4(),  # AP 300s
        # Competencia actual (puede ser distinta a la STA)
        "current_cid": None,
        "current_pid": None,
        "current_disciplina": Disciplina.STA,
        "exception": None,
        "response": None,
    }


@pytest.fixture(autouse=True)
def cleanup_overrides() -> None:  # type: ignore[return]
    yield
    app.dependency_overrides.clear()


# ── Helpers async ─────────────────────────────────────────────────────────────


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


def _registrar_ap(
    store: SQLiteEventStore,
    cid: UUID,
    pid: UUID,
    valor: str,
    disciplina: Disciplina,
    unidad: UnidadMedida,
) -> None:
    _run(
        RegistrarAPHandler(store, _ESTADO_STUB, _DESCRIPTOR).handle(
            RegistrarAPCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disciplina,
                valor_ap=Decimal(valor),
                unidad=unidad,
            )
        )
    )


def _llamar(
    store: SQLiteEventStore, cid: UUID, pid: UUID, disciplina: Disciplina, posicion: int
) -> None:
    _run(
        LlamarAtletaHandler(store, _ESTADO_STUB).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disciplina,
                ot_programado=_OT,
                posicion_grilla=posicion,
            )
        )
    )


def _completar(
    store: SQLiteEventStore,
    cid: UUID,
    pid: UUID,
    disciplina: Disciplina,
    valor: str,
    unidad: UnidadMedida,
) -> None:
    _run(
        RegistrarResultadoHandler(store, _DESCRIPTOR).handle(
            RegistrarResultadoCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disciplina,
                valor_rp=Decimal(valor),
                unidad=unidad,
                registrado_por=_JUEZ,
            )
        )
    )
    _run(
        AsignarTarjetaHandler(store).handle(
            AsignarTarjetaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=disciplina,
                tipo=TipoTarjeta.Blanca,
                asignada_por=_JUEZ,
            )
        )
    )


def _setup_competencia_sta_con_grilla(ctx: dict) -> None:  # type: ignore[type-arg]
    """Registra 3 APs STA, genera grilla ordenada e inicia la competencia."""
    store = ctx["store"]
    cid = ctx["sta_cid"]
    p1, p2, p3 = ctx["sta_p1"], ctx["sta_p2"], ctx["sta_p3"]

    _registrar_ap(store, cid, p1, "120", Disciplina.STA, UnidadMedida.Segundos)
    _registrar_ap(store, cid, p2, "180", Disciplina.STA, UnidadMedida.Segundos)
    _registrar_ap(store, cid, p3, "300", Disciplina.STA, UnidadMedida.Segundos)

    _run(
        ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=cid,
                disciplina=Disciplina.STA,
                intervalo_minutos=5,
                configurado_por=_JUEZ,
            )
        )
    )
    _run(
        GenerarGrillaHandler(store, StubPerformancesAPPort(store), _DESCRIPTOR).handle(
            GenerarGrillaCommand(competencia_id=cid, disciplina=Disciplina.STA, ot_inicio=_OT)
        )
    )
    _run(
        ConfirmarGrillaHandler(store).handle(
            ConfirmarGrillaCommand(competencia_id=cid, disciplina=Disciplina.STA)
        )
    )
    _run(
        IniciarCompetenciaHandler(store).handle(
            IniciarCompetenciaCommand(competencia_id=cid, disciplina=Disciplina.STA, juez_id=_JUEZ)
        )
    )
    ctx["current_cid"] = cid
    ctx["current_disciplina"] = Disciplina.STA


# ── Background ────────────────────────────────────────────────────────────────


@given("una competencia en estado EnEjecucion con 3 atletas en grilla STA")
def step_background_sta_en_ejecucion(ctx: dict) -> None:  # type: ignore[type-arg]
    _setup_competencia_sta_con_grilla(ctx)


@given(
    "el orden de grilla es posicion 1 con AP 120s, posicion 2 con AP 180s, posicion 3 con AP 300s"
)
def step_orden_grilla(ctx: dict) -> None:  # type: ignore[type-arg]
    # El orden es garantizado por el dominio (STA: menor AP primero).
    # Este step documenta la postcondición del Background.
    pass


# ── Given — estados de performance ────────────────────────────────────────────


@given("el atleta en posicion 1 fue llamado")
def step_atleta_pos1_llamado(ctx: dict) -> None:  # type: ignore[type-arg]
    _llamar(ctx["store"], ctx["sta_cid"], ctx["sta_p1"], Disciplina.STA, posicion=1)
    ctx["current_pid"] = ctx["sta_p1"]


@given("el atleta en posicion 1 fue llamado y completo su performance")
def step_atleta_pos1_completo(ctx: dict) -> None:  # type: ignore[type-arg]
    _llamar(ctx["store"], ctx["sta_cid"], ctx["sta_p1"], Disciplina.STA, posicion=1)
    _completar(
        ctx["store"], ctx["sta_cid"], ctx["sta_p1"], Disciplina.STA, "290", UnidadMedida.Segundos
    )


@given("el atleta en posicion 1 esta en estado Llamada para STA")
def step_atleta_pos1_en_llamada_sta(ctx: dict) -> None:  # type: ignore[type-arg]
    _llamar(ctx["store"], ctx["sta_cid"], ctx["sta_p1"], Disciplina.STA, posicion=1)
    ctx["current_cid"] = ctx["sta_cid"]
    ctx["current_pid"] = ctx["sta_p1"]
    ctx["current_disciplina"] = Disciplina.STA


@given("una competencia en estado EnEjecucion con disciplina DNF")
def step_competencia_dnf(ctx: dict) -> None:  # type: ignore[type-arg]
    store = ctx["store"]
    cid = uuid4()
    pid = uuid4()
    _registrar_ap(store, cid, pid, "80", Disciplina.DNF, UnidadMedida.Metros)
    _run(
        ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=cid,
                disciplina=Disciplina.DNF,
                intervalo_minutos=5,
                configurado_por=_JUEZ,
            )
        )
    )
    _run(
        GenerarGrillaHandler(store, StubPerformancesAPPort(store), _DESCRIPTOR).handle(
            GenerarGrillaCommand(competencia_id=cid, disciplina=Disciplina.DNF, ot_inicio=_OT)
        )
    )
    _run(
        ConfirmarGrillaHandler(store).handle(
            ConfirmarGrillaCommand(competencia_id=cid, disciplina=Disciplina.DNF)
        )
    )
    _run(
        IniciarCompetenciaHandler(store).handle(
            IniciarCompetenciaCommand(competencia_id=cid, disciplina=Disciplina.DNF, juez_id=_JUEZ)
        )
    )
    ctx["current_cid"] = cid
    ctx["current_pid"] = pid
    ctx["current_disciplina"] = Disciplina.DNF


@given("el atleta en posicion 1 fue llamado para DNF")
def step_atleta_pos1_llamado_dnf(ctx: dict) -> None:  # type: ignore[type-arg]
    _llamar(ctx["store"], ctx["current_cid"], ctx["current_pid"], Disciplina.DNF, posicion=1)


@given("una competencia STA en estado Preparacion con un atleta")
def step_competencia_sta_preparacion(ctx: dict) -> None:  # type: ignore[type-arg]
    cid = uuid4()
    pid = uuid4()
    ctx["current_cid"] = cid
    ctx["current_pid"] = pid
    ctx["current_disciplina"] = Disciplina.STA


@given("una competencia DNF con atleta en estado Llamada")
def step_competencia_dnf_atleta_llamado(ctx: dict) -> None:  # type: ignore[type-arg]
    store = ctx["store"]
    cid = uuid4()
    pid = uuid4()
    _registrar_ap(store, cid, pid, "75", Disciplina.DNF, UnidadMedida.Metros)
    _llamar(store, cid, pid, Disciplina.DNF, posicion=1)
    ctx["current_cid"] = cid
    ctx["current_pid"] = pid
    ctx["current_disciplina"] = Disciplina.DNF


# ── When ──────────────────────────────────────────────────────────────────────


@when(parsers.parse("el juez registra resultado de {valor} Segundos para STA"))
def step_registrar_resultado_segundos(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    try:
        _run(
            RegistrarResultadoHandler(ctx["store"], _DESCRIPTOR).handle(
                RegistrarResultadoCommand(
                    competencia_id=ctx["current_cid"],
                    participante_id=ctx["current_pid"],
                    disciplina=Disciplina.STA,
                    valor_rp=Decimal(valor),
                    unidad=UnidadMedida.Segundos,
                    registrado_por=_JUEZ,
                )
            )
        )
    except Exception as e:
        ctx["exception"] = e


@when(parsers.parse("el juez intenta registrar resultado de {valor} Metros para STA"))
def step_registrar_resultado_metros_sta(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    try:
        _run(
            RegistrarResultadoHandler(ctx["store"], _DESCRIPTOR).handle(
                RegistrarResultadoCommand(
                    competencia_id=ctx["current_cid"],
                    participante_id=ctx["current_pid"],
                    disciplina=Disciplina.STA,
                    valor_rp=Decimal(valor),
                    unidad=UnidadMedida.Metros,
                    registrado_por=_JUEZ,
                )
            )
        )
    except Exception as e:
        ctx["exception"] = e


@when(parsers.parse("el juez registra resultado de {valor} Metros para DNF"))
def step_registrar_resultado_metros_dnf(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    try:
        _run(
            RegistrarResultadoHandler(ctx["store"], _DESCRIPTOR).handle(
                RegistrarResultadoCommand(
                    competencia_id=ctx["current_cid"],
                    participante_id=ctx["current_pid"],
                    disciplina=Disciplina.DNF,
                    valor_rp=Decimal(valor),
                    unidad=UnidadMedida.Metros,
                    registrado_por=_JUEZ,
                )
            )
        )
    except Exception as e:
        ctx["exception"] = e


@when(parsers.parse("el atleta intenta declarar AP de {valor} Metros para STA"))
def step_declarar_ap_metros_sta(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    try:
        _run(
            RegistrarAPHandler(ctx["store"], _ESTADO_STUB, _DESCRIPTOR).handle(
                RegistrarAPCommand(
                    competencia_id=ctx["current_cid"],
                    participante_id=ctx["current_pid"],
                    disciplina=Disciplina.STA,
                    valor_ap=Decimal(valor),
                    unidad=UnidadMedida.Metros,
                )
            )
        )
    except Exception as e:
        ctx["exception"] = e


@when("el juez consulta las proximas performances")
def step_consultar_proximas(ctx: dict) -> None:  # type: ignore[type-arg]
    cid = ctx["current_cid"]
    ctx["response"] = ctx["client"].get(f"/competencia/{cid}/performance/proximas?disciplina=STA")


@when("el juez consulta la performance actual")
def step_consultar_actual(ctx: dict) -> None:  # type: ignore[type-arg]
    cid = ctx["current_cid"]
    ctx["response"] = ctx["client"].get(f"/competencia/{cid}/performance/actual")


@when("el juez consulta la performance actual para DNF")
def step_consultar_actual_dnf(ctx: dict) -> None:  # type: ignore[type-arg]
    cid = ctx["current_cid"]
    ctx["response"] = ctx["client"].get(f"/competencia/{cid}/performance/actual")


# ── Then ──────────────────────────────────────────────────────────────────────


@then(parsers.parse("el evento ResultadoRegistrado persiste con unidad {unidad}"))
def step_evento_persiste_unidad(ctx: dict, unidad: str) -> None:  # type: ignore[type-arg]
    assert ctx["exception"] is None, f"Excepción inesperada: {ctx['exception']}"
    # Verificar en el event store que se persistió ResultadoRegistrado con la unidad correcta
    store: SQLiteEventStore = ctx["store"]
    cid = ctx["current_cid"]
    pid = ctx["current_pid"]
    stream_id = f"performance-{cid}-{pid}-STA"
    events = _run(store.load(stream_id))
    resultado = next((e for e in events if e["event_type"] == "ResultadoRegistrado"), None)
    assert resultado is not None, "No se encontró evento ResultadoRegistrado"
    assert resultado["payload"]["unidad"] == unidad


@then("el sistema rechaza con error UnidadIncompatible")
def step_rechaza_unidad_incompatible(ctx: dict) -> None:  # type: ignore[type-arg]
    assert ctx["exception"] is not None, "Se esperaba una excepción pero no se lanzó"
    assert isinstance(
        ctx["exception"], UnidadIncompatible
    ), f"Excepción incorrecta: {type(ctx['exception'])}"


@then("ningun evento es persistido")
def step_ningun_evento_persistido(ctx: dict) -> None:  # type: ignore[type-arg]
    store: SQLiteEventStore = ctx["store"]
    cid = ctx["current_cid"]
    pid = ctx["current_pid"]
    stream_id = f"performance-{cid}-{pid}-STA"
    events = _run(store.load(stream_id))
    # Solo debe existir el APRegistrado y AtletaLlamado, no ResultadoRegistrado
    resultado = next((e for e in events if e["event_type"] == "ResultadoRegistrado"), None)
    assert resultado is None, "Se persistió ResultadoRegistrado cuando no debería"


@then(parsers.parse("el evento ResultadoRegistrado persiste con valor {valor} y unidad {unidad}"))
def step_evento_persiste_valor_unidad(ctx: dict, valor: str, unidad: str) -> None:  # type: ignore[type-arg]
    assert ctx["exception"] is None, f"Excepción inesperada: {ctx['exception']}"
    store: SQLiteEventStore = ctx["store"]
    cid = ctx["current_cid"]
    pid = ctx["current_pid"]
    stream_id = f"performance-{cid}-{pid}-DNF"
    events = _run(store.load(stream_id))
    resultado = next((e for e in events if e["event_type"] == "ResultadoRegistrado"), None)
    assert resultado is not None, "No se encontró evento ResultadoRegistrado"
    assert resultado["payload"]["unidad"] == unidad
    assert resultado["payload"]["valor_rp"] == valor


@then(parsers.parse("el primer resultado es el atleta en posicion 2 con AP {valor}s"))
def step_primer_resultado_pos2(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    data = ctx["response"].json()
    assert len(data) >= 1, f"Lista vacía: {data}"
    assert data[0]["posicion"] == 2, f"Esperado posicion=2, obtenido {data[0]['posicion']}"
    assert (
        data[0]["ap_declarado"] == valor
    ), f"Esperado AP={valor}, obtenido {data[0]['ap_declarado']}"


@then(parsers.parse("el segundo resultado es el atleta en posicion 3 con AP {valor}s"))
def step_segundo_resultado_pos3(ctx: dict, valor: str) -> None:  # type: ignore[type-arg]
    data = ctx["response"].json()
    assert len(data) >= 2, f"Menos de 2 resultados: {data}"
    assert data[1]["posicion"] == 3, f"Esperado posicion=3, obtenido {data[1]['posicion']}"
    assert (
        data[1]["ap_declarado"] == valor
    ), f"Esperado AP={valor}, obtenido {data[1]['ap_declarado']}"


@then(parsers.parse("la respuesta incluye unidad_esperada {unidad}"))
def step_respuesta_incluye_unidad_esperada(ctx: dict, unidad: str) -> None:  # type: ignore[type-arg]
    data = ctx["response"].json()
    assert data is not None, "La respuesta es None"
    assert "unidad_esperada" in data, f"Campo unidad_esperada no encontrado en {data}"
    assert (
        data["unidad_esperada"] == unidad
    ), f"Esperado unidad_esperada={unidad}, obtenido {data['unidad_esperada']}"
