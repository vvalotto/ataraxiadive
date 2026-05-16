from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.actualizar_juez import (
    ActualizarJuezCommand,
    ActualizarJuezHandler,
)
from registro.application.commands.registrar_juez import (
    RegistrarJuezCommand,
    RegistrarJuezHandler,
)
from registro.application.queries.obtener_juez import ObtenerJuezHandler
from registro.domain.aggregates.juez import Juez
from registro.domain.exceptions import JuezNoEncontrado, JuezYaRegistrado


def _juez(**kwargs) -> Juez:
    defaults = dict(juez_id=uuid4(), email="juez@test.com")
    defaults.update(kwargs)
    return Juez(**defaults)


class TestRegistrarJuezHandler:
    @pytest.mark.asyncio
    async def test_happy_path_genera_juez_id(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarJuezHandler(repo)

        juez_id = await handler.handle(RegistrarJuezCommand(email="juez@test.com"))

        assert juez_id is not None
        repo.save.assert_awaited_once()
        saved: Juez = repo.save.call_args[0][0]
        assert saved.juez_id == juez_id
        assert saved.email == "juez@test.com"

    @pytest.mark.asyncio
    async def test_email_duplicado_lanza_excepcion(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = _juez()
        handler = RegistrarJuezHandler(repo)

        with pytest.raises(JuezYaRegistrado):
            await handler.handle(RegistrarJuezCommand(email="juez@test.com"))

        repo.save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_registra_con_datos_completos(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarJuezHandler(repo)

        await handler.handle(
            RegistrarJuezCommand(
                email="juez@test.com",
                numero_licencia="ARG-001",
                federacion="AIDA",
            )
        )

        saved: Juez = repo.save.call_args[0][0]
        assert saved.numero_licencia == "ARG-001"
        assert saved.federacion == "AIDA"

    @pytest.mark.asyncio
    async def test_registra_sin_datos_opcionales(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None
        handler = RegistrarJuezHandler(repo)

        await handler.handle(RegistrarJuezCommand(email="juez@test.com"))

        saved: Juez = repo.save.call_args[0][0]
        assert saved.numero_licencia is None
        assert saved.federacion is None


class TestActualizarJuezHandler:
    @pytest.mark.asyncio
    async def test_actualiza_y_persiste(self) -> None:
        juez = _juez()
        repo = AsyncMock()
        repo.find_by_email.return_value = juez

        result = await ActualizarJuezHandler(repo).handle(
            ActualizarJuezCommand(email="juez@test.com", numero_licencia="ARG-042")
        )

        repo.save.assert_awaited_once_with(juez)
        assert result.numero_licencia == "ARG-042"

    @pytest.mark.asyncio
    async def test_lanza_si_no_encontrado(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        with pytest.raises(JuezNoEncontrado):
            await ActualizarJuezHandler(repo).handle(
                ActualizarJuezCommand(email="noexiste@test.com")
            )

    @pytest.mark.asyncio
    async def test_patch_parcial_no_borra_otros(self) -> None:
        juez = _juez(numero_licencia="ARG-001", federacion="AIDA")
        repo = AsyncMock()
        repo.find_by_email.return_value = juez

        await ActualizarJuezHandler(repo).handle(
            ActualizarJuezCommand(email="juez@test.com", numero_licencia="ARG-999")
        )

        assert juez.federacion == "AIDA"
        assert juez.numero_licencia == "ARG-999"


class TestObtenerJuezHandler:
    @pytest.mark.asyncio
    async def test_retorna_juez_existente(self) -> None:
        juez = _juez(numero_licencia="ARG-001")
        repo = AsyncMock()
        repo.find_by_email.return_value = juez

        result = await ObtenerJuezHandler(repo).handle("juez@test.com")

        assert result.numero_licencia == "ARG-001"

    @pytest.mark.asyncio
    async def test_lanza_si_no_encontrado(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        with pytest.raises(JuezNoEncontrado):
            await ObtenerJuezHandler(repo).handle("noexiste@test.com")
