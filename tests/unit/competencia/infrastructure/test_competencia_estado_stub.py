"""Tests unitarios del StubCompetenciaEstadoAdapter — SP1."""

from __future__ import annotations

from uuid import uuid4

import pytest

from competencia.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter


@pytest.fixture
def stub() -> StubCompetenciaEstadoAdapter:
    return StubCompetenciaEstadoAdapter()


@pytest.mark.asyncio
async def test_stub_plazo_siempre_activo(stub: StubCompetenciaEstadoAdapter) -> None:
    """SP1: is_plazo_vencido retorna False (plazo siempre activo)."""
    result = await stub.is_plazo_vencido(uuid4(), Disciplina.STA)
    assert result is False


@pytest.mark.asyncio
async def test_stub_grilla_nunca_confirmada(stub: StubCompetenciaEstadoAdapter) -> None:
    """SP1: is_grilla_confirmada retorna False (grilla nunca confirmada)."""
    result = await stub.is_grilla_confirmada(uuid4(), Disciplina.DNF)
    assert result is False


@pytest.mark.asyncio
async def test_stub_competencia_siempre_en_ejecucion(stub: StubCompetenciaEstadoAdapter) -> None:
    """SP1: is_en_ejecucion retorna True (competencia siempre activa)."""
    result = await stub.is_en_ejecucion(uuid4())
    assert result is True
