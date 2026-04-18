"""Excepciones de dominio del BC Notificaciones."""

from __future__ import annotations


class NotificacionesDomainError(Exception):
    """Base de errores de dominio de Notificaciones."""


class DestinatarioInvalido(NotificacionesDomainError):
    """El destinatario no cumple el formato esperado."""


class ContenidoEmailInvalido(NotificacionesDomainError):
    """El contenido del email no cumple los invariantes."""


class EstadoNotificacionInvalido(NotificacionesDomainError):
    """La operación no es válida para el estado actual."""
