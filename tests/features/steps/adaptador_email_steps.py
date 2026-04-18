from __future__ import annotations

import asyncio

import httpx
import pytest
from fastapi import FastAPI, Header, HTTPException
from pytest_bdd import scenarios, then, when

from notificaciones.domain.value_objects.contenido_email import ContenidoEmail
from notificaciones.domain.value_objects.destinatario import Destinatario
from notificaciones.infrastructure.email.resend_email_adapter import ResendEmailAdapter

scenarios("../US-4.5.2-adaptador-email.feature")


@pytest.fixture
def ctx() -> dict:
    return {
        "provider_id": None,
        "payload": None,
        "error": None,
    }


def _build_adapter(
    app: FastAPI,
    *,
    api_key: str = "test-api-key",
    from_email: str = "no-reply@ataraxiadive.com",
) -> ResendEmailAdapter:
    transport = httpx.ASGITransport(app=app)

    def client_factory() -> httpx.AsyncClient:
        return httpx.AsyncClient(
            transport=transport,
            base_url="http://testserver",
        )

    return ResendEmailAdapter(
        api_key=api_key,
        from_email=from_email,
        base_url="http://testserver",
        client_factory=client_factory,
    )


@when('se envia un email via el adaptador Resend al destinatario "juan@example.com"')
def when_envio_exitoso(ctx: dict) -> None:
    async def _run() -> None:
        app = FastAPI()

        @app.post("/emails")
        async def create_email(
            payload: dict, authorization: str = Header(default="")
        ) -> dict[str, str]:
            if authorization != "Bearer test-api-key":
                raise HTTPException(status_code=401, detail="unauthorized")
            ctx["payload"] = payload
            return {"id": "provider-123"}

        adapter = _build_adapter(app)
        ctx["provider_id"] = await adapter.enviar(
            Destinatario(email="juan@example.com"),
            ContenidoEmail(asunto="Inscripcion confirmada", cuerpo_texto="ok"),
        )

    asyncio.run(_run())


@then('el adaptador retorna el identificador de proveedor "provider-123"')
def then_provider_id(ctx: dict) -> None:
    assert ctx["provider_id"] == "provider-123"


@then('el proveedor recibe el email con asunto "Inscripcion confirmada"')
def then_payload(ctx: dict) -> None:
    assert ctx["payload"]["subject"] == "Inscripcion confirmada"


@when("el proveedor Resend responde con error al enviar email")
def when_error_proveedor(ctx: dict) -> None:
    async def _run() -> None:
        app = FastAPI()

        @app.post("/emails")
        async def create_email(_payload: dict) -> None:
            raise HTTPException(status_code=502, detail="bad gateway")

        adapter = _build_adapter(app)
        try:
            await adapter.enviar(
                Destinatario(email="juan@example.com"),
                ContenidoEmail(asunto="Inscripcion confirmada", cuerpo_texto="ok"),
            )
        except Exception as exc:  # noqa: BLE001
            ctx["error"] = exc

    asyncio.run(_run())


@then("el adaptador email falla con error tecnico")
def then_error_tecnico(ctx: dict) -> None:
    assert isinstance(ctx["error"], RuntimeError)


@when("se inicializa el adaptador Resend sin api key")
def when_sin_api_key(ctx: dict) -> None:
    adapter = ResendEmailAdapter(api_key="", from_email="no-reply@ataraxiadive.com")
    try:
        adapter._assert_configured()
    except Exception as exc:  # noqa: BLE001
        ctx["error"] = exc


@then("el adaptador rechaza la configuracion requerida")
def then_config_invalida(ctx: dict) -> None:
    assert isinstance(ctx["error"], ValueError)
