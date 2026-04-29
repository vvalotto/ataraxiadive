from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from torneo.application.commands.transicionar_torneo import (
    AbrirInscripcionHandler,
    CancelarTorneoHandler,
    CerrarInscripcionHandler,
    CerrarTorneoHandler,
    IniciarEjecucionHandler,
    IniciarPremiacionHandler,
    TransicionarTorneoCommand,
    VolverAPreparacionHandler,
)
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import TorneoNoEncontrado, TransicionEstadoInvalida
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede


def _torneo(estado: EstadoTorneo = EstadoTorneo.CREADO) -> Torneo:
    t = Torneo(
        nombre="Torneo",
        descripcion="Desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina", "BA", "AR"),
        entidad_organizadora=EntidadOrganizadora("AIDA", "FEDERACION"),
    )
    t.estado = estado
    return t


def _repo(torneo: Torneo | None) -> AsyncMock:
    repo = AsyncMock()
    repo.find_by_id.return_value = torneo
    return repo


@pytest.mark.asyncio
async def test_abrir_inscripcion_ok() -> None:
    torneo = _torneo(EstadoTorneo.CREADO)
    repo = _repo(torneo)
    await AbrirInscripcionHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.INSCRIPCION_ABIERTA
    repo.save.assert_awaited_once_with(torneo)


@pytest.mark.asyncio
async def test_cerrar_inscripcion_ok() -> None:
    torneo = _torneo(EstadoTorneo.INSCRIPCION_ABIERTA)
    repo = _repo(torneo)
    await CerrarInscripcionHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.PREPARACION


@pytest.mark.asyncio
async def test_cerrar_inscripcion_ejecuta_precondicion() -> None:
    torneo = _torneo(EstadoTorneo.INSCRIPCION_ABIERTA)
    repo = _repo(torneo)
    precondition = AsyncMock()

    await CerrarInscripcionHandler(repo, precondition=precondition).handle(
        TransicionarTorneoCommand(torneo.torneo_id)
    )

    precondition.assert_awaited_once_with(torneo.torneo_id)


@pytest.mark.asyncio
async def test_iniciar_ejecucion_ok() -> None:
    torneo = _torneo(EstadoTorneo.PREPARACION)
    repo = _repo(torneo)
    await IniciarEjecucionHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.EJECUCION


@pytest.mark.asyncio
async def test_volver_preparacion_ok() -> None:
    torneo = _torneo(EstadoTorneo.EJECUCION)
    repo = _repo(torneo)
    await VolverAPreparacionHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.PREPARACION


@pytest.mark.asyncio
async def test_iniciar_premiacion_ok() -> None:
    torneo = _torneo(EstadoTorneo.EJECUCION)
    repo = _repo(torneo)
    await IniciarPremiacionHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.PREMIACION


@pytest.mark.asyncio
async def test_cerrar_torneo_ok() -> None:
    torneo = _torneo(EstadoTorneo.PREMIACION)
    repo = _repo(torneo)
    await CerrarTorneoHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.CERRADO


@pytest.mark.asyncio
async def test_cancelar_torneo_ok() -> None:
    torneo = _torneo(EstadoTorneo.INSCRIPCION_ABIERTA)
    repo = _repo(torneo)
    await CancelarTorneoHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    assert torneo.estado == EstadoTorneo.CANCELADO


@pytest.mark.asyncio
async def test_torneo_no_encontrado_lanza_excepcion() -> None:
    repo = _repo(None)
    with pytest.raises(TorneoNoEncontrado):
        await AbrirInscripcionHandler(repo).handle(TransicionarTorneoCommand(uuid4()))


@pytest.mark.asyncio
async def test_transicion_invalida_lanza_excepcion() -> None:
    torneo = _torneo(EstadoTorneo.CREADO)
    repo = _repo(torneo)
    with pytest.raises(TransicionEstadoInvalida):
        await IniciarEjecucionHandler(repo).handle(TransicionarTorneoCommand(torneo.torneo_id))
    repo.save.assert_not_awaited()
