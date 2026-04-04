from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from torneo.application.queries.obtener_torneo import (
    ListarTorneosHandler,
    ListarTorneosQuery,
    ObtenerTorneoHandler,
    ObtenerTorneoQuery,
)
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import TorneoNoEncontrado
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede


def _torneo() -> Torneo:
    return Torneo(
        nombre="Torneo",
        descripcion="Desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina", "BA", "AR"),
        entidad_organizadora=EntidadOrganizadora("AIDA", "FEDERACION"),
    )


@pytest.mark.asyncio
async def test_obtener_torneo_existente() -> None:
    torneo = _torneo()
    repo = AsyncMock()
    repo.find_by_id.return_value = torneo
    result = await ObtenerTorneoHandler(repo).handle(ObtenerTorneoQuery(torneo_id=torneo.torneo_id))
    assert result is torneo


@pytest.mark.asyncio
async def test_obtener_torneo_no_encontrado() -> None:
    repo = AsyncMock()
    repo.find_by_id.return_value = None
    with pytest.raises(TorneoNoEncontrado):
        await ObtenerTorneoHandler(repo).handle(ObtenerTorneoQuery(torneo_id=uuid4()))


@pytest.mark.asyncio
async def test_listar_torneos_vacio() -> None:
    repo = AsyncMock()
    repo.find_all.return_value = []
    result = await ListarTorneosHandler(repo).handle(ListarTorneosQuery())
    assert result == []


@pytest.mark.asyncio
async def test_listar_torneos_varios() -> None:
    torneos = [_torneo(), _torneo(), _torneo()]
    repo = AsyncMock()
    repo.find_all.return_value = torneos
    result = await ListarTorneosHandler(repo).handle(ListarTorneosQuery())
    assert len(result) == 3
