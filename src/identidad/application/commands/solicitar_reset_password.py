from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


@dataclass(frozen=True)
class SolicitarResetPasswordCommand:
    email: str


class SolicitarResetPasswordHandler:
    def __init__(
        self,
        repo: UsuarioRepositoryPort,
        token_service: TokenServicePort,
        email_sender: EmailPort,
        frontend_base_url: str,
    ) -> None:
        self._repo = repo
        self._token_service = token_service
        self._email_sender = email_sender
        self._frontend_base_url = frontend_base_url.rstrip("/")

    async def handle(self, cmd: SolicitarResetPasswordCommand) -> None:
        usuario = await self._repo.find_by_email(cmd.email.strip())
        if usuario is None:
            return

        token = self._token_service.generate_reset_token(usuario.email)
        reset_link = f"{self._frontend_base_url}/reset-password?token={quote(token, safe='')}"
        await self._email_sender.enviar(
            Destinatario(email=usuario.email, nombre=f"{usuario.nombre} {usuario.apellido}".strip()),
            ContenidoEmail(
                asunto="Recuperar contraseña de AtaraxiaDive",
                cuerpo_texto=(
                    "Recibimos una solicitud para restablecer tu contraseña.\n"
                    f"Usa este enlace para continuar: {reset_link}\n"
                    "Si no solicitaste este cambio, podes ignorar este mensaje."
                ),
            ),
        )
