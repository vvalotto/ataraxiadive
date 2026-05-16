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
        nombre="Ana",
        apellido="García",
        email="ana@example.com",
        fecha_nacimiento=date(1990, 5, 15),
    )
    defaults.update(kwargs)
    return RegistrarAtletaCommand(**defaults)


def _atleta_existente(email: str = "ana@example.com") -> Atleta:
    return Atleta(
        atleta_id=uuid4(),
        nombre="Ana",
        apellido="García",
        email=email,
        fecha_nacimiento=date(1990, 5, 15),
    )


class TestRegistrarAtletaHandler:
    async def test_happy_path_genera_atleta_id(self):
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarAtletaHandler(repo)

        atleta_id = await handler.handle(_cmd())

        assert atleta_id is not None
        repo.save.assert_awaited_once()
        saved: Atleta = repo.save.call_args[0][0]
        assert saved.atleta_id == atleta_id

    async def test_email_duplicado_lanza_excepcion(self):
        repo = AsyncMock()
        repo.find_by_email.return_value = _atleta_existente()
        handler = RegistrarAtletaHandler(repo)

        with pytest.raises(AtletaYaRegistrado):
            await handler.handle(_cmd())

        repo.save.assert_not_awaited()

    async def test_registra_sin_club_ni_categoria(self):
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarAtletaHandler(repo)

        await handler.handle(_cmd())

        saved: Atleta = repo.save.call_args[0][0]
        assert saved.club is None
        assert saved.categoria is None

    async def test_registra_con_dni_y_telefono(self):
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarAtletaHandler(repo)

        await handler.handle(_cmd(dni="30123456", telefono="1155559999"))

        saved: Atleta = repo.save.call_args[0][0]
        assert saved.dni == "30123456"
        assert saved.telefono == "1155559999"

    async def test_registra_con_todos_los_campos(self):
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarAtletaHandler(repo)

        await handler.handle(
            _cmd(
                club="Club Apnea BA",
                categoria=Categoria.SENIOR_FEMENINO,
                brevet="AIDA-3",
                dni="28888999",
                telefono="1133334444",
            )
        )

        saved: Atleta = repo.save.call_args[0][0]
        assert saved.club == "Club Apnea BA"
        assert saved.categoria == Categoria.SENIOR_FEMENINO
        assert saved.brevet == "AIDA-3"
