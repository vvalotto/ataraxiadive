from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaYaRegistrado
from registro.domain.value_objects.categoria import Categoria


def _cmd(**kwargs) -> RegistrarAtletaCommand:
    defaults = dict(
        atleta_id=uuid4(),
        nombre="Ana",
        apellido="García",
        email="ana@example.com",
        fecha_nacimiento=date(1990, 5, 15),
        categoria=Categoria.SENIOR_FEMENINO,
        brevet=None,
    )
    defaults.update(kwargs)
    return RegistrarAtletaCommand(**defaults)


class TestRegistrarAtletaHandler:
    async def test_happy_path(self):
        repo = AsyncMock()
        repo.find_by_id.return_value = None
        handler = RegistrarAtletaHandler(repo)
        cmd = _cmd()

        atleta_id = await handler.handle(cmd)

        assert atleta_id == cmd.atleta_id
        repo.save.assert_awaited_once()

    async def test_atleta_duplicado_lanza_excepcion(self):
        repo = AsyncMock()
        atleta_id = uuid4()
        repo.find_by_id.return_value = Atleta(
            atleta_id=atleta_id,
            nombre="Ana",
            apellido="García",
            email="ana@example.com",
            fecha_nacimiento=date(1990, 5, 15),
            categoria=Categoria.SENIOR_FEMENINO,
        )
        handler = RegistrarAtletaHandler(repo)
        cmd = _cmd(atleta_id=atleta_id)

        with pytest.raises(AtletaYaRegistrado):
            await handler.handle(cmd)

        repo.save.assert_not_awaited()

    async def test_registra_sin_brevet(self):
        repo = AsyncMock()
        repo.find_by_id.return_value = None
        handler = RegistrarAtletaHandler(repo)
        cmd = _cmd(brevet=None)

        await handler.handle(cmd)

        saved: Atleta = repo.save.call_args[0][0]
        assert saved.brevet is None
