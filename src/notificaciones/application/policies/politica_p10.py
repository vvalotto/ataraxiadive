from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Protocol

from notificaciones.application.commands.enviar_notificacion import (
    EnviarNotificacionCommand,
    EnviarNotificacionHandler,
)
from notificaciones.application.commands.solicitar_envio import (
    SolicitarEnvioCommand,
    SolicitarEnvioHandler,
)
from notificaciones.application.policies._helpers import registrar_fallo_sin_email
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


@dataclass(frozen=True)
class InscripcionConfirmada:
    id: str
    atleta_id: str
    atleta_email: str | None
    atleta_nombre: str
    torneo_nombre: str
    torneo_fecha: date | str
    torneo_sede: str
    disciplinas: tuple[str, ...]


class InscripcionConfirmadaTemplatePort(Protocol):
    def render(self, evento: InscripcionConfirmada) -> ContenidoEmail: ...


class PoliticaP10Handler:
    def __init__(
        self,
        *,
        repository: NotificacionRepository,
        solicitar_envio_handler: SolicitarEnvioHandler,
        enviar_notificacion_handler: EnviarNotificacionHandler,
        template: InscripcionConfirmadaTemplatePort,
    ) -> None:
        self._repository = repository
        self._solicitar_envio_handler = solicitar_envio_handler
        self._enviar_notificacion_handler = enviar_notificacion_handler
        self._template = template

    async def handle(self, evento: InscripcionConfirmada) -> None:
        if not evento.atleta_email or not evento.atleta_email.strip():
            await registrar_fallo_sin_email(evento.id, self._repository)
            return

        contenido = self._template.render(evento)
        notificacion_id = await self._solicitar_envio_handler.handle(
            SolicitarEnvioCommand(
                evento_fuente_id=evento.id,
                destinatario=Destinatario(
                    email=evento.atleta_email,
                    nombre=evento.atleta_nombre,
                ),
                contenido=contenido,
            )
        )
        if notificacion_id is None:
            return

        await self._enviar_notificacion_handler.handle(
            EnviarNotificacionCommand(notificacion_id=notificacion_id)
        )
