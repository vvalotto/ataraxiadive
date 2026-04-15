"""Adaptador de email para desarrollo — loguea en consola, no envía emails reales."""

from __future__ import annotations

import logging
import uuid

from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario

logger = logging.getLogger(__name__)


class LoggingEmailAdapter(EmailPort):
    """Implementación de EmailPort para desarrollo/smoke-test.

    Imprime el contenido del email en el log en lugar de enviarlo.
    Usar cuando RESEND_API_KEY no está configurado.
    """

    async def enviar(
        self,
        destinatario: Destinatario,
        contenido: ContenidoEmail,
    ) -> str:
        provider_id = f"log-{uuid.uuid4()}"
        logger.warning(
            "\n"
            "╔══════════════════════════════════════════════════════════╗\n"
            "║  📧  EMAIL (modo desarrollo — no enviado realmente)      ║\n"
            "╠══════════════════════════════════════════════════════════╣\n"
            "║  Para:    %-47s ║\n"
            "║  Asunto:  %-47s ║\n"
            "╠══════════════════════════════════════════════════════════╣\n"
            "%s"
            "╚══════════════════════════════════════════════════════════╝\n"
            "  provider_id: %s",
            f"{destinatario.nombre} <{destinatario.email}>",
            contenido.asunto[:47],
            "".join(
                f"║  {line:<57}║\n"
                for line in (contenido.cuerpo_texto or contenido.cuerpo_html or "").splitlines()[:15]
            ),
            provider_id,
        )
        return provider_id
