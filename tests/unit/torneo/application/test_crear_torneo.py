from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import UUID

import pytest

from torneo.application.commands.crear_torneo import CrearTorneoCommand, CrearTorneoHandler
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.estado_torneo import EstadoTorneo


def _cmd(**overrides: object) -> CrearTorneoCommand:
    defaults: dict[str, object] = dict(
        nombre="Torneo Test",
        descripcion="Descripción",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede_nombre="Piscina Municipal",
        sede_ciudad="Buenos Aires",
        sede_pais="Argentina",
        entidad_nombre="AIDA Argentina",
        entidad_tipo="FEDERACION",
    )
    defaults.update(overrides)
    return CrearTorneoCommand(**defaults)  # type: ignore[arg-type]


@pytest.mark.asyncio
async def test_crear_torneo_retorna_uuid() -> None:
    repo = AsyncMock()
    handler = CrearTorneoHandler(repo)
    torneo_id = await handler.handle(_cmd())
    assert isinstance(torneo_id, UUID)
    repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_crear_torneo_persiste_con_estado_creado() -> None:
    repo = AsyncMock()
    handler = CrearTorneoHandler(repo)
    await handler.handle(_cmd())
    torneo: Torneo = repo.save.call_args[0][0]
    assert torneo.estado == EstadoTorneo.CREADO
    assert torneo.nombre == "Torneo Test"


@pytest.mark.asyncio
async def test_crear_torneo_nombre_vacio_lanza_error() -> None:
    repo = AsyncMock()
    handler = CrearTorneoHandler(repo)
    with pytest.raises(ValueError, match="nombre"):
        await handler.handle(_cmd(nombre=""))
    repo.save.assert_not_awaited()


@pytest.mark.asyncio
async def test_crear_torneo_fechas_invalidas_lanza_error() -> None:
    repo = AsyncMock()
    handler = CrearTorneoHandler(repo)
    with pytest.raises(ValueError, match="fecha_fin"):
        await handler.handle(_cmd(fecha_inicio=date(2026, 6, 5), fecha_fin=date(2026, 6, 1)))
    repo.save.assert_not_awaited()
