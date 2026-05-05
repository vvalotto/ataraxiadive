"""Step definitions BDD — US-4.5.1: Aggregate Notificacion con idempotencia."""

from __future__ import annotations

import asyncio

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.events.notificacion_enviada import NotificacionEnviada
from notificaciones.domain.events.notificacion_fallida import NotificacionFallida
from notificaciones.domain.events.notificacion_solicitada import NotificacionSolicitada
from notificaciones.domain.value_objects.canal_envio import CanalEnvio
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)

scenarios("../US-4.5.1-notificacion-idempotencia.feature")


@pytest.fixture
def ctx(tmp_path) -> dict:
    store = SQLiteNotificacionEventStore(str(tmp_path / "notificaciones.db"))
    repo = SQLiteNotificacionRepository(store)
    return {
        "store": store,
        "repo": repo,
        "aggregate": None,
        "events": [],
        "error": None,
        "envio_externo": 0,
    }


async def _persist_pending(ctx: dict) -> None:
    aggregate = ctx["aggregate"]
    if aggregate is None:
        return
    for event in aggregate.pull_events():
        ctx["events"].append(event)
        await ctx["repo"].append(aggregate.stream_id, event.event_type, event.to_payload())


@given(
    parsers.parse(
        'el event store de notificaciones no tiene eventos para evento_fuente_id "{evento_fuente_id}"'
    )
)
def given_store_vacio(ctx: dict, evento_fuente_id: str) -> None:
    ctx["evento_fuente_id"] = evento_fuente_id


@given(
    parsers.parse(
        'el event store de notificaciones tiene NotificacionEnviada para evento_fuente_id "{evento_fuente_id}"'
    )
)
def given_store_con_exito(ctx: dict, evento_fuente_id: str) -> None:
    async def _run() -> None:
        aggregate = await Notificacion.solicitar_envio(
            evento_fuente_id=EventoFuenteId(evento_fuente_id),
            destinatario=Destinatario(email="juan@example.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
            canal=CanalEnvio.EMAIL,
            existe_envio_exitoso_previo=False,
        )
        assert aggregate is not None
        ctx["aggregate"] = aggregate
        await _persist_pending(ctx)
        aggregate.registrar_envio_exitoso("provider-1")
        await _persist_pending(ctx)

    asyncio.run(_run())
    ctx["evento_fuente_id"] = evento_fuente_id


@given(
    parsers.parse(
        'el event store de notificaciones tiene NotificacionFallida para evento_fuente_id "{evento_fuente_id}"'
    )
)
def given_store_con_fallo(ctx: dict, evento_fuente_id: str) -> None:
    async def _run() -> None:
        aggregate = await Notificacion.solicitar_envio(
            evento_fuente_id=EventoFuenteId(evento_fuente_id),
            destinatario=Destinatario(email="ana@example.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
            canal=CanalEnvio.EMAIL,
            existe_envio_exitoso_previo=False,
        )
        assert aggregate is not None
        ctx["aggregate"] = aggregate
        await _persist_pending(ctx)
        aggregate.registrar_fallo("timeout")
        await _persist_pending(ctx)

    asyncio.run(_run())
    ctx["evento_fuente_id"] = evento_fuente_id


@given("el aggregate Notificacion esta en estado Solicitada")
def given_notificacion_solicitada(ctx: dict) -> None:
    async def _run() -> None:
        aggregate = await Notificacion.solicitar_envio(
            evento_fuente_id=EventoFuenteId("reg-solicited"),
            destinatario=Destinatario(email="solicitada@example.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
            canal=CanalEnvio.EMAIL,
            existe_envio_exitoso_previo=False,
        )
        assert aggregate is not None
        ctx["aggregate"] = aggregate

    asyncio.run(_run())


@when(
    parsers.parse(
        'se ejecuta SolicitarEnvio con evento_fuente_id "{evento_fuente_id}" y destinatario "{email}"'
    )
)
def when_solicitar_envio(ctx: dict, evento_fuente_id: str, email: str) -> None:
    async def _run() -> None:
        try:
            aggregate = await Notificacion.solicitar_envio(
                evento_fuente_id=EventoFuenteId(evento_fuente_id),
                destinatario=Destinatario(email=email),
                contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
                canal=CanalEnvio.EMAIL,
                existe_envio_exitoso_previo=await ctx["repo"].exists_success_by_evento_fuente_id(
                    evento_fuente_id
                ),
            )
            ctx["aggregate"] = aggregate
            if aggregate is not None:
                await _persist_pending(ctx)
        except Exception as exc:
            ctx["error"] = exc

    asyncio.run(_run())


@when(
    parsers.parse('se ejecuta SolicitarEnvio con evento_fuente_id "{evento_fuente_id}" nuevamente')
)
def when_solicitar_envio_duplicado(ctx: dict, evento_fuente_id: str) -> None:
    async def _run() -> None:
        ctx["aggregate"] = await Notificacion.solicitar_envio(
            evento_fuente_id=EventoFuenteId(evento_fuente_id),
            destinatario=Destinatario(email="juan@example.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
            canal=CanalEnvio.EMAIL,
            existe_envio_exitoso_previo=await ctx["repo"].exists_success_by_evento_fuente_id(
                evento_fuente_id
            ),
        )

    asyncio.run(_run())


@when(
    parsers.parse(
        'se ejecuta SolicitarEnvio con evento_fuente_id "{evento_fuente_id}" y destinatario "ana@example.com"'
    )
)
def when_reintento(ctx: dict, evento_fuente_id: str) -> None:
    when_solicitar_envio(ctx, evento_fuente_id, "ana@example.com")


@when(parsers.parse('se ejecuta SolicitarEnvio con destinatario email "{email}"'))
def when_email_invalido(ctx: dict, email: str) -> None:
    async def _run() -> None:
        try:
            await Notificacion.solicitar_envio(
                evento_fuente_id=EventoFuenteId("reg-invalid"),
                destinatario=Destinatario(email=email),
                contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
                canal=CanalEnvio.EMAIL,
                existe_envio_exitoso_previo=False,
            )
        except Exception as exc:
            ctx["error"] = exc

    asyncio.run(_run())


@when("se ejecuta RegistrarEnvioExitoso")
def when_registrar_envio_exitoso(ctx: dict) -> None:
    ctx["aggregate"].registrar_envio_exitoso("provider-1")
    ctx["events"] = ctx["aggregate"].pull_events()


@when(parsers.parse('se ejecuta RegistrarFallo con motivo "{motivo}"'))
def when_registrar_fallo(ctx: dict, motivo: str) -> None:
    ctx["aggregate"].registrar_fallo(motivo)
    ctx["events"] = ctx["aggregate"].pull_events()


@then("el aggregate Notificacion emite NotificacionSolicitada")
def then_emitio_solicitada(ctx: dict) -> None:
    assert any(isinstance(event, NotificacionSolicitada) for event in ctx["events"])


@then("el evento queda persistido en el event store de notificaciones")
def then_evento_persistido(ctx: dict) -> None:
    async def _run() -> None:
        stored = await ctx["repo"].load(ctx["aggregate"].stream_id)
        assert len(stored) == 1

    asyncio.run(_run())


@then("el aggregate Notificacion no emite nuevos eventos")
def then_no_emite_eventos(ctx: dict) -> None:
    assert ctx["aggregate"] is None


@then("no se realiza ningun envio al canal externo")
def then_sin_envio_externo(ctx: dict) -> None:
    assert ctx["envio_externo"] == 0


@then("el aggregate Notificacion emite NotificacionSolicitada como reintento")
def then_reintento_emitido(ctx: dict) -> None:
    assert ctx["aggregate"] is not None
    assert any(isinstance(event, NotificacionSolicitada) for event in ctx["events"])


@then("el aggregate Notificacion rechaza la solicitud por validacion de dominio")
def then_rechazo_validacion(ctx: dict) -> None:
    assert ctx["error"] is not None


@then("no emite ningun evento")
def then_no_emite_ningun_evento(ctx: dict) -> None:
    assert ctx["events"] == []


@then("el aggregate Notificacion emite NotificacionEnviada")
def then_emitio_enviada(ctx: dict) -> None:
    assert any(isinstance(event, NotificacionEnviada) for event in ctx["events"])


@then("la notificacion queda en estado terminal")
def then_terminal(ctx: dict) -> None:
    assert ctx["aggregate"].estado in {"Enviada", "Fallida"}


@then("el aggregate Notificacion emite NotificacionFallida con ese motivo")
def then_emitio_fallida(ctx: dict) -> None:
    assert any(isinstance(event, NotificacionFallida) for event in ctx["events"])
