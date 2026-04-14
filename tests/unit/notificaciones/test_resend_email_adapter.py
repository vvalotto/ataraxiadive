from __future__ import annotations

import httpx
import pytest

from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.infrastructure.email.resend_email_adapter import ResendEmailAdapter


def _build_adapter(transport: httpx.BaseTransport) -> ResendEmailAdapter:
    def client_factory() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=transport,
            base_url="https://email.test",
        )

    return ResendEmailAdapter(
        api_key="secret-key",
        from_email="no-reply@ataraxiadive.com",
        base_url="https://email.test",
        client_factory=client_factory,
    )


@pytest.mark.asyncio
async def test_enviar_email_mapea_payload_y_devuelve_provider_id() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["auth"] = request.headers["Authorization"]
        captured["payload"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"id": "email_123"})

    adapter = _build_adapter(httpx.MockTransport(handler))

    provider_id = await adapter.enviar(
        Destinatario(email="juan@example.com", nombre="Juan"),
        ContenidoEmail(
            asunto="Inscripcion confirmada",
            cuerpo_texto="Tu inscripcion fue confirmada",
            cuerpo_html="<p>Tu inscripcion fue confirmada</p>",
        ),
    )

    assert provider_id == "email_123"
    assert captured["path"] == "/emails"
    assert captured["auth"] == "Bearer secret-key"
    assert '"to":["juan@example.com"]' in str(captured["payload"])
    assert '"html":"<p>Tu inscripcion fue confirmada</p>"' in str(captured["payload"])


@pytest.mark.asyncio
async def test_enviar_email_omite_html_si_no_esta_presente() -> None:
    captured: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["payload"] = request.read().decode("utf-8")
        return httpx.Response(200, json={"id": "email_456"})

    adapter = _build_adapter(httpx.MockTransport(handler))

    provider_id = await adapter.enviar(
        Destinatario(email="ana@example.com"),
        ContenidoEmail(asunto="Aviso", cuerpo_texto="Solo texto"),
    )

    assert provider_id == "email_456"
    assert '"html"' not in captured["payload"]


@pytest.mark.asyncio
async def test_enviar_email_falla_si_el_proveedor_retorna_error() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"message": "upstream failure"})

    adapter = _build_adapter(httpx.MockTransport(handler))

    with pytest.raises(RuntimeError, match="No se pudo enviar el email mediante Resend"):
        await adapter.enviar(
            Destinatario(email="ana@example.com"),
            ContenidoEmail(asunto="Aviso", cuerpo_texto="Solo texto"),
        )


@pytest.mark.asyncio
async def test_enviar_email_falla_si_falta_provider_id() -> None:
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "queued"})

    adapter = _build_adapter(httpx.MockTransport(handler))

    with pytest.raises(RuntimeError, match="sin identificador de envio"):
        await adapter.enviar(
            Destinatario(email="ana@example.com"),
            ContenidoEmail(asunto="Aviso", cuerpo_texto="Solo texto"),
        )


def test_enviar_email_requiere_configuracion_minima() -> None:
    adapter = ResendEmailAdapter(api_key="", from_email="")

    with pytest.raises(ValueError, match="RESEND_API_KEY es obligatorio"):
        adapter._assert_configured()
