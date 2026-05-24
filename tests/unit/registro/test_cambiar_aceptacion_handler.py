from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.cambiar_aceptacion_inscripcion import (
    CambiarAceptacionInscripcionCommand,
    CambiarAceptacionInscripcionHandler,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import InscripcionNoEncontrada
from registro.domain.value_objects.estado_aceptacion import EstadoAceptacion
from shared.domain.value_objects.disciplina import Disciplina


def _inscripcion(**kwargs) -> Inscripcion:
    defaults = {
        "atleta_id": uuid4(),
        "torneo_id": uuid4(),
        "disciplinas": frozenset({Disciplina.STA}),
    }
    defaults.update(kwargs)
    return Inscripcion(**defaults)


@pytest.mark.asyncio
async def test_cambiar_aceptacion_rechaza_inscripcion():
    inscripcion = _inscripcion()
    repo = AsyncMock()
    repo.find_by_id.return_value = inscripcion

    handler = CambiarAceptacionInscripcionHandler(repo)
    await handler.handle(
        CambiarAceptacionInscripcionCommand(
            inscripcion_id=inscripcion.inscripcion_id,
            nuevo_estado=EstadoAceptacion.RECHAZADO,
        )
    )

    assert inscripcion.estado_aceptacion == EstadoAceptacion.RECHAZADO
    repo.save.assert_awaited_once_with(inscripcion)


@pytest.mark.asyncio
async def test_cambiar_aceptacion_acepta_inscripcion():
    inscripcion = _inscripcion()
    inscripcion.cambiar_aceptacion(EstadoAceptacion.RECHAZADO)
    repo = AsyncMock()
    repo.find_by_id.return_value = inscripcion

    handler = CambiarAceptacionInscripcionHandler(repo)
    await handler.handle(
        CambiarAceptacionInscripcionCommand(
            inscripcion_id=inscripcion.inscripcion_id,
            nuevo_estado=EstadoAceptacion.ACEPTADO,
        )
    )

    assert inscripcion.estado_aceptacion == EstadoAceptacion.ACEPTADO
    repo.save.assert_awaited_once_with(inscripcion)


@pytest.mark.asyncio
async def test_cambiar_aceptacion_inscripcion_no_encontrada():
    repo = AsyncMock()
    repo.find_by_id.return_value = None

    handler = CambiarAceptacionInscripcionHandler(repo)
    with pytest.raises(InscripcionNoEncontrada):
        await handler.handle(
            CambiarAceptacionInscripcionCommand(
                inscripcion_id=uuid4(),
                nuevo_estado=EstadoAceptacion.RECHAZADO,
            )
        )
