from __future__ import annotations

from uuid import uuid4

import aiosqlite
import pytest
import pytest_asyncio

from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.domain.value_objects.disciplina import Disciplina


@pytest_asyncio.fixture
async def repo(tmp_path):
    db = str(tmp_path / "registro.db")
    return SQLiteInscripcionRepository(db_path=db)


def _inscripcion(atleta_id=None, torneo_id=None) -> Inscripcion:
    return Inscripcion(
        atleta_id=atleta_id or uuid4(),
        torneo_id=torneo_id or uuid4(),
        disciplinas=frozenset({Disciplina.STA, Disciplina.DNF}),
    )


@pytest.mark.asyncio
async def test_save_and_find_by_id(repo):
    ins = _inscripcion()
    await repo.save(ins)
    found = await repo.find_by_id(ins.inscripcion_id)
    assert found is not None
    assert found.inscripcion_id == ins.inscripcion_id
    assert found.atleta_id == ins.atleta_id
    assert found.estado == EstadoInscripcion.ACTIVA


@pytest.mark.asyncio
async def test_find_by_id_no_existe(repo):
    result = await repo.find_by_id(uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_find_by_atleta_y_torneo(repo):
    atleta_id = uuid4()
    torneo_id = uuid4()
    ins = _inscripcion(atleta_id=atleta_id, torneo_id=torneo_id)
    await repo.save(ins)
    found = await repo.find_by_atleta_y_torneo(atleta_id, torneo_id)
    assert found is not None
    assert found.inscripcion_id == ins.inscripcion_id


@pytest.mark.asyncio
async def test_find_by_atleta_y_torneo_no_existe(repo):
    result = await repo.find_by_atleta_y_torneo(uuid4(), uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_find_by_torneo(repo):
    torneo_id = uuid4()
    ins1 = _inscripcion(torneo_id=torneo_id)
    ins2 = _inscripcion(torneo_id=torneo_id)
    ins3 = _inscripcion()  # otro torneo
    await repo.save(ins1)
    await repo.save(ins2)
    await repo.save(ins3)
    result = await repo.find_by_torneo(torneo_id)
    assert len(result) == 2
    ids = {i.inscripcion_id for i in result}
    assert ins1.inscripcion_id in ids
    assert ins2.inscripcion_id in ids


@pytest.mark.asyncio
async def test_save_actualiza_estado(repo):
    ins = _inscripcion()
    await repo.save(ins)
    ins.estado = EstadoInscripcion.CANCELADA
    await repo.save(ins)
    found = await repo.find_by_id(ins.inscripcion_id)
    assert found.estado == EstadoInscripcion.CANCELADA


@pytest.mark.asyncio
async def test_disciplinas_persisten_correctamente(repo):
    ins = _inscripcion()
    await repo.save(ins)
    found = await repo.find_by_id(ins.inscripcion_id)
    assert found.disciplinas == frozenset({Disciplina.STA, Disciplina.DNF})


@pytest.mark.asyncio
async def test_adjuntos_persisten_correctamente(repo):
    ins = _inscripcion()
    ins.adjuntar_apto_medico("data/adjuntos/ins/apto_medico.pdf")
    ins.adjuntar_constancia_pago("data/adjuntos/ins/constancia_pago.pdf")

    await repo.save(ins)

    found = await repo.find_by_id(ins.inscripcion_id)
    assert found is not None
    assert found.apto_medico_path == "data/adjuntos/ins/apto_medico.pdf"
    assert found.constancia_pago_path == "data/adjuntos/ins/constancia_pago.pdf"


@pytest.mark.asyncio
async def test_migracion_legacy_sin_adjuntos_usa_none(tmp_path):
    db_path = tmp_path / "legacy_registro.db"
    inscripcion_id = uuid4()
    atleta_id = uuid4()
    torneo_id = uuid4()

    async with aiosqlite.connect(db_path) as conn:
        await conn.execute(
            """
            CREATE TABLE inscripciones (
                inscripcion_id    TEXT PRIMARY KEY,
                atleta_id         TEXT NOT NULL,
                torneo_id         TEXT NOT NULL,
                disciplinas       TEXT NOT NULL,
                ap_por_disciplina TEXT NOT NULL DEFAULT '{}',
                estado            TEXT NOT NULL,
                fecha_inscripcion TEXT NOT NULL
            )
            """
        )
        await conn.execute(
            """
            INSERT INTO inscripciones (
                inscripcion_id,
                atleta_id,
                torneo_id,
                disciplinas,
                ap_por_disciplina,
                estado,
                fecha_inscripcion
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(inscripcion_id),
                str(atleta_id),
                str(torneo_id),
                '["STA"]',
                "{}",
                EstadoInscripcion.ACTIVA.value,
                "2026-05-07T12:00:00",
            ),
        )
        await conn.commit()

    repo = SQLiteInscripcionRepository(db_path=str(db_path))
    found = await repo.find_by_id(inscripcion_id)

    assert found is not None
    assert found.apto_medico_path is None
    assert found.constancia_pago_path is None
