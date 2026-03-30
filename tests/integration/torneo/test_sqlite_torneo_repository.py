from __future__ import annotations

from datetime import date
from uuid import uuid4

import pytest

from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository


def _torneo(**overrides: object) -> Torneo:
    defaults: dict[str, object] = dict(
        nombre="Torneo Integración",
        descripcion="Descripción de prueba",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina Municipal", "Buenos Aires", "Argentina"),
        entidad_organizadora=EntidadOrganizadora("AIDA Argentina", "FEDERACION"),
    )
    defaults.update(overrides)
    return Torneo(**defaults)  # type: ignore[arg-type]


@pytest.fixture
def repo(tmp_path: object) -> SQLiteTorneoRepository:
    import tempfile
    db = tempfile.mktemp(suffix=".db")
    return SQLiteTorneoRepository(db_path=db)


@pytest.mark.asyncio
async def test_save_y_find_by_id(repo: SQLiteTorneoRepository) -> None:
    torneo = _torneo()
    await repo.save(torneo)
    resultado = await repo.find_by_id(torneo.torneo_id)
    assert resultado is not None
    assert resultado.torneo_id == torneo.torneo_id
    assert resultado.nombre == torneo.nombre
    assert resultado.descripcion == torneo.descripcion
    assert resultado.fecha_inicio == torneo.fecha_inicio
    assert resultado.fecha_fin == torneo.fecha_fin
    assert resultado.sede.ciudad == "Buenos Aires"
    assert resultado.entidad_organizadora.tipo == "FEDERACION"
    assert resultado.estado == EstadoTorneo.CREADO


@pytest.mark.asyncio
async def test_find_by_id_no_existente(repo: SQLiteTorneoRepository) -> None:
    resultado = await repo.find_by_id(uuid4())
    assert resultado is None


@pytest.mark.asyncio
async def test_find_all_vacio(repo: SQLiteTorneoRepository) -> None:
    resultado = await repo.find_all()
    assert resultado == []


@pytest.mark.asyncio
async def test_find_all_varios(repo: SQLiteTorneoRepository) -> None:
    t1, t2, t3 = _torneo(nombre="T1"), _torneo(nombre="T2"), _torneo(nombre="T3")
    for t in (t1, t2, t3):
        await repo.save(t)
    resultado = await repo.find_all()
    assert len(resultado) == 3


@pytest.mark.asyncio
async def test_save_actualiza_estado(repo: SQLiteTorneoRepository) -> None:
    torneo = _torneo()
    await repo.save(torneo)
    torneo.abrir_inscripcion()
    await repo.save(torneo)
    resultado = await repo.find_by_id(torneo.torneo_id)
    assert resultado is not None
    assert resultado.estado == EstadoTorneo.INSCRIPCION_ABIERTA


@pytest.mark.asyncio
async def test_round_trip_completo(repo: SQLiteTorneoRepository) -> None:
    torneo = _torneo()
    await repo.save(torneo)
    loaded = await repo.find_by_id(torneo.torneo_id)
    assert loaded is not None
    assert loaded.sede.nombre == "Piscina Municipal"
    assert loaded.sede.pais == "Argentina"
    assert loaded.entidad_organizadora.nombre == "AIDA Argentina"
