"""Tests unitarios del endpoint POST /competencia/{id}/generar-grilla."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import FastAPI
from fastapi.testclient import TestClient

from competencia.api.router import get_generar_grilla_handler, router
from competencia.application.commands.generar_grilla import GenerarGrillaCommand
from identidad.api.dependencies import get_current_user


COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000005114")


class SpyGenerarGrillaHandler:
    """Handler espía para verificar traducción HTTP -> command."""

    def __init__(self) -> None:
        self.command: GenerarGrillaCommand | None = None

    async def handle(self, command: GenerarGrillaCommand) -> None:
        self.command = command


def test_post_generar_grilla_traduce_body_a_command() -> None:
    handler = SpyGenerarGrillaHandler()
    app = FastAPI()
    app.include_router(router)
    app.dependency_overrides[get_generar_grilla_handler] = lambda: handler
    app.dependency_overrides[get_current_user] = lambda: {
        "sub": "organizador-01",
        "email": "org@ataraxia.com",
        "rol": "ORGANIZADOR",
    }
    client = TestClient(app)

    response = client.post(
        f"/competencia/{COMPETENCIA_ID}/generar-grilla",
        json={
            "disciplina": "DNF",
            "ot_inicio": "2026-04-20T09:00:00Z",
            "andariveles": 2,
        },
    )

    assert response.status_code == 204
    assert handler.command is not None
    assert handler.command.competencia_id == COMPETENCIA_ID
    assert handler.command.disciplina.value == "DNF"
    assert handler.command.ot_inicio == datetime(2026, 4, 20, 9, 0, tzinfo=timezone.utc)
    assert handler.command.andariveles == 2
