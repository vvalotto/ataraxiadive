"""Value Objects del BC Notificaciones."""

from notificaciones.domain.value_objects.canal_envio import CanalEnvio
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId
from notificaciones.domain.value_objects.notificacion_id import NotificacionId

__all__ = [
    "CanalEnvio",
    "ContenidoEmail",
    "Destinatario",
    "EventoFuenteId",
    "NotificacionId",
]
