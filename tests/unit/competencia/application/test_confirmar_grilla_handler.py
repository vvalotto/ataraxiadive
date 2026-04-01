"""Tests unitarios de ConfirmarGrillaHandler — US-2.1.4."""

from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID, uuid4

import pytest

from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.domain.exceptions import GrillaNoGenerada, GrillaYaConfirmada
from competencia.domain.value_objects.disciplina import Disciplina

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000003")
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)


class FakeEventStore:
    """Fake event store para tests unitarios de handlers."""

    def __init__(self, initial_events: list[dict[str, Any]] | None = None) -> None:
        self._events: list[dict[str, Any]] = initial_events or []
        self.appended: list[dict[str, Any]] = []

    async def load(self, stream_id: str) -> list[dict[str, Any]]:  # noqa: ARG002
        return list(self._events)

    async def append(self, stream_id: str, event_type: str, payload: Any) -> None:  # noqa: ARG002
        self.appended.append({"event_type": event_type, "payload": payload})
        self._events.append({"event_type": event_type, "payload": payload})


def _grilla_generada_stream() -> list[dict[str, Any]]:
    """Stream con IntervaloOTConfigurado + GrillaDeSalidaGenerada."""
    pid1 = str(uuid4())
    pid2 = str(uuid4())
    return [
        {
            "event_type": "IntervaloOTConfigurado",
            "payload": {
                "competencia_id": str(COMPETENCIA_ID),
                "disciplina": "STA",
                "intervalo_minutos": 9,
                "configurado_por": "org-01",
                "occurred_at": OT_INICIO.isoformat(),
            },
        },
        {
            "event_type": "GrillaDeSalidaGenerada",
            "payload": {
                "competencia_id": str(COMPETENCIA_ID),
                "disciplina": "STA",
                "ot_inicio": OT_INICIO.isoformat(),
                "generada_en": OT_INICIO.isoformat(),
                "occurred_at": OT_INICIO.isoformat(),
                "performances": [
                    {
                        "performance_id": pid1,
                        "atleta_id": "00000000-0000-0000-0000-000000000011",
                        "posicion": 1,
                        "andarivel": 1,
                        "ot_programado": OT_INICIO.isoformat(),
                    },
                    {
                        "performance_id": pid2,
                        "atleta_id": "00000000-0000-0000-0000-000000000012",
                        "posicion": 2,
                        "andarivel": 1,
                        "ot_programado": "2026-01-01T10:09:00+00:00",
                    },
                ],
            },
        },
    ]


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_handler_persiste_grilla_confirmada() -> None:
    store = FakeEventStore(_grilla_generada_stream())
    handler = ConfirmarGrillaHandler(store)
    await handler.handle(ConfirmarGrillaCommand(COMPETENCIA_ID, Disciplina.STA))
    assert len(store.appended) == 1
    assert store.appended[0]["event_type"] == "GrillaConfirmada"


@pytest.mark.asyncio
async def test_handler_sin_grilla_lanza_grilla_no_generada() -> None:
    store = FakeEventStore([])
    handler = ConfirmarGrillaHandler(store)
    with pytest.raises(GrillaNoGenerada):
        await handler.handle(ConfirmarGrillaCommand(COMPETENCIA_ID, Disciplina.STA))


@pytest.mark.asyncio
async def test_handler_grilla_ya_confirmada_lanza_error() -> None:
    stream = _grilla_generada_stream()
    stream.append(
        {
            "event_type": "GrillaConfirmada",
            "payload": {
                "competencia_id": str(COMPETENCIA_ID),
                "disciplina": "STA",
                "confirmada_en": OT_INICIO.isoformat(),
                "occurred_at": OT_INICIO.isoformat(),
            },
        }
    )
    store = FakeEventStore(stream)
    handler = ConfirmarGrillaHandler(store)
    with pytest.raises(GrillaYaConfirmada):
        await handler.handle(ConfirmarGrillaCommand(COMPETENCIA_ID, Disciplina.STA))
