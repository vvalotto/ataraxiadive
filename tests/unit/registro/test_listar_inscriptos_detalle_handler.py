from datetime import date, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from registro.application.queries.listar_inscriptos_detalle import (
    InscriptoDetalleDto,
    ListarInscriptosDetalleHandler,
)
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina


def _atleta(atleta_id=None) -> Atleta:
    return Atleta(
        atleta_id=atleta_id or uuid4(),
        nombre="Ana",
        apellido="García",
        email="ana@example.com",
        fecha_nacimiento=date(1990, 5, 15),
        categoria=Categoria.SENIOR_FEMENINO,
        club="Club Aqua",
    )


def _inscripcion(
    atleta_id, torneo_id, disciplinas=None, estado=EstadoInscripcion.ACTIVA
) -> Inscripcion:
    insc = Inscripcion(
        atleta_id=atleta_id,
        torneo_id=torneo_id,
        disciplinas=frozenset(disciplinas or [Disciplina.DNF]),
        fecha_inscripcion=datetime(2026, 1, 1),
    )
    insc.estado = estado
    return insc


class TestListarInscriptosDetalleHandler:
    async def test_retorna_inscripciones_activas_con_datos_atleta(self):
        torneo_id = uuid4()
        atleta = _atleta()
        insc = _inscripcion(atleta.atleta_id, torneo_id, [Disciplina.DNF, Disciplina.STA])

        inscripcion_repo = AsyncMock()
        inscripcion_repo.find_by_torneo.return_value = [insc]
        atleta_repo = AsyncMock()
        atleta_repo.find_by_id.return_value = atleta

        handler = ListarInscriptosDetalleHandler(inscripcion_repo, atleta_repo)
        result = await handler.handle(torneo_id)

        assert len(result) == 1
        dto = result[0]
        assert isinstance(dto, InscriptoDetalleDto)
        assert dto.atleta_id == atleta.atleta_id
        assert dto.nombre == "Ana"
        assert dto.apellido == "García"
        assert dto.categoria == Categoria.SENIOR_FEMENINO.value
        assert dto.club == "Club Aqua"
        assert set(dto.disciplinas) == {"DNF", "STA"}
        assert dto.estado == "ACTIVA"

    async def test_excluye_inscripciones_canceladas(self):
        torneo_id = uuid4()
        atleta = _atleta()
        insc_activa = _inscripcion(atleta.atleta_id, torneo_id)
        insc_cancelada = _inscripcion(uuid4(), torneo_id, estado=EstadoInscripcion.CANCELADA)

        inscripcion_repo = AsyncMock()
        inscripcion_repo.find_by_torneo.return_value = [insc_activa, insc_cancelada]
        atleta_repo = AsyncMock()
        atleta_repo.find_by_id.return_value = atleta

        handler = ListarInscriptosDetalleHandler(inscripcion_repo, atleta_repo)
        result = await handler.handle(torneo_id)

        assert len(result) == 1
        assert result[0].atleta_id == atleta.atleta_id

    async def test_torneo_sin_inscripciones_activas_devuelve_lista_vacia(self):
        torneo_id = uuid4()
        inscripcion_repo = AsyncMock()
        inscripcion_repo.find_by_torneo.return_value = []
        atleta_repo = AsyncMock()

        handler = ListarInscriptosDetalleHandler(inscripcion_repo, atleta_repo)
        result = await handler.handle(torneo_id)

        assert result == []
        atleta_repo.find_by_id.assert_not_awaited()

    async def test_atleta_no_encontrado_es_omitido(self):
        torneo_id = uuid4()
        insc = _inscripcion(uuid4(), torneo_id)

        inscripcion_repo = AsyncMock()
        inscripcion_repo.find_by_torneo.return_value = [insc]
        atleta_repo = AsyncMock()
        atleta_repo.find_by_id.return_value = None

        handler = ListarInscriptosDetalleHandler(inscripcion_repo, atleta_repo)
        result = await handler.handle(torneo_id)

        assert result == []

    async def test_multiples_inscripciones_activas(self):
        torneo_id = uuid4()
        atleta1 = _atleta()
        atleta2 = _atleta()
        insc1 = _inscripcion(atleta1.atleta_id, torneo_id, [Disciplina.DNF])
        insc2 = _inscripcion(atleta2.atleta_id, torneo_id, [Disciplina.DYN])

        inscripcion_repo = AsyncMock()
        inscripcion_repo.find_by_torneo.return_value = [insc1, insc2]
        atleta_repo = AsyncMock()
        atleta_repo.find_by_id.side_effect = lambda aid: (
            atleta1 if aid == atleta1.atleta_id else atleta2
        )

        handler = ListarInscriptosDetalleHandler(inscripcion_repo, atleta_repo)
        result = await handler.handle(torneo_id)

        assert len(result) == 2
        ids = {r.atleta_id for r in result}
        assert atleta1.atleta_id in ids
        assert atleta2.atleta_id in ids
