"""Step definitions BDD — US-2.3.1: Ejecución Multi-Andarivel.

Verifica el invariante INV-C-05 (conflicto de andarivel) y el Read Model
AndarivelesActivos en el endpoint GET /competencia/{id}/andariveles.

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
from competencia.application.commands.llamar_atleta import (
    AndarivelesConflicto,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
)
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
from competencia.infrastructure.repositories.andariveles_activos_adapter import (
    AndarivelesActivosAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter

scenarios("../US-2.3.1-ejecucion-multi-andarivel.feature")

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

_OT_BASE = datetime(2026, 3, 27, 10, 0, 0, tzinfo=timezone.utc)
_JUEZ = "juez-001"
_DESCRIPTOR = DisciplinaDescriptorAdapter()
_ESTADO_STUB = StubCompetenciaEstadoAdapter()


# ── Store factory ──────────────────────────────────────────────────────────────


def _make_store() -> SQLiteEventStore:
    db_path = f"{tempfile.mkdtemp()}/bdd_231.db"

    async def _init() -> None:
        async with aiosqlite.connect(db_path) as db:
            await db.execute(_CREATE_TABLE)
            await db.commit()

    asyncio.run(_init())
    return SQLiteEventStore(db_path)


def _run(coro):  # type: ignore[no-untyped-def]
    return asyncio.run(coro)


# ── Fixture de contexto ────────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict:  # type: ignore[type-arg]
    store = _make_store()
    app.dependency_overrides[get_event_store] = lambda: store
    client = TestClient(app)
    cid = uuid4()
    pid_a = uuid4()
    pid_b = uuid4()
    pid_c = uuid4()
    return {
        "store": store,
        "client": client,
        "cid": cid,
        "pid_a": pid_a,
        "pid_b": pid_b,
        "pid_c": pid_c,
        "exception": None,
        "response": None,
        "andariveles": 1,
    }


@pytest.fixture(autouse=True)
def cleanup_overrides() -> None:  # type: ignore[return]
    yield
    app.dependency_overrides.clear()


# ── Helpers async ──────────────────────────────────────────────────────────────


def _setup_competencia_en_ejecucion(
    store: SQLiteEventStore,
    cid: UUID,
    pid_a: UUID,
    pid_b: UUID,
    pid_c: UUID,
    andariveles: int = 2,
) -> None:
    """Setup completo: AP → ConfigOT → GenerarGrilla → ConfirmarGrilla → Iniciar."""
    # APs: A=300s, B=280s, C=260s (orden descendente → grilla)
    for pid, valor in [(pid_a, "300"), (pid_b, "280"), (pid_c, "260")]:
        _run(
            RegistrarAPHandler(store, _ESTADO_STUB, _DESCRIPTOR).handle(
                RegistrarAPCommand(
                    competencia_id=cid,
                    participante_id=pid,
                    disciplina=Disciplina.STA,
                    valor_ap=Decimal(valor),
                    unidad=UnidadMedida.Segundos,
                )
            )
        )

    # Configurar intervalo OT
    _run(
        ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=cid,
                disciplina=Disciplina.STA,
                intervalo_minutos=3,
                configurado_por=_JUEZ,
            )
        )
    )

    # Generar grilla con N andariveles
    _run(
        GenerarGrillaHandler(store, PerformancesAPAdapter(store), _DESCRIPTOR).handle(
            GenerarGrillaCommand(
                competencia_id=cid,
                disciplina=Disciplina.STA,
                ot_inicio=_OT_BASE,
                andariveles=andariveles,
            )
        )
    )

    # Confirmar y arrancar
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


def _llamar_atleta(
    store: SQLiteEventStore, cid: UUID, pid: UUID, andarivel: int, posicion: int
) -> None:
    adapter = AndarivelesActivosAdapter(store)
    _run(
        LlamarAtletaHandler(store, _ESTADO_STUB, adapter).handle(
            LlamarAtletaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.STA,
                ot_programado=_OT_BASE,
                posicion_grilla=posicion,
                andarivel=andarivel,
            )
        )
    )


def _completar_atleta(store: SQLiteEventStore, cid: UUID, pid: UUID) -> None:
    _run(
        RegistrarResultadoHandler(store, _DESCRIPTOR).handle(
            RegistrarResultadoCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.STA,
                valor_rp=Decimal("295"),
                unidad=UnidadMedida.Segundos,
                registrado_por=_JUEZ,
            )
        )
    )
    _run(
        AsignarTarjetaHandler(store).handle(
            AsignarTarjetaCommand(
                competencia_id=cid,
                participante_id=pid,
                disciplina=Disciplina.STA,
                tipo=TipoTarjeta.Blanca,
                asignada_por=_JUEZ,
            )
        )
    )


# ── Background ────────────────────────────────────────────────────────────────


@given(parsers.parse("una competencia STA en estado EnEjecucion con 2 andariveles"))
def setup_competencia_2_andariveles(ctx: dict) -> None:
    _setup_competencia_en_ejecucion(
        ctx["store"],
        ctx["cid"],
        ctx["pid_a"],
        ctx["pid_b"],
        ctx["pid_c"],
        andariveles=2,
    )
    ctx["andariveles"] = 2


@given(
    parsers.parse(
        "la grilla tiene pos 1 Atleta A andarivel 1, pos 2 Atleta B andarivel 2, pos 3 Atleta C andarivel 1"
    )
)
def grilla_ya_configurada(ctx: dict) -> None:
    # La grilla fue generada en el step anterior; solo verificamos que existe.
    response = ctx["client"].get(
        f"/competencia/{ctx['cid']}/grilla",
        params={"disciplina": "STA"},
    )
    assert response.status_code == 200
    entradas = response.json()
    assert len(entradas) == 3


# ── Scenario 1: sin conflicto ─────────────────────────────────────────────────


@when(parsers.parse("el juez llama a Atleta A en andarivel 1"))
def llamar_atleta_a(ctx: dict) -> None:
    _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_a"], andarivel=1, posicion=1)


@when(parsers.parse("el juez llama a Atleta B en andarivel 2"))
def llamar_atleta_b(ctx: dict) -> None:
    _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_b"], andarivel=2, posicion=2)


@then(parsers.parse("ambos AtletaLlamado persisten"))
def ambos_llamados_persisten(ctx: dict) -> None:
    response = ctx["client"].get(f"/competencia/{ctx['cid']}/events")
    assert response.status_code == 200
    eventos = response.json()["events"]
    llamados = [e for e in eventos if e["event_type"] == "AtletaLlamado"]
    assert len(llamados) == 2


@then(
    parsers.parse("GET andariveles muestra andarivel 1 ocupado por A y andarivel 2 ocupado por B")
)
def andariveles_ambos_ocupados(ctx: dict) -> None:
    response = ctx["client"].get(
        f"/competencia/{ctx['cid']}/andariveles",
        params={"disciplina": "STA", "andariveles": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["numero"] == 1
    assert data[0]["ocupado"] is True
    assert data[0]["atleta_id"] == str(ctx["pid_a"])
    assert data[1]["numero"] == 2
    assert data[1]["ocupado"] is True
    assert data[1]["atleta_id"] == str(ctx["pid_b"])


# ── Scenario 2: rechazo INV-C-05 ─────────────────────────────────────────────


@given(parsers.parse("Atleta A fue llamado y esta en estado Llamada en andarivel 1"))
def atleta_a_llamado_andarivel_1(ctx: dict) -> None:
    _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_a"], andarivel=1, posicion=1)


@when(parsers.parse("el juez intenta llamar a Atleta C en andarivel 1"))
def intentar_llamar_c_andarivel_ocupado(ctx: dict) -> None:
    try:
        _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_c"], andarivel=1, posicion=3)
    except AndarivelesConflicto as e:
        ctx["exception"] = e


@then(parsers.parse("el sistema rechaza con error AndarivelesConflicto"))
def rechaza_con_conflicto(ctx: dict) -> None:
    assert isinstance(ctx["exception"], AndarivelesConflicto)


@then(parsers.parse("ningun evento es persistido"))
def ningun_evento_persistido(ctx: dict) -> None:
    response = ctx["client"].get(f"/competencia/{ctx['cid']}/events")
    eventos = response.json()["events"]
    llamados = [e for e in eventos if e["event_type"] == "AtletaLlamado"]
    # Solo el AtletaLlamado de A (el de C fue rechazado)
    assert len(llamados) == 1
    assert llamados[0]["performance_id"] is not None


# ── Scenario 3: andarivel liberado tras resultado ────────────────────────────


@given(parsers.parse("Atleta A fue llamado en andarivel 1 y completo con tarjeta blanca"))
def atleta_a_completo(ctx: dict) -> None:
    _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_a"], andarivel=1, posicion=1)
    _completar_atleta(ctx["store"], ctx["cid"], ctx["pid_a"])


@when(parsers.parse("el juez llama a Atleta C en andarivel 1"))
def llamar_atleta_c(ctx: dict) -> None:
    _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_c"], andarivel=1, posicion=3)


@then(parsers.parse("AtletaLlamado de Atleta C persiste"))
def atleta_c_llamado_persiste(ctx: dict) -> None:
    response = ctx["client"].get(f"/competencia/{ctx['cid']}/events")
    eventos = response.json()["events"]
    llamados = [e for e in eventos if e["event_type"] == "AtletaLlamado"]
    pids_llamados = [e["performance_id"] for e in llamados]
    # Debe haber al menos 2 llamados (A y C)
    assert len(llamados) >= 2


@then(parsers.parse("GET andariveles muestra andarivel 1 ocupado por C"))
def andarivel_1_ocupado_por_c(ctx: dict) -> None:
    response = ctx["client"].get(
        f"/competencia/{ctx['cid']}/andariveles",
        params={"disciplina": "STA", "andariveles": 2},
    )
    assert response.status_code == 200
    data = response.json()
    assert data[0]["numero"] == 1
    assert data[0]["ocupado"] is True
    assert data[0]["atleta_id"] == str(ctx["pid_c"])


# ── Scenario 4: AndarivelesActivos refleja estado ────────────────────────────


@given(parsers.parse("Atleta A fue llamado en andarivel 1 y esta en Llamada"))
def atleta_a_en_llamada(ctx: dict) -> None:
    _llamar_atleta(ctx["store"], ctx["cid"], ctx["pid_a"], andarivel=1, posicion=1)


@when(parsers.parse("se consulta GET andariveles de la competencia"))
def consultar_andariveles(ctx: dict) -> None:
    ctx["response"] = ctx["client"].get(
        f"/competencia/{ctx['cid']}/andariveles",
        params={"disciplina": "STA", "andariveles": 2},
    )


@then(parsers.parse("la respuesta muestra andarivel 1 ocupado con atleta A"))
def andarivel_1_con_a(ctx: dict) -> None:
    data = ctx["response"].json()
    assert data[0]["numero"] == 1
    assert data[0]["ocupado"] is True
    assert data[0]["atleta_id"] == str(ctx["pid_a"])


@then(parsers.parse("andarivel 2 libre"))
def andarivel_2_libre(ctx: dict) -> None:
    data = ctx["response"].json()
    assert data[1]["numero"] == 2
    assert data[1]["ocupado"] is False


# ── Scenario 5: GenerarGrilla distribuye andariveles ─────────────────────────


@given(
    parsers.parse(
        "una competencia STA en estado Preparacion con 4 atletas y 2 andariveles configurados"
    )
)
def setup_4_atletas_2_andariveles(ctx: dict) -> None:
    """4 atletas con AP, intervalo configurado, grilla generada con 2 andariveles."""
    cid = uuid4()
    ctx["cid_5"] = cid
    pids = [uuid4() for _ in range(4)]
    ctx["pids_5"] = pids
    store = ctx["store"]

    valores = ["300", "280", "260", "240"]
    for pid, valor in zip(pids, valores):
        _run(
            RegistrarAPHandler(store, _ESTADO_STUB, _DESCRIPTOR).handle(
                RegistrarAPCommand(
                    competencia_id=cid,
                    participante_id=pid,
                    disciplina=Disciplina.STA,
                    valor_ap=Decimal(valor),
                    unidad=UnidadMedida.Segundos,
                )
            )
        )

    _run(
        ConfigurarIntervaloOTHandler(store).handle(
            ConfigurarIntervaloOTCommand(
                competencia_id=cid,
                disciplina=Disciplina.STA,
                intervalo_minutos=3,
                configurado_por=_JUEZ,
            )
        )
    )

    _run(
        GenerarGrillaHandler(store, PerformancesAPAdapter(store), _DESCRIPTOR).handle(
            GenerarGrillaCommand(
                competencia_id=cid,
                disciplina=Disciplina.STA,
                ot_inicio=_OT_BASE,
                andariveles=2,
            )
        )
    )


@when(parsers.parse("se genera la grilla"))
def grilla_generada(ctx: dict) -> None:
    # La grilla ya fue generada en el step dado
    pass


@then(parsers.parse("las posiciones 1 y 3 quedan en andarivel 1"))
def posiciones_impares_andarivel_1(ctx: dict) -> None:
    response = ctx["client"].get(
        f"/competencia/{ctx['cid_5']}/grilla",
        params={"disciplina": "STA"},
    )
    assert response.status_code == 200
    entradas = {e["posicion"]: e["andarivel"] for e in response.json()}
    assert entradas[1] == 1
    assert entradas[3] == 1


@then(parsers.parse("las posiciones 2 y 4 quedan en andarivel 2"))
def posiciones_pares_andarivel_2(ctx: dict) -> None:
    response = ctx["client"].get(
        f"/competencia/{ctx['cid_5']}/grilla",
        params={"disciplina": "STA"},
    )
    assert response.status_code == 200
    entradas = {e["posicion"]: e["andarivel"] for e in response.json()}
    assert entradas[2] == 2
    assert entradas[4] == 2
