from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from identidad.domain.value_objects.rol import Rol
from registro.domain.exceptions import AtletaYaRegistrado, JuezYaRegistrado, OrganizadorYaRegistrado
from registro.infrastructure.perfil_registro_adapter import PerfilRegistroAdapter


def _make_adapter(atleta_repo=None, juez_repo=None, organizador_repo=None) -> PerfilRegistroAdapter:
    atleta_repo = atleta_repo or MagicMock()
    juez_repo = juez_repo or MagicMock()
    organizador_repo = organizador_repo or MagicMock()
    return PerfilRegistroAdapter(atleta_repo, juez_repo, organizador_repo)


@pytest.mark.asyncio
async def test_crear_perfiles_atleta_crea_atleta() -> None:
    atleta_repo = MagicMock()
    atleta_repo.find_by_email = AsyncMock(return_value=None)
    atleta_repo.save = AsyncMock()
    adapter = _make_adapter(atleta_repo=atleta_repo)

    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Ana",
        apellido="Lopez",
        email="ana@test.com",
        roles=[Rol.ATLETA],
    )

    atleta_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_crear_perfiles_juez_crea_juez() -> None:
    juez_repo = MagicMock()
    juez_repo.find_by_email = AsyncMock(return_value=None)
    juez_repo.save = AsyncMock()
    adapter = _make_adapter(juez_repo=juez_repo)

    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Juan",
        apellido="Perez",
        email="juez@test.com",
        roles=[Rol.JUEZ],
        numero_licencia="AIDA-123",
        federacion="AIDA",
    )

    juez_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_crear_perfiles_organizador_crea_organizador() -> None:
    org_repo = MagicMock()
    org_repo.find_by_email = AsyncMock(return_value=None)
    org_repo.save = AsyncMock()
    adapter = _make_adapter(organizador_repo=org_repo)

    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Club",
        apellido="Org",
        email="org@test.com",
        roles=[Rol.ORGANIZADOR],
        nombre_organizacion="Club Apnea",
    )

    org_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_crear_perfiles_multi_rol_crea_todos() -> None:
    atleta_repo = MagicMock()
    atleta_repo.find_by_email = AsyncMock(return_value=None)
    atleta_repo.save = AsyncMock()
    juez_repo = MagicMock()
    juez_repo.find_by_email = AsyncMock(return_value=None)
    juez_repo.save = AsyncMock()
    org_repo = MagicMock()
    org_repo.find_by_email = AsyncMock(return_value=None)
    org_repo.save = AsyncMock()
    adapter = _make_adapter(atleta_repo, juez_repo, org_repo)

    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Multi",
        apellido="Rol",
        email="multi@test.com",
        roles=[Rol.ATLETA, Rol.JUEZ, Rol.ORGANIZADOR],
    )

    atleta_repo.save.assert_awaited_once()
    juez_repo.save.assert_awaited_once()
    org_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_idempotencia_atleta_ya_registrado_no_lanza() -> None:
    atleta_repo = MagicMock()
    atleta_repo.find_by_email = AsyncMock(side_effect=AtletaYaRegistrado("ya existe"))
    adapter = _make_adapter(atleta_repo=atleta_repo)

    # No debe lanzar excepción
    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Ana",
        apellido="Lopez",
        email="ana@test.com",
        roles=[Rol.ATLETA],
    )


@pytest.mark.asyncio
async def test_idempotencia_juez_ya_registrado_no_lanza() -> None:
    juez_repo = MagicMock()
    juez_repo.find_by_email = AsyncMock(side_effect=JuezYaRegistrado("ya existe"))
    adapter = _make_adapter(juez_repo=juez_repo)

    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Juan",
        apellido="Perez",
        email="juez@test.com",
        roles=[Rol.JUEZ],
    )
