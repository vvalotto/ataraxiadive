from datetime import date
from typing import Any

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import TorneoCerrado, TransicionEstadoInvalida
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede

scenarios("../US-3.1.1-aggregate-torneo.feature")


def _make_torneo(**kwargs: Any) -> Torneo:
    defaults: dict[str, Any] = dict(
        nombre="Open Nacional 2026",
        descripcion="Torneo anual",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede(nombre="Club Náutico", ciudad="Buenos Aires", pais="Argentina"),
        entidad_organizadora=EntidadOrganizadora(nombre="FADA", tipo="FEDERACION"),
    )
    defaults.update(kwargs)
    return Torneo(**defaults)


def _avanzar_hasta(torneo: Torneo, estado: EstadoTorneo) -> None:
    acciones = {
        EstadoTorneo.INSCRIPCION_ABIERTA: torneo.abrir_inscripcion,
        EstadoTorneo.PREPARACION: torneo.cerrar_inscripcion,
        EstadoTorneo.EJECUCION: torneo.iniciar_ejecucion,
        EstadoTorneo.PREMIACION: torneo.iniciar_premiacion,
        EstadoTorneo.CERRADO: torneo.cerrar,
    }
    for s in [
        EstadoTorneo.INSCRIPCION_ABIERTA,
        EstadoTorneo.PREPARACION,
        EstadoTorneo.EJECUCION,
        EstadoTorneo.PREMIACION,
        EstadoTorneo.CERRADO,
    ]:
        if torneo.estado == estado:
            break
        acciones[s]()


@pytest.fixture
def ctx() -> dict[str, Any]:
    return {"torneo": None, "exc": None, "nombre": None}


# ── Givens ────────────────────────────────────────────────────────────────────


@given("un nombre inválido vacío")
def nombre_vacio(ctx: dict[str, Any]) -> None:
    ctx["nombre"] = ""


@given("un nombre inválido de solo espacios")
def nombre_espacios(ctx: dict[str, Any]) -> None:
    ctx["nombre"] = "   "


@given(parsers.parse("fecha_inicio {fi} y fecha_fin {ff}"))
def fechas_invalidas(fi: str, ff: str, ctx: dict[str, Any]) -> None:
    ctx["fecha_inicio"] = date.fromisoformat(fi)
    ctx["fecha_fin"] = date.fromisoformat(ff)


@given("un Torneo en estado CREADO")
def torneo_creado(ctx: dict[str, Any]) -> None:
    ctx["torneo"] = _make_torneo()


@given("un Torneo en estado INSCRIPCION_ABIERTA")
def torneo_inscripcion(ctx: dict[str, Any]) -> None:
    t = _make_torneo()
    t.abrir_inscripcion()
    ctx["torneo"] = t


@given("un Torneo en estado PREPARACION")
def torneo_preparacion(ctx: dict[str, Any]) -> None:
    t = _make_torneo()
    _avanzar_hasta(t, EstadoTorneo.PREPARACION)
    ctx["torneo"] = t


@given("un Torneo en estado EJECUCION")
def torneo_ejecucion(ctx: dict[str, Any]) -> None:
    t = _make_torneo()
    _avanzar_hasta(t, EstadoTorneo.EJECUCION)
    ctx["torneo"] = t


@given("un Torneo en estado CERRADO")
def torneo_cerrado(ctx: dict[str, Any]) -> None:
    t = _make_torneo()
    _avanzar_hasta(t, EstadoTorneo.CERRADO)
    ctx["torneo"] = t


@given("un Torneo en estado CANCELADO")
def torneo_cancelado(ctx: dict[str, Any]) -> None:
    t = _make_torneo()
    t.abrir_inscripcion()
    t.cancelar()
    ctx["torneo"] = t


# ── Whens ─────────────────────────────────────────────────────────────────────


@when("se instancia un Torneo con los datos válidos")
def instanciar_torneo_valido(ctx: dict[str, Any]) -> None:
    ctx["torneo"] = _make_torneo()


@when("se instancia un Torneo con nombre inválido")
def instanciar_con_nombre(ctx: dict[str, Any]) -> None:
    try:
        ctx["torneo"] = _make_torneo(nombre=ctx["nombre"])
    except Exception as exc:
        ctx["exc"] = exc


@when("se instancia un Torneo con esas fechas")
def instanciar_con_fechas(ctx: dict[str, Any]) -> None:
    try:
        ctx["torneo"] = _make_torneo(
            fecha_inicio=ctx["fecha_inicio"],
            fecha_fin=ctx["fecha_fin"],
        )
    except Exception as exc:
        ctx["exc"] = exc


@when(
    "se ejecutan en secuencia abrir_inscripcion, cerrar_inscripcion, iniciar_ejecucion, iniciar_premiacion, cerrar"
)
def ciclo_completo(ctx: dict[str, Any]) -> None:
    t = ctx["torneo"]
    t.abrir_inscripcion()
    t.cerrar_inscripcion()
    t.iniciar_ejecucion()
    t.iniciar_premiacion()
    t.cerrar()


@when("se llama volver_a_preparacion")
def llamar_volver_preparacion(ctx: dict[str, Any]) -> None:
    ctx["torneo"].volver_a_preparacion()


@when("se llama cancelar")
def llamar_cancelar(ctx: dict[str, Any]) -> None:
    try:
        ctx["torneo"].cancelar()
    except Exception as exc:
        ctx["exc"] = exc


@when("se llama iniciar_ejecucion directamente")
def llamar_iniciar_ejecucion(ctx: dict[str, Any]) -> None:
    try:
        ctx["torneo"].iniciar_ejecucion()
    except Exception as exc:
        ctx["exc"] = exc


@when("se llama abrir_inscripcion")
def llamar_abrir_inscripcion(ctx: dict[str, Any]) -> None:
    try:
        ctx["torneo"].abrir_inscripcion()
    except Exception as exc:
        ctx["exc"] = exc


# ── Thens ─────────────────────────────────────────────────────────────────────


@then(parsers.parse("el estado es {estado}"))
def verificar_estado(estado: str, ctx: dict[str, Any]) -> None:
    assert ctx["torneo"].estado == EstadoTorneo(estado)


@then(parsers.parse("el estado final es {estado}"))
def verificar_estado_final(estado: str, ctx: dict[str, Any]) -> None:
    assert ctx["torneo"].estado == EstadoTorneo(estado)


@then("el torneo_id es un UUID válido")
def verificar_uuid(ctx: dict[str, Any]) -> None:
    from uuid import UUID

    assert isinstance(ctx["torneo"].torneo_id, UUID)


@then(parsers.parse("se lanza ValueError con mensaje sobre {tema}"))
def verificar_value_error(tema: str, ctx: dict[str, Any]) -> None:
    assert isinstance(ctx.get("exc"), ValueError)


@then("se lanza TorneoCerrado")
def verificar_torneo_cerrado(ctx: dict[str, Any]) -> None:
    assert isinstance(ctx.get("exc"), TorneoCerrado)


@then("se lanza TransicionEstadoInvalida")
def verificar_transicion_invalida(ctx: dict[str, Any]) -> None:
    assert isinstance(ctx.get("exc"), TransicionEstadoInvalida)
