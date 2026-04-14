"""Puertos del BC Notificaciones."""

from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.ports.notificacion_repository import NotificacionRepository

__all__ = ["EmailPort", "NotificacionRepository"]
