from __future__ import annotations

import inspect
import os
from collections.abc import Awaitable, Callable
from typing import Any

import httpx

from notificaciones.domain.ports.email_port import EmailPort
from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario


class ResendEmailAdapter(EmailPort):
    """Adaptador EmailPort sobre la API HTTP de Resend."""

    def __init__(
        self,
        *,
        api_key: str | None = None,
        from_email: str | None = None,
        base_url: str | None = None,
        timeout: float = 10.0,
        client_factory: (
            Callable[[], Awaitable[httpx.AsyncClient] | httpx.AsyncClient] | None
        ) = None,
    ) -> None:
        self._api_key = api_key or os.getenv("RESEND_API_KEY")
        self._from_email = from_email or os.getenv("NOTIFICACIONES_EMAIL_FROM")
        self._base_url = (
            base_url or os.getenv("RESEND_BASE_URL", "https://api.resend.com")
        ).rstrip("/")
        self._timeout = timeout
        self._client_factory = client_factory

    async def enviar(
        self,
        destinatario: Destinatario,
        contenido: ContenidoEmail,
    ) -> str | None:
        self._assert_configured()

        payload = {
            "from": self._from_email,
            "to": [destinatario.email],
            "subject": contenido.asunto,
            "text": contenido.cuerpo_texto,
        }
        if contenido.cuerpo_html:
            payload["html"] = contenido.cuerpo_html

        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        response = await self._post("/emails", payload, headers)
        try:
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise RuntimeError("No se pudo enviar el email mediante Resend") from exc

        try:
            data = response.json()
        except ValueError as exc:
            raise RuntimeError("Respuesta invalida del proveedor de email") from exc

        provider_id = data.get("id")
        if not isinstance(provider_id, str) or not provider_id.strip():
            raise RuntimeError("Respuesta del proveedor sin identificador de envio")
        return provider_id

    def _assert_configured(self) -> None:
        if not self._api_key or not self._api_key.strip():
            raise ValueError("RESEND_API_KEY es obligatorio")
        if not self._from_email or not self._from_email.strip():
            raise ValueError("NOTIFICACIONES_EMAIL_FROM es obligatorio")

    async def _post(
        self,
        path: str,
        payload: dict[str, Any],
        headers: dict[str, str],
    ) -> httpx.Response:
        if self._client_factory is not None:
            client_or_awaitable = self._client_factory()
            client = (
                await client_or_awaitable
                if inspect.isawaitable(client_or_awaitable)
                else client_or_awaitable
            )
            async with client:
                return await client.post(path, json=payload, headers=headers)

        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            return await client.post(path, json=payload, headers=headers)
