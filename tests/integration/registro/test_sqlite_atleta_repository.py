from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from registro.domain.aggregates.atleta import Atleta
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository


def _atleta(**kwargs) -> Atleta:
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
    return Atleta(**defaults)


@pytest.fixture
def repo(tmp_path) -> SQLiteAtletaRepository:
    return SQLiteAtletaRepository(db_path=str(tmp_path / "registro.db"))


class TestSQLiteAtletaRepository:
    async def test_save_y_find_by_id(self, repo: SQLiteAtletaRepository):
        atleta = _atleta()
        await repo.save(atleta)
        result = await repo.find_by_id(atleta.atleta_id)
        assert result is not None
        assert result.atleta_id == atleta.atleta_id
        assert result.nombre == atleta.nombre
        assert result.email == atleta.email
        assert result.brevet is None

    async def test_save_y_find_by_id_con_brevet(self, repo: SQLiteAtletaRepository):
        atleta = _atleta(brevet="AIDA-3")
        await repo.save(atleta)
        result = await repo.find_by_id(atleta.atleta_id)
        assert result is not None
        assert result.brevet == "AIDA-3"

    async def test_find_by_email(self, repo: SQLiteAtletaRepository):
        atleta = _atleta(email="carlos@example.com")
        await repo.save(atleta)
        result = await repo.find_by_email("carlos@example.com")
        assert result is not None
        assert result.atleta_id == atleta.atleta_id

    async def test_find_by_id_no_existente(self, repo: SQLiteAtletaRepository):
        result = await repo.find_by_id(uuid4())
        assert result is None

    async def test_find_by_email_no_existente(self, repo: SQLiteAtletaRepository):
        result = await repo.find_by_email("noexiste@example.com")
        assert result is None

    async def test_upsert_actualiza_datos(self, repo: SQLiteAtletaRepository):
        atleta = _atleta()
        await repo.save(atleta)
        from dataclasses import replace

        actualizado = replace(atleta, nombre="Actualizado")
        await repo.save(actualizado)
        result = await repo.find_by_id(atleta.atleta_id)
        assert result is not None
        assert result.nombre == "Actualizado"
