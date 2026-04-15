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
    persistir_eventos_pendientes,
)
from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId


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
            await self._registrar_fallo_sin_email(evento)
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

    async def _registrar_fallo_sin_email(self, evento: InscripcionConfirmada) -> None:
        if await self._repository.exists_success_by_evento_fuente_id(evento.id):
            return
        aggregate = Notificacion.registrar_fallo_de_solicitud(
            evento_fuente_id=EventoFuenteId(evento.id),
            motivo="destinatario_sin_email",
        )
        await persistir_eventos_pendientes(self._repository, aggregate)
