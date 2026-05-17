from __future__ import annotations

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.commands.actualizar_organizador import (
    ActualizarOrganizadorCommand,
    ActualizarOrganizadorHandler,
)
from registro.application.commands.registrar_organizador import (
    RegistrarOrganizadorCommand,
    RegistrarOrganizadorHandler,
)
from registro.application.queries.obtener_organizador import ObtenerOrganizadorHandler
from registro.domain.aggregates.organizador import Organizador
from registro.domain.exceptions import OrganizadorNoEncontrado, OrganizadorYaRegistrado


def _org(**kwargs) -> Organizador:
    defaults = dict(organizador_id=uuid4(), email="org@test.com")
    defaults.update(kwargs)
    return Organizador(**defaults)


class TestRegistrarOrganizadorHandler:
    @pytest.mark.asyncio
    async def test_happy_path_genera_organizador_id(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        organizador_id = await RegistrarOrganizadorHandler(repo).handle(
            RegistrarOrganizadorCommand(email="org@test.com")
        )

        assert organizador_id is not None
        repo.save.assert_awaited_once()
        saved: Organizador = repo.save.call_args[0][0]
        assert saved.organizador_id == organizador_id
        assert saved.email == "org@test.com"
        assert saved.nombre_organizacion is None

    @pytest.mark.asyncio
    async def test_registra_con_nombre(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        await RegistrarOrganizadorHandler(repo).handle(
            RegistrarOrganizadorCommand(
                email="org@test.com",
                nombre_organizacion="Club Apnea BA",
            )
        )

        saved: Organizador = repo.save.call_args[0][0]
        assert saved.nombre_organizacion == "Club Apnea BA"

    @pytest.mark.asyncio
    async def test_email_duplicado_lanza_excepcion(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = _org()

        with pytest.raises(OrganizadorYaRegistrado):
            await RegistrarOrganizadorHandler(repo).handle(
                RegistrarOrganizadorCommand(email="org@test.com")
            )

        repo.save.assert_not_awaited()

    @pytest.mark.asyncio
    async def test_registra_sin_datos_opcionales(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        await RegistrarOrganizadorHandler(repo).handle(
            RegistrarOrganizadorCommand(email="org@test.com")
        )

        saved: Organizador = repo.save.call_args[0][0]
        assert saved.nombre_organizacion is None


class TestActualizarOrganizadorHandler:
    @pytest.mark.asyncio
    async def test_actualiza_nombre_y_persiste(self) -> None:
        org = _org()
        repo = AsyncMock()
        repo.find_by_email.return_value = org

        result = await ActualizarOrganizadorHandler(repo).handle(
            ActualizarOrganizadorCommand(email="org@test.com", nombre_organizacion="Federación Sur")
        )

        repo.save.assert_awaited_once_with(org)
        assert result.nombre_organizacion == "Federación Sur"

    @pytest.mark.asyncio
    async def test_actualiza_nombre_a_null_limpia_campo(self) -> None:
        org = _org(nombre_organizacion="Club Viejo")
        repo = AsyncMock()
        repo.find_by_email.return_value = org

        result = await ActualizarOrganizadorHandler(repo).handle(
            ActualizarOrganizadorCommand(email="org@test.com", nombre_organizacion=None)
        )

        assert result.nombre_organizacion is None
        repo.save.assert_awaited_once_with(org)

    @pytest.mark.asyncio
    async def test_lanza_si_no_encontrado(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        with pytest.raises(OrganizadorNoEncontrado):
            await ActualizarOrganizadorHandler(repo).handle(
                ActualizarOrganizadorCommand(email="noexiste@test.com")
            )


class TestObtenerOrganizadorHandler:
    @pytest.mark.asyncio
    async def test_retorna_organizador_existente(self) -> None:
        org = _org(nombre_organizacion="Club Apnea BA")
        repo = AsyncMock()
        repo.find_by_email.return_value = org

        result = await ObtenerOrganizadorHandler(repo).handle("org@test.com")

        assert result.nombre_organizacion == "Club Apnea BA"

    @pytest.mark.asyncio
    async def test_lanza_si_no_encontrado(self) -> None:
        repo = AsyncMock()
        repo.find_by_email.return_value = None

        with pytest.raises(OrganizadorNoEncontrado):
            await ObtenerOrganizadorHandler(repo).handle("noexiste@test.com")
