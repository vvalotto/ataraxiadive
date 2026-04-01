"""Tests unitarios de ObtenerAndarivelesActivosHandler — US-2.3.1."""

from __future__ import annotations

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from competencia.application.queries.obtener_andariveles_activos import (
    ObtenerAndarivelesActivosHandler,
    ObtenerAndarivelesActivosQuery,
)
from competencia.domain.ports.andariveles_activos_port import AndarivelesActivosData
from competencia.domain.value_objects.disciplina import Disciplina

OT = datetime(2026, 3, 22, 10, 30, 0)


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def competencia_id() -> Any:
    return uuid4()


@pytest.fixture
def atleta_a_id() -> Any:
    return uuid4()


@pytest.fixture
def perf_a_id() -> Any:
    return uuid4()


# ── Tests ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_handler_delega_al_port(competencia_id: Any) -> None:
    """ObtenerAndarivelesActivosHandler delega correctamente al port."""
    port = AsyncMock()
    port.get_andariveles_activos.return_value = []
    handler = ObtenerAndarivelesActivosHandler(port)

    query = ObtenerAndarivelesActivosQuery(
        competencia_id=competencia_id,
        disciplina=Disciplina.STA,
        andariveles=2,
    )
    result = await handler.handle(query)

    port.get_andariveles_activos.assert_called_once_with(
        competencia_id=competencia_id,
        disciplina=Disciplina.STA,
        andariveles=2,
    )
    assert result == []


@pytest.mark.asyncio
async def test_handler_retorna_datos_del_port(
    competencia_id: Any, atleta_a_id: Any, perf_a_id: Any
) -> None:
    """El handler retorna exactamente lo que devuelve el port."""
    datos = [
        AndarivelesActivosData(
            numero=1,
            ocupado=True,
            atleta_id=atleta_a_id,
            performance_id=perf_a_id,
            ot_programado=OT,
        ),
        AndarivelesActivosData(
            numero=2,
            ocupado=False,
            atleta_id=None,
            performance_id=None,
            ot_programado=None,
        ),
    ]
    port = AsyncMock()
    port.get_andariveles_activos.return_value = datos
    handler = ObtenerAndarivelesActivosHandler(port)

    query = ObtenerAndarivelesActivosQuery(
        competencia_id=competencia_id,
        disciplina=Disciplina.STA,
        andariveles=2,
    )
    result = await handler.handle(query)

    assert len(result) == 2
    assert result[0].numero == 1
    assert result[0].ocupado is True
    assert result[0].atleta_id == atleta_a_id
    assert result[1].numero == 2
    assert result[1].ocupado is False
