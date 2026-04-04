from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.cancelar_inscripcion import (
    CancelarInscripcionCommand,
    CancelarInscripcionHandler,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import InscripcionNoEncontrada, PlazoCancelacionVencido
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina


def _inscripcion_activa() -> Inscripcion:
    return Inscripcion(
        atleta_id=uuid4(),
        torneo_id=uuid4(),
        disciplinas=frozenset({Disciplina.STA}),
    )


def _handler(inscripcion=None, fecha_inicio=date(2026, 6, 10)):
    repo = AsyncMock()
    repo.find_by_id.return_value = inscripcion
    consulta = AsyncMock()
    consulta.obtener_fecha_inicio.return_value = fecha_inicio
    return CancelarInscripcionHandler(repo, consulta), repo


@pytest.mark.asyncio
async def test_cancelar_exitosamente():
    ins = _inscripcion_activa()
    handler, repo = _handler(inscripcion=ins, fecha_inicio=date(2026, 6, 10))
    cmd = CancelarInscripcionCommand(
        inscripcion_id=ins.inscripcion_id, fecha_actual=date(2026, 6, 9)
    )
    await handler.handle(cmd)
    assert ins.estado == EstadoInscripcion.CANCELADA
    repo.save.assert_called_once_with(ins)


@pytest.mark.asyncio
async def test_inscripcion_no_encontrada():
    handler, _ = _handler(inscripcion=None)
    cmd = CancelarInscripcionCommand(inscripcion_id=uuid4(), fecha_actual=date(2026, 6, 9))
    with pytest.raises(InscripcionNoEncontrada):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_cancelar_el_dia_del_torneo_falla():
    ins = _inscripcion_activa()
    handler, _ = _handler(inscripcion=ins, fecha_inicio=date(2026, 6, 10))
    cmd = CancelarInscripcionCommand(
        inscripcion_id=ins.inscripcion_id, fecha_actual=date(2026, 6, 10)
    )
    with pytest.raises(PlazoCancelacionVencido):
        await handler.handle(cmd)
