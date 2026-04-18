from __future__ import annotations

from typing import Any

import pytest

from notificaciones.application.commands.enviar_notificacion import (
    EnviarNotificacionCommand,
    EnviarNotificacionHandler,
)
from notificaciones.application.commands.solicitar_envio import (
    SolicitarEnvioCommand,
    SolicitarEnvioHandler,
)
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


class FakeNotificacionRepository:
    def __init__(self) -> None:
        self.events_by_stream: dict[str, list[dict[str, Any]]] = {}

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        self.events_by_stream.setdefault(stream_id, []).append(
            {
                "event_type": event_type,
                "payload": payload,
                "version": len(self.events_by_stream.get(stream_id, [])) + 1,
                "occurred_at": payload["occurred_at"],
            }
        )

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        return self.events_by_stream.get(stream_id, [])

    async def exists_success_by_evento_fuente_id(self, evento_fuente_id: str) -> bool:
        return any(
            event["event_type"] == "NotificacionEnviada"
            and event["payload"]["evento_fuente_id"] == evento_fuente_id
            for events in self.events_by_stream.values()
            for event in events
        )


class FakeEmailPort:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent = 0

    async def enviar(self, destinatario, contenido) -> str | None:
        self.sent += 1
        if self.fail:
            raise RuntimeError("proveedor_no_disponible")
        return "provider-123"


async def _crear_solicitada(repo: FakeNotificacionRepository):
    handler = SolicitarEnvioHandler(repo)
    return await handler.handle(
        SolicitarEnvioCommand(
            evento_fuente_id="evt-reg-001",
            destinatario=Destinatario(email="garcia@apnea.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        )
    )


@pytest.mark.asyncio
async def test_enviar_notificacion_registra_envio_exitoso() -> None:
    repo = FakeNotificacionRepository()
    notificacion_id = await _crear_solicitada(repo)
    assert notificacion_id is not None

    email = FakeEmailPort()
    await EnviarNotificacionHandler(repo, email).handle(
        EnviarNotificacionCommand(notificacion_id=notificacion_id)
    )

    events = next(iter(repo.events_by_stream.values()))
    assert email.sent == 1
    assert events[-1]["event_type"] == "NotificacionEnviada"
    assert events[-1]["payload"]["proveedor_id"] == "provider-123"


@pytest.mark.asyncio
async def test_enviar_notificacion_registra_fallo_tecnico() -> None:
    repo = FakeNotificacionRepository()
    notificacion_id = await _crear_solicitada(repo)
    assert notificacion_id is not None

    email = FakeEmailPort(fail=True)
    await EnviarNotificacionHandler(repo, email).handle(
        EnviarNotificacionCommand(notificacion_id=notificacion_id)
    )

    events = next(iter(repo.events_by_stream.values()))
    assert email.sent == 1
    assert events[-1]["event_type"] == "NotificacionFallida"
    assert "proveedor_no_disponible" in events[-1]["payload"]["motivo"]
