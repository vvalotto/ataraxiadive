from __future__ import annotations

from uuid import uuid4

import pytest

from registro.domain.aggregates.juez import Juez
from registro.infrastructure.repositories.sqlite_juez_repository import SQLiteJuezRepository


def _juez(**kwargs) -> Juez:
    defaults = dict(juez_id=uuid4(), email="juez@example.com")
    defaults.update(kwargs)
    return Juez(**defaults)


@pytest.fixture
def repo(tmp_path) -> SQLiteJuezRepository:
    return SQLiteJuezRepository(db_path=str(tmp_path / "registro.db"))


class TestSQLiteJuezRepository:
    async def test_save_y_find_by_id(self, repo: SQLiteJuezRepository) -> None:
        juez = _juez()
        await repo.save(juez)
        result = await repo.find_by_id(juez.juez_id)
        assert result is not None
        assert result.juez_id == juez.juez_id
        assert result.email == juez.email
        assert result.numero_licencia is None
        assert result.federacion is None

    async def test_save_con_todos_los_campos(self, repo: SQLiteJuezRepository) -> None:
        juez = _juez(numero_licencia="ARG-001", federacion="AIDA")
        await repo.save(juez)
        result = await repo.find_by_id(juez.juez_id)
        assert result is not None
        assert result.numero_licencia == "ARG-001"
        assert result.federacion == "AIDA"

    async def test_find_by_email(self, repo: SQLiteJuezRepository) -> None:
        juez = _juez(email="otro@example.com")
        await repo.save(juez)
        result = await repo.find_by_email("otro@example.com")
        assert result is not None
        assert result.juez_id == juez.juez_id

    async def test_find_by_id_no_existente(self, repo: SQLiteJuezRepository) -> None:
        result = await repo.find_by_id(uuid4())
        assert result is None

    async def test_find_by_email_no_existente(self, repo: SQLiteJuezRepository) -> None:
        result = await repo.find_by_email("noexiste@example.com")
        assert result is None

    async def test_upsert_actualiza_datos(self, repo: SQLiteJuezRepository) -> None:
        juez = _juez()
        await repo.save(juez)
        juez.actualizar(numero_licencia="ARG-042", federacion="CMAS")
        await repo.save(juez)
        result = await repo.find_by_id(juez.juez_id)
        assert result is not None
        assert result.numero_licencia == "ARG-042"
        assert result.federacion == "CMAS"

    async def test_dos_jueces_en_misma_db(self, repo: SQLiteJuezRepository) -> None:
        juez1 = _juez(email="juez1@example.com")
        juez2 = _juez(email="juez2@example.com")
        await repo.save(juez1)
        await repo.save(juez2)
        r1 = await repo.find_by_email("juez1@example.com")
        r2 = await repo.find_by_email("juez2@example.com")
        assert r1 is not None and r1.juez_id == juez1.juez_id
        assert r2 is not None and r2.juez_id == juez2.juez_id
