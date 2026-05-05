from __future__ import annotations

from typing import Any

import pytest

from notificaciones.application.commands.enviar_notificacion import EnviarNotificacionHandler
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p10 import (
    InscripcionConfirmada,
    PoliticaP10Handler,
)
from notificaciones.infrastructure.templates.inscripcion_confirmada_template import (
    InscripcionConfirmadaTemplate,
)


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

    def event_types(self) -> list[str]:
        return [
            event["event_type"] for events in self.events_by_stream.values() for event in events
        ]


class FakeEmailPort:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.sent = 0
        self.last_subject: str | None = None
        self.last_body: str | None = None

    async def enviar(self, destinatario, contenido) -> str | None:
        self.sent += 1
        self.last_subject = contenido.asunto
        self.last_body = contenido.cuerpo_texto
        if self.fail:
            raise RuntimeError("proveedor_no_disponible")
        return "provider-123"


def _evento(email: str | None = "garcia@apnea.com") -> InscripcionConfirmada:
    return InscripcionConfirmada(
        id="evt-reg-001",
        atleta_id="ath-123",
        atleta_email=email,
        atleta_nombre="Martin Garcia",
        torneo_nombre="Open BA 2026",
        torneo_fecha="2026-05-15",
        torneo_sede="Club Nautico",
        disciplinas=("DNF", "STA"),
    )


def _handler(repo: FakeNotificacionRepository, email: FakeEmailPort) -> PoliticaP10Handler:
    return PoliticaP10Handler(
        repository=repo,
        solicitar_envio_handler=SolicitarEnvioHandler(repo),
        enviar_notificacion_handler=EnviarNotificacionHandler(repo, email),
        template=InscripcionConfirmadaTemplate(),
    )


@pytest.mark.asyncio
async def test_p10_envia_email_de_confirmacion() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento())

    assert email.sent == 1
    assert repo.event_types() == ["NotificacionSolicitada", "NotificacionEnviada"]
    assert email.last_subject == "Inscripcion confirmada - Open BA 2026"
    assert email.last_body is not None
    assert "Open BA 2026" in email.last_body
    assert "DNF, STA" in email.last_body


@pytest.mark.asyncio
async def test_p10_es_idempotente_si_evento_ya_fue_enviado() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()
    handler = _handler(repo, email)

    await handler.handle(_evento())
    await handler.handle(_evento())

    assert email.sent == 1
    assert repo.event_types() == ["NotificacionSolicitada", "NotificacionEnviada"]


@pytest.mark.asyncio
async def test_p10_registra_fallo_si_atleta_no_tiene_email() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort()

    await _handler(repo, email).handle(_evento(email=None))

    assert email.sent == 0
    assert repo.event_types() == ["NotificacionFallida"]
    event = next(iter(repo.events_by_stream.values()))[0]
    assert event["payload"]["motivo"] == "destinatario_sin_email"


@pytest.mark.asyncio
async def test_p10_no_propaga_fallo_del_proveedor() -> None:
    repo = FakeNotificacionRepository()
    email = FakeEmailPort(fail=True)

    await _handler(repo, email).handle(_evento())

    assert email.sent == 1
    assert repo.event_types() == ["NotificacionSolicitada", "NotificacionFallida"]
