from __future__ import annotations

from abc import ABC, abstractmethod

from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


class EmailPort(ABC):
    @abstractmethod
    async def enviar(
        self,
        destinatario: Destinatario,
        contenido: ContenidoEmail,
    ) -> str | None: ...
