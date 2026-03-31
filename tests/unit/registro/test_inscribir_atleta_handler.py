from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.inscribir_atleta import (
    InscribirAtletaCommand,
    InscribirAtletaHandler,
)
from registro.domain.exceptions import AtletaYaInscripto, DisciplinaNoDisponible, TorneoNoDisponible
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina


def _handler(abierto: bool = True, disciplinas_torneo=None, existente=None):
    if disciplinas_torneo is None:
        disciplinas_torneo = frozenset({Disciplina.STA, Disciplina.DNF})
    repo = AsyncMock()
    repo.find_by_atleta_y_torneo.return_value = existente
    consulta = AsyncMock()
    consulta.esta_abierto_para_inscripcion.return_value = abierto
    consulta.obtener_disciplinas.return_value = disciplinas_torneo
    return InscribirAtletaHandler(repo, consulta), repo


@pytest.mark.asyncio
async def test_inscribir_atleta_exitosamente():
    handler, repo = _handler()
    cmd = InscribirAtletaCommand(
        atleta_id=uuid4(),
        torneo_id=uuid4(),
        disciplinas=frozenset({Disciplina.STA}),
    )
    inscripcion_id = await handler.handle(cmd)
    assert inscripcion_id is not None
    repo.save.assert_called_once()


@pytest.mark.asyncio
async def test_torneo_no_disponible():
    handler, _ = _handler(abierto=False)
    cmd = InscribirAtletaCommand(
        atleta_id=uuid4(), torneo_id=uuid4(), disciplinas=frozenset({Disciplina.STA})
    )
    with pytest.raises(TorneoNoDisponible):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_disciplina_no_disponible():
    handler, _ = _handler(disciplinas_torneo=frozenset({Disciplina.STA}))
    cmd = InscribirAtletaCommand(
        atleta_id=uuid4(), torneo_id=uuid4(), disciplinas=frozenset({Disciplina.DYN})
    )
    with pytest.raises(DisciplinaNoDisponible):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_atleta_ya_inscripto():
    from registro.domain.aggregates.inscripcion import Inscripcion

    existente = Inscripcion(
        atleta_id=uuid4(), torneo_id=uuid4(), disciplinas=frozenset({Disciplina.STA})
    )
    handler, _ = _handler(existente=existente)
    cmd = InscribirAtletaCommand(
        atleta_id=uuid4(), torneo_id=uuid4(), disciplinas=frozenset({Disciplina.STA})
    )
    with pytest.raises(AtletaYaInscripto):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_disciplinas_vacias_lanza_error():
    handler, _ = _handler()
    cmd = InscribirAtletaCommand(atleta_id=uuid4(), torneo_id=uuid4(), disciplinas=frozenset())
    with pytest.raises(ValueError):
        await handler.handle(cmd)


@pytest.mark.asyncio
async def test_inscripcion_guardada_con_estado_activa():
    handler, repo = _handler()
    cmd = InscribirAtletaCommand(
        atleta_id=uuid4(),
        torneo_id=uuid4(),
        disciplinas=frozenset({Disciplina.STA}),
    )
    await handler.handle(cmd)
    inscripcion_guardada = repo.save.call_args[0][0]
    assert inscripcion_guardada.estado == EstadoInscripcion.ACTIVA
