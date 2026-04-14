from __future__ import annotations

import pytest

from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.events.notificacion_enviada import NotificacionEnviada
from notificaciones.domain.events.notificacion_solicitada import NotificacionSolicitada
from notificaciones.domain.exceptions import EstadoNotificacionInvalido
from notificaciones.domain.value_objects.canal_envio import CanalEnvio
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId


@pytest.mark.asyncio
async def test_solicitud_nueva_emite_notificacion_solicitada() -> None:
    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-001"),
        destinatario=Destinatario(email="juan@example.com", nombre="Juan"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )

    assert aggregate is not None
    events = aggregate.pull_events()
    assert len(events) == 1
    assert isinstance(events[0], NotificacionSolicitada)
    assert aggregate.estado == "Solicitada"


@pytest.mark.asyncio
async def test_idempotencia_no_emite_eventos_si_ya_hubo_exito() -> None:
    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-001"),
        destinatario=Destinatario(email="juan@example.com"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=True,
    )

    assert aggregate is None


@pytest.mark.asyncio
async def test_registrar_envio_exitoso_deja_estado_terminal() -> None:
    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-001"),
        destinatario=Destinatario(email="juan@example.com"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert aggregate is not None
    aggregate.pull_events()

    aggregate.registrar_envio_exitoso("provider-1")
    events = aggregate.pull_events()

    assert len(events) == 1
    assert isinstance(events[0], NotificacionEnviada)
    assert aggregate.estado == "Enviada"

    with pytest.raises(EstadoNotificacionInvalido):
        aggregate.registrar_fallo("late failure")


@pytest.mark.asyncio
async def test_registrar_fallo_deja_estado_terminal() -> None:
    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-002"),
        destinatario=Destinatario(email="ana@example.com"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert aggregate is not None
    aggregate.pull_events()

    aggregate.registrar_fallo("SMTP connection refused")
    assert aggregate.estado == "Fallida"
    assert aggregate.motivo_fallo == "SMTP connection refused"

    with pytest.raises(EstadoNotificacionInvalido):
        aggregate.registrar_envio_exitoso()


@pytest.mark.asyncio
async def test_reconstituye_y_permite_reintento_tras_fallo_previo() -> None:
    aggregate = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-002"),
        destinatario=Destinatario(email="ana@example.com"),
        contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert aggregate is not None
    stored_events = [event.to_payload() for event in aggregate.pull_events()]
    aggregate.registrar_fallo("timeout")
    stored_events.extend(event.to_payload() for event in aggregate.pull_events())

    reconstituted = Notificacion.reconstitute(
        [
            {"event_type": "NotificacionSolicitada", "payload": stored_events[0]},
            {"event_type": "NotificacionFallida", "payload": stored_events[1]},
        ]
    )
    assert reconstituted.estado == "Fallida"

    retry = await Notificacion.solicitar_envio(
        evento_fuente_id=EventoFuenteId("reg-002"),
        destinatario=Destinatario(email="ana@example.com"),
        contenido=ContenidoEmail(asunto="Reintento", cuerpo_texto="ok"),
        canal=CanalEnvio.EMAIL,
        existe_envio_exitoso_previo=False,
    )
    assert retry is not None
    assert retry.estado == "Solicitada"
