from __future__ import annotations

import httpx
import pytest
from fastapi import FastAPI, Header, HTTPException

from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.infrastructure.email.resend_email_adapter import ResendEmailAdapter


@pytest.mark.asyncio
async def test_resend_adapter_contrato_http_basico() -> None:
    app = FastAPI()
    received: dict[str, object] = {}

    @app.post("/emails")
    async def create_email(
        payload: dict[str, object],
        authorization: str = Header(default=""),
    ) -> dict[str, str]:
        if authorization != "Bearer test-api-key":
            raise HTTPException(status_code=401, detail="unauthorized")
        received["payload"] = payload
        return {"id": "provider-789"}

    transport = httpx.ASGITransport(app=app)

    def client_factory() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        )

    adapter = ResendEmailAdapter(
        api_key="test-api-key",
        from_email="no-reply@ataraxiadive.com",
        base_url="http://testserver",
        client_factory=client_factory,
    )

    provider_id = await adapter.enviar(
        Destinatario(email="atleta@example.com", nombre="Atleta Test"),
        ContenidoEmail(asunto="Confirmacion", cuerpo_texto="Inscripcion OK"),
    )

    assert provider_id == "provider-789"
    assert received["payload"] == {
        "from": "no-reply@ataraxiadive.com",
        "to": ["atleta@example.com"],
        "subject": "Confirmacion",
        "text": "Inscripcion OK",
    }
