from __future__ import annotations

from uuid import uuid4

import pytest

from registro.domain.aggregates.organizador import Organizador
from registro.infrastructure.repositories.sqlite_organizador_repository import (
    SQLiteOrganizadorRepository,
)


def _org(**kwargs) -> Organizador:
    defaults = dict(organizador_id=uuid4(), email="org@example.com")
    defaults.update(kwargs)
    return Organizador(**defaults)


@pytest.fixture
def repo(tmp_path) -> SQLiteOrganizadorRepository:
    return SQLiteOrganizadorRepository(db_path=str(tmp_path / "registro.db"))


class TestSQLiteOrganizadorRepository:
    async def test_save_y_find_by_id(self, repo: SQLiteOrganizadorRepository) -> None:
        org = _org()
        await repo.save(org)
        result = await repo.find_by_id(org.organizador_id)
        assert result is not None
        assert result.organizador_id == org.organizador_id
        assert result.email == org.email
        assert result.nombre_organizacion is None

    async def test_save_con_nombre(self, repo: SQLiteOrganizadorRepository) -> None:
        org = _org(nombre_organizacion="Club Apnea BA")
        await repo.save(org)
        result = await repo.find_by_id(org.organizador_id)
        assert result is not None
        assert result.nombre_organizacion == "Club Apnea BA"

    async def test_find_by_email(self, repo: SQLiteOrganizadorRepository) -> None:
        org = _org(email="otro@example.com")
        await repo.save(org)
        result = await repo.find_by_email("otro@example.com")
        assert result is not None
        assert result.organizador_id == org.organizador_id

    async def test_find_by_id_no_existente(self, repo: SQLiteOrganizadorRepository) -> None:
        result = await repo.find_by_id(uuid4())
        assert result is None

    async def test_find_by_email_no_existente(self, repo: SQLiteOrganizadorRepository) -> None:
        result = await repo.find_by_email("noexiste@example.com")
        assert result is None

    async def test_upsert_actualiza_nombre(self, repo: SQLiteOrganizadorRepository) -> None:
        org = _org()
        await repo.save(org)
        org.actualizar(nombre_organizacion="Federación Sur")
        await repo.save(org)
        result = await repo.find_by_id(org.organizador_id)
        assert result is not None
        assert result.nombre_organizacion == "Federación Sur"

    async def test_upsert_limpia_nombre_a_null(self, repo: SQLiteOrganizadorRepository) -> None:
        org = _org(nombre_organizacion="Club Viejo")
        await repo.save(org)
        org.actualizar(nombre_organizacion=None)
        await repo.save(org)
        result = await repo.find_by_id(org.organizador_id)
        assert result is not None
        assert result.nombre_organizacion is None

    async def test_dos_organizadores_en_misma_db(self, repo: SQLiteOrganizadorRepository) -> None:
        org1 = _org(email="org1@example.com")
        org2 = _org(email="org2@example.com")
        await repo.save(org1)
        await repo.save(org2)
        r1 = await repo.find_by_email("org1@example.com")
        r2 = await repo.find_by_email("org2@example.com")
        assert r1 is not None and r1.organizador_id == org1.organizador_id
        assert r2 is not None and r2.organizador_id == org2.organizador_id
