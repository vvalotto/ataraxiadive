from datetime import date
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.queries.obtener_atleta import ObtenerAtletaHandler
from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaNoEncontrado
from registro.domain.value_objects.categoria import Categoria


def _atleta(atleta_id=None) -> Atleta:
    return Atleta(
        atleta_id=atleta_id or uuid4(),
        nombre="Ana",
        apellido="García",
        email="ana@example.com",
        fecha_nacimiento=date(1990, 5, 15),
        categoria=Categoria.SENIOR_FEMENINO,
    )


class TestObtenerAtletaHandler:
    async def test_retorna_atleta_existente(self):
        atleta = _atleta()
        repo = AsyncMock()
        repo.find_by_id.return_value = atleta
        handler = ObtenerAtletaHandler(repo)

        result = await handler.handle(atleta.atleta_id)

        assert result == atleta
        repo.find_by_id.assert_awaited_once_with(atleta.atleta_id)

    async def test_lanza_excepcion_si_no_existe(self):
        repo = AsyncMock()
        repo.find_by_id.return_value = None
        handler = ObtenerAtletaHandler(repo)

        with pytest.raises(AtletaNoEncontrado):
            await handler.handle(uuid4())
