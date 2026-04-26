"""Tests de integración: persistencia de tipo_reglamento en SQLite [US-5.6.2]."""

from __future__ import annotations

from datetime import date

import pytest

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede
from torneo.domain.value_objects.tipo_reglamento import TipoReglamento
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


def _torneo(**overrides: object) -> Torneo:
    defaults: dict[str, object] = dict(
        nombre="Torneo Integración",
        descripcion="desc",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 2),
        sede=Sede("Piscina", "Buenos Aires", "AR"),
        entidad_organizadora=EntidadOrganizadora("Club", "Club"),
    )
    defaults.update(overrides)
    return Torneo(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def repo(tmp_path: object) -> SQLiteTorneoRepository:
    import tempfile
    db = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    return SQLiteTorneoRepository(db_path=db.name)


@pytest.mark.asyncio
async def test_persiste_y_recupera_tipo_reglamento_faas(repo: SQLiteTorneoRepository) -> None:
    torneo = _torneo(tipo_reglamento=TipoReglamento.FAAS)
    await repo.save(torneo)
    recuperado = await repo.find_by_id(torneo.torneo_id)
    assert recuperado is not None
    assert recuperado.tipo_reglamento == TipoReglamento.FAAS


@pytest.mark.asyncio
async def test_persiste_y_recupera_tipo_reglamento_cmas(repo: SQLiteTorneoRepository) -> None:
    torneo = _torneo(tipo_reglamento=TipoReglamento.CMAS)
    await repo.save(torneo)
    recuperado = await repo.find_by_id(torneo.torneo_id)
    assert recuperado is not None
    assert recuperado.tipo_reglamento == TipoReglamento.CMAS


@pytest.mark.asyncio
async def test_default_faas_sin_campo_explicito(repo: SQLiteTorneoRepository) -> None:
    torneo = _torneo()
    assert torneo.tipo_reglamento == TipoReglamento.FAAS
    await repo.save(torneo)
    recuperado = await repo.find_by_id(torneo.torneo_id)
    assert recuperado is not None
    assert recuperado.tipo_reglamento == TipoReglamento.FAAS


@pytest.mark.asyncio
async def test_find_all_incluye_tipo_reglamento(repo: SQLiteTorneoRepository) -> None:
    t1 = _torneo(nombre="T1", tipo_reglamento=TipoReglamento.FAAS)
    t2 = _torneo(nombre="T2", tipo_reglamento=TipoReglamento.AIDA)
    await repo.save(t1)
    await repo.save(t2)
    todos = await repo.find_all()
    reglamentos = {t.nombre: t.tipo_reglamento for t in todos}
    assert reglamentos["T1"] == TipoReglamento.FAAS
    assert reglamentos["T2"] == TipoReglamento.AIDA
