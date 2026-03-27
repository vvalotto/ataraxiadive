"""Tests unitarios de ObtenerProximasPerformancesHandler — US-1.3.1 / US-2.2.2."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.queries.obtener_proximas_performances import (
    ObtenerProximasPerformancesHandler,
    ObtenerProximasPerformancesQuery,
)
from competencia.domain.value_objects.disciplina import Disciplina


# ── Helpers ────────────────────────────────────────────────────────────────────


def _ts() -> str:
    return datetime.now(timezone.utc).isoformat()


def _ap_stream(
    competencia_id: str, participante_id: str, performance_id: str | None = None
) -> list[dict[str, Any]]:
    pid = performance_id or str(uuid4())
    return [
        {
            "event_type": "APRegistrado",
            "payload": {
                "performance_id": pid,
                "competencia_id": competencia_id,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "valor_ap": "50",
                "unidad": "Metros",
            },
            "version": 1,
            "occurred_at": _ts(),
        }
    ]


def _llamado_stream(
    competencia_id: str, participante_id: str, posicion_grilla: int = 1
) -> list[dict[str, Any]]:
    stream = _ap_stream(competencia_id, participante_id)
    pid = stream[0]["payload"]["performance_id"]
    stream.append(
        {
            "event_type": "AtletaLlamado",
            "payload": {
                "performance_id": pid,
                "participante_id": participante_id,
                "disciplina": "DNF",
                "posicion_grilla": posicion_grilla,
                "ot_programado": _ts(),
                "llamado_en": _ts(),
            },
            "version": 2,
            "occurred_at": _ts(),
        }
    )
    return stream


def _make_query(competencia_id: Any) -> ObtenerProximasPerformancesQuery:
    return ObtenerProximasPerformancesQuery(
        competencia_id=competencia_id, disciplina=Disciplina.DNF
    )


# ── Tests ──────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_retorna_hasta_3_proximas_en_anunciada_ap() -> None:
    """Retorna máximo 3 performances en estado AnunciadaAP."""
    competencia_id = uuid4()
    cid = str(competencia_id)
    # 5 streams: 2 llamadas + 3 en AnunciadaAP
    streams = [_ap_stream(cid, str(uuid4())) for _ in range(3)]
    streams += [_llamado_stream(cid, str(uuid4())) for _ in range(2)]

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    store.load.return_value = []  # grilla vacía → posiciones fallback
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(_make_query(competencia_id))

    assert len(result) == 3


@pytest.mark.asyncio
async def test_retorna_menos_de_3_si_hay_pocas_disponibles() -> None:
    """Retorna menos de 3 si hay pocas performances en AnunciadaAP."""
    competencia_id = uuid4()
    cid = str(competencia_id)
    streams = [_ap_stream(cid, str(uuid4())) for _ in range(2)]

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    store.load.return_value = []
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(_make_query(competencia_id))

    assert len(result) == 2


@pytest.mark.asyncio
async def test_retorna_lista_vacia_si_todas_llamadas() -> None:
    """Retorna lista vacía si todas las performances ya fueron llamadas."""
    competencia_id = uuid4()
    cid = str(competencia_id)
    streams = [_llamado_stream(cid, str(uuid4())) for _ in range(3)]

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = streams
    store.load.return_value = []
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(_make_query(competencia_id))

    assert result == []


@pytest.mark.asyncio
async def test_retorna_lista_vacia_sin_performances() -> None:
    """Retorna lista vacía si no hay performances."""
    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = []
    store.load.return_value = []
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(
        ObtenerProximasPerformancesQuery(competencia_id=uuid4(), disciplina=Disciplina.STA)
    )

    assert result == []


@pytest.mark.asyncio
async def test_ordena_por_posicion_grilla() -> None:
    """US-2.2.2: las próximas performances se ordenan por posicion_grilla de la grilla."""
    competencia_id = uuid4()
    cid = str(competencia_id)
    pid1 = str(uuid4())
    pid2 = str(uuid4())
    pid3 = str(uuid4())
    aid = str(uuid4())
    ot = "2026-03-27T10:00:00+00:00"

    # Streams de performance (DNF): posicion_grilla no está en AtletaLlamado aquí
    # → se obtiene del grilla_map de la Competencia
    perf1 = _ap_stream(cid, str(uuid4()), performance_id=pid1)
    perf2 = _ap_stream(cid, str(uuid4()), performance_id=pid2)
    perf3 = _ap_stream(cid, str(uuid4()), performance_id=pid3)

    # Evento de Competencia con grilla: orden inverso al natural (pid3=1, pid2=2, pid1=3)
    grilla_event = {
        "event_type": "GrillaDeSalidaGenerada",
        "payload": {
            "competencia_id": cid,
            "disciplina": "DNF",
            "ot_inicio": ot,
            "performances": [
                {"performance_id": pid3, "atleta_id": aid, "posicion": 1, "andarivel": 1, "ot_programado": ot},
                {"performance_id": pid2, "atleta_id": aid, "posicion": 2, "andarivel": 2, "ot_programado": ot},
                {"performance_id": pid1, "atleta_id": aid, "posicion": 3, "andarivel": 3, "ot_programado": ot},
            ],
            "generada_en": ot,
            "occurred_at": ot,
        },
    }

    store = AsyncMock()
    store.load_all_streams_with_prefix.return_value = [perf1, perf2, perf3]
    store.load.return_value = [grilla_event]
    handler = ObtenerProximasPerformancesHandler(store)

    result = await handler.handle(
        ObtenerProximasPerformancesQuery(competencia_id=competencia_id, disciplina=Disciplina.DNF)
    )

    assert len(result) == 3
    assert result[0].posicion == 1
    assert result[1].posicion == 2
    assert result[2].posicion == 3
