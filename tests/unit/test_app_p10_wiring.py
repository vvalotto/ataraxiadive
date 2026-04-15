from __future__ import annotations

from datetime import date
from uuid import UUID, uuid4

import pytest

from app import build_on_inscripcion_confirmada_callback
from notificaciones.application.policies.politica_p10 import InscripcionConfirmada
from registro.domain.aggregates.atleta import Atleta
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.value_objects.categoria import Categoria
from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.sede import Sede


class FakeP10Handler:
    def __init__(self) -> None:
        self.eventos: list[InscripcionConfirmada] = []

    async def handle(self, evento: InscripcionConfirmada) -> None:
        self.eventos.append(evento)


class FakeAtletaRepo:
    def __init__(self, atleta: Atleta | None) -> None:
        self._atleta = atleta

    async def find_by_id(self, _atleta_id: UUID) -> Atleta | None:
        return self._atleta


class FakeTorneoRepo:
    def __init__(self, torneo: Torneo | None) -> None:
        self._torneo = torneo

    async def find_by_id(self, _torneo_id: UUID) -> Torneo | None:
        return self._torneo


def _atleta(atleta_id: UUID) -> Atleta:
    return Atleta(
        atleta_id=atleta_id,
        nombre="Ana",
        apellido="Paz",
        email="ana.paz@ataraxiadive.io",
        fecha_nacimiento=date(1992, 4, 12),
        categoria=Categoria.SENIOR_FEMENINO,
        club="Azul",
    )


def _torneo(torneo_id: UUID) -> Torneo:
    return Torneo(
        torneo_id=torneo_id,
        nombre="Open BA 2026",
        descripcion="Torneo de apnea",
        fecha_inicio=date(2026, 5, 15),
        fecha_fin=date(2026, 5, 16),
        sede=Sede(nombre="Club Nautico", ciudad="Buenos Aires", pais="Argentina"),
        entidad_organizadora=EntidadOrganizadora(nombre="ADA", tipo="FEDERACION"),
    )


def _inscripcion(atleta_id: UUID, torneo_id: UUID) -> Inscripcion:
    return Inscripcion(
        atleta_id=atleta_id,
        torneo_id=torneo_id,
        disciplinas=frozenset({Disciplina.STA, Disciplina.DNF}),
    )


@pytest.mark.asyncio
async def test_callback_enriquece_inscripcion_y_llama_p10() -> None:
    atleta_id = uuid4()
    torneo_id = uuid4()
    p10 = FakeP10Handler()
    inscripcion = _inscripcion(atleta_id, torneo_id)
    callback = build_on_inscripcion_confirmada_callback(
        p10_handler=p10,
        atleta_repo=FakeAtletaRepo(_atleta(atleta_id)),
        torneo_repo=FakeTorneoRepo(_torneo(torneo_id)),
    )

    await callback(inscripcion)

    assert len(p10.eventos) == 1
    evento = p10.eventos[0]
    assert evento.id == str(inscripcion.inscripcion_id)
    assert evento.atleta_id == str(atleta_id)
    assert evento.atleta_email == "ana.paz@ataraxiadive.io"
    assert evento.atleta_nombre == "Ana Paz"
    assert evento.torneo_nombre == "Open BA 2026"
    assert evento.torneo_fecha == date(2026, 5, 15)
    assert evento.torneo_sede == "Club Nautico"
    assert evento.disciplinas == ("DNF", "STA")


@pytest.mark.asyncio
async def test_callback_no_llama_p10_si_atleta_no_existe() -> None:
    torneo_id = uuid4()
    p10 = FakeP10Handler()
    callback = build_on_inscripcion_confirmada_callback(
        p10_handler=p10,
        atleta_repo=FakeAtletaRepo(None),
        torneo_repo=FakeTorneoRepo(_torneo(torneo_id)),
    )

    await callback(_inscripcion(uuid4(), torneo_id))

    assert p10.eventos == []


@pytest.mark.asyncio
async def test_callback_no_llama_p10_si_torneo_no_existe() -> None:
    atleta_id = uuid4()
    p10 = FakeP10Handler()
    callback = build_on_inscripcion_confirmada_callback(
        p10_handler=p10,
        atleta_repo=FakeAtletaRepo(_atleta(atleta_id)),
        torneo_repo=FakeTorneoRepo(None),
    )

    await callback(_inscripcion(atleta_id, uuid4()))

    assert p10.eventos == []
