from __future__ import annotations

from dataclasses import dataclass

from notificaciones.application.commands.solicitar_envio import (
    persistir_eventos_pendientes,
)
from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.domain.value_objects.notificacion_id import NotificacionId


@dataclass(frozen=True)
class EnviarNotificacionCommand:
    notificacion_id: NotificacionId


class EnviarNotificacionHandler:
    def __init__(
        self,
        repository: NotificacionRepository,
        email_port: EmailPort,
    ) -> None:
        self._repository = repository
        self._email_port = email_port

    async def handle(self, command: EnviarNotificacionCommand) -> None:
        stream_id = f"notificacion-{command.notificacion_id}"
        events = await self._repository.load(stream_id)
        aggregate = Notificacion.reconstitute(events)

        if aggregate.destinatario is None or aggregate.contenido is None:
            aggregate.registrar_fallo("notificacion_sin_contenido")
            await persistir_eventos_pendientes(self._repository, aggregate)
            return

        try:
            proveedor_id = await self._email_port.enviar(
                aggregate.destinatario,
                aggregate.contenido,
            )
            aggregate.registrar_envio_exitoso(proveedor_id)
        except Exception as exc:  # noqa: BLE001
            aggregate.registrar_fallo(str(exc) or exc.__class__.__name__)

        await persistir_eventos_pendientes(self._repository, aggregate)
