"""Tests unitarios de IniciarCompetenciaHandler — US-2.1.4."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import pytest

from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.domain.exceptions import CompetenciaNoConfirmada
from competencia.domain.value_objects.disciplina import Disciplina

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000004")
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


def _stream_confirmada() -> list[dict[str, Any]]:
    """Stream con grilla generada y confirmada."""
    pid = str(uuid4())
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
                        "performance_id": pid,
                        "atleta_id": "00000000-0000-0000-0000-000000000011",
                        "posicion": 1,
                        "andarivel": 1,
                        "ot_programado": OT_INICIO.isoformat(),
                    }
                ],
            },
        },
        {
            "event_type": "GrillaConfirmada",
            "payload": {
                "competencia_id": str(COMPETENCIA_ID),
                "disciplina": "STA",
                "confirmada_en": OT_INICIO.isoformat(),
                "occurred_at": OT_INICIO.isoformat(),
            },
        },
    ]


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_handler_persiste_competencia_iniciada() -> None:
    store = FakeEventStore(_stream_confirmada())
    handler = IniciarCompetenciaHandler(store)
    await handler.handle(
        IniciarCompetenciaCommand(COMPETENCIA_ID, Disciplina.STA, "juez-01")
    )
    assert len(store.appended) == 1
    assert store.appended[0]["event_type"] == "CompetenciaIniciada"
    assert store.appended[0]["payload"]["juez_id"] == "juez-01"


@pytest.mark.asyncio
async def test_handler_sin_confirmar_lanza_competencia_no_confirmada() -> None:
    store = FakeEventStore([])  # stream vacío → estado Preparacion
    handler = IniciarCompetenciaHandler(store)
    with pytest.raises(CompetenciaNoConfirmada):
        await handler.handle(
            IniciarCompetenciaCommand(COMPETENCIA_ID, Disciplina.STA, "juez-01")
        )


@pytest.mark.asyncio
async def test_handler_con_grilla_generada_pero_no_confirmada_lanza_error() -> None:
    """Grilla generada pero no confirmada → estado Preparacion → falla."""
    stream = _stream_confirmada()[:2]  # solo IntervaloOT + GrillaDeSalidaGenerada
    store = FakeEventStore(stream)
    handler = IniciarCompetenciaHandler(store)
    with pytest.raises(CompetenciaNoConfirmada):
        await handler.handle(
            IniciarCompetenciaCommand(COMPETENCIA_ID, Disciplina.STA, "juez-01")
        )
