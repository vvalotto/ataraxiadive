from __future__ import annotations

from uuid import UUID

import pytest

from notificaciones.domain.exceptions import ContenidoEmailInvalido, DestinatarioInvalido
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.domain.value_objects.evento_fuente_id import EventoFuenteId
from notificaciones.domain.value_objects.notificacion_id import NotificacionId


def test_destinatario_rechaza_email_invalido() -> None:
    with pytest.raises(DestinatarioInvalido):
        Destinatario(email="no-es-un-email")


def test_contenido_email_rechaza_asunto_vacio() -> None:
    with pytest.raises(ContenidoEmailInvalido):
        ContenidoEmail(asunto=" ", cuerpo_texto="hola")


def test_notificacion_id_acepta_uuid_string() -> None:
    raw = "12345678-1234-5678-1234-567812345678"
    vo = NotificacionId(raw)
    assert vo.value == UUID(raw)


def test_evento_fuente_id_rechaza_vacio() -> None:
    with pytest.raises(ValueError):
        EventoFuenteId(" ")
