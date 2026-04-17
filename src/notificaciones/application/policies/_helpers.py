"""Helpers compartidos para políticas de notificación."""

from __future__ import annotations

from notificaciones.application.commands.solicitar_envio import persistir_eventos_pendientes
from notificaciones.domain.aggregates.notificacion import Notificacion
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId


async def registrar_fallo_sin_email(
    evento_fuente_id: str,
    repository: NotificacionRepository,
) -> None:
    """Registra NotificacionFallida cuando el destinatario no tiene email.

    Idempotente: si ya existe un éxito para el mismo evento_fuente_id, no registra.
    """
    if await repository.exists_success_by_evento_fuente_id(evento_fuente_id):
        return
    aggregate = Notificacion.registrar_fallo_de_solicitud(
        evento_fuente_id=EventoFuenteId(evento_fuente_id),
        motivo="destinatario_sin_email",
    )
    await persistir_eventos_pendientes(repository, aggregate)
