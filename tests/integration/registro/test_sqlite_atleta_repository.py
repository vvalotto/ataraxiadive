from __future__ import annotations

import aiosqlite
from dataclasses import replace
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
        assert result.club is None
        assert result.categoria is None
        assert result.brevet is None
        assert result.dni is None
        assert result.telefono is None

    async def test_save_con_todos_los_campos(self, repo: SQLiteAtletaRepository):
        atleta = _atleta(
            club="Club Apnea Norte",
            categoria=Categoria.SENIOR_FEMENINO,
            brevet="AIDA-3",
            dni="30123456",
            telefono="1155559999",
        )
        await repo.save(atleta)
        result = await repo.find_by_id(atleta.atleta_id)
        assert result is not None
        assert result.club == "Club Apnea Norte"
        assert result.categoria == Categoria.SENIOR_FEMENINO
        assert result.brevet == "AIDA-3"
        assert result.dni == "30123456"
        assert result.telefono == "1155559999"

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
        actualizado = replace(atleta, nombre="Actualizado", dni="99999999")
        await repo.save(actualizado)
        result = await repo.find_by_id(atleta.atleta_id)
        assert result is not None
        assert result.nombre == "Actualizado"
        assert result.dni == "99999999"

    async def test_migracion_columnas_en_db_existente(self, tmp_path):
        db_path = str(tmp_path / "legacy.db")
        # Simular DB anterior sin columnas dni/telefono
        legacy_id = str(uuid4())
        async with aiosqlite.connect(db_path) as conn:
            await conn.execute("""CREATE TABLE atletas (
                    atleta_id TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL, apellido TEXT NOT NULL,
                    email TEXT NOT NULL, fecha_nacimiento TEXT NOT NULL,
                    categoria TEXT NOT NULL, club TEXT NOT NULL, brevet TEXT
                )""")
            await conn.execute(
                "INSERT INTO atletas VALUES (?,?,?,?,?,?,?,?)",
                (
                    legacy_id,
                    "Pedro",
                    "Ruiz",
                    "pedro@test.com",
                    "1985-01-01",
                    "SENIOR_MASCULINO",
                    "Club Norte",
                    None,
                ),
            )
            await conn.commit()

        repo = SQLiteAtletaRepository(db_path=db_path)
        result = await repo.find_by_email("pedro@test.com")
        assert result is not None
        assert result.nombre == "Pedro"
        assert result.club == "Club Norte"
        assert result.dni is None
        assert result.telefono is None
