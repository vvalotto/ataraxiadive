from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from pytest_bdd import given, when, then, scenario, parsers

from identidad.domain.value_objects.rol import Rol
from registro.domain.aggregates.atleta import Atleta
from registro.domain.exceptions import AtletaYaRegistrado
from registro.infrastructure.perfil_registro_adapter import PerfilRegistroAdapter


def _make_adapter_with_saves():
    atleta_repo = MagicMock()
    atleta_repo.find_by_email = AsyncMock(return_value=None)
    atleta_repo.save = AsyncMock()
    juez_repo = MagicMock()
    juez_repo.find_by_email = AsyncMock(return_value=None)
    juez_repo.save = AsyncMock()
    org_repo = MagicMock()
    org_repo.find_by_email = AsyncMock(return_value=None)
    org_repo.save = AsyncMock()
    adapter = PerfilRegistroAdapter(atleta_repo, juez_repo, org_repo)
    return adapter, atleta_repo, juez_repo, org_repo


@pytest.mark.asyncio
async def test_registro_atleta_crea_perfil_stub():
    adapter, atleta_repo, _, _ = _make_adapter_with_saves()
    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Ana",
        apellido="Lopez",
        email="ana@test.com",
        roles=[Rol.ATLETA],
    )
    atleta_repo.save.assert_awaited_once()
    saved: Atleta = atleta_repo.save.call_args[0][0]
    assert saved.nombre == "Ana"
    assert saved.apellido == "Lopez"
    assert saved.email == "ana@test.com"
    assert saved.fecha_nacimiento is None


@pytest.mark.asyncio
async def test_registro_atleta_juez_crea_ambos_perfiles():
    adapter, atleta_repo, juez_repo, _ = _make_adapter_with_saves()
    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Multi",
        apellido="Rol",
        email="multi@test.com",
        roles=[Rol.ATLETA, Rol.JUEZ],
    )
    atleta_repo.save.assert_awaited_once()
    juez_repo.save.assert_awaited_once()


@pytest.mark.asyncio
async def test_registro_organizador_crea_perfil():
    adapter, _, _, org_repo = _make_adapter_with_saves()
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
async def test_atleta_sin_fecha_nacimiento_es_valido():
    atleta = Atleta(
        atleta_id=uuid4(),
        nombre="Carlos",
        apellido="Test",
        email="c@test.com",
        fecha_nacimiento=None,
    )
    assert atleta.fecha_nacimiento is None


@pytest.mark.asyncio
async def test_atleta_puede_actualizar_fecha_nacimiento():
    atleta = Atleta(
        atleta_id=uuid4(),
        nombre="Carlos",
        apellido="Test",
        email="c@test.com",
        fecha_nacimiento=None,
    )
    atleta.actualizar(fecha_nacimiento=date(1990, 5, 15))
    assert atleta.fecha_nacimiento == date(1990, 5, 15)


@pytest.mark.asyncio
async def test_idempotencia_atleta_ya_registrado():
    atleta_repo = MagicMock()
    atleta_repo.find_by_email = AsyncMock(side_effect=AtletaYaRegistrado("ya existe"))
    juez_repo = MagicMock()
    juez_repo.find_by_email = AsyncMock(return_value=None)
    juez_repo.save = AsyncMock()
    org_repo = MagicMock()
    org_repo.find_by_email = AsyncMock(return_value=None)
    org_repo.save = AsyncMock()
    adapter = PerfilRegistroAdapter(atleta_repo, juez_repo, org_repo)

    # No debe lanzar excepción
    await adapter.crear_perfiles(
        usuario_id=uuid4(),
        nombre="Ana",
        apellido="Lopez",
        email="existing@test.com",
        roles=[Rol.ATLETA],
    )
