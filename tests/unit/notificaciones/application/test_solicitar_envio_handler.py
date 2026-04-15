from __future__ import annotations

from typing import Any

import pytest

from notificaciones.application.commands.solicitar_envio import (
    SolicitarEnvioCommand,
    SolicitarEnvioHandler,
)
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


class FakeNotificacionRepository:
    def __init__(self) -> None:
        self.events: list[tuple[str, str, dict[str, Any]]] = []
        self.success_evento_fuente_ids: set[str] = set()

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        self.events.append((stream_id, event_type, payload))

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        return []

    async def exists_success_by_evento_fuente_id(self, evento_fuente_id: str) -> bool:
        return evento_fuente_id in self.success_evento_fuente_ids


@pytest.mark.asyncio
async def test_solicitar_envio_crea_notificacion_si_no_hay_exito_previo() -> None:
    repo = FakeNotificacionRepository()
    handler = SolicitarEnvioHandler(repo)

    notificacion_id = await handler.handle(
        SolicitarEnvioCommand(
            evento_fuente_id="evt-reg-001",
            destinatario=Destinatario(email="garcia@apnea.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        )
    )

    assert notificacion_id is not None
    assert len(repo.events) == 1
    assert repo.events[0][1] == "NotificacionSolicitada"
    assert repo.events[0][2]["evento_fuente_id"] == "evt-reg-001"


@pytest.mark.asyncio
async def test_solicitar_envio_no_persiste_si_existe_envio_exitoso_previo() -> None:
    repo = FakeNotificacionRepository()
    repo.success_evento_fuente_ids.add("evt-reg-001")
    handler = SolicitarEnvioHandler(repo)

    notificacion_id = await handler.handle(
        SolicitarEnvioCommand(
            evento_fuente_id="evt-reg-001",
            destinatario=Destinatario(email="garcia@apnea.com"),
            contenido=ContenidoEmail(asunto="Inscripcion", cuerpo_texto="ok"),
        )
    )

    assert notificacion_id is None
    assert repo.events == []
