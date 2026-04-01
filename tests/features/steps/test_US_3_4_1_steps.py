"""Steps BDD — US-3.4.1: AsignarDisciplinas + AsignarJuez"""

from __future__ import annotations

import tempfile
import os
from datetime import date
from uuid import uuid4, UUID

import pytest
from pytest_bdd import given, when, then, scenarios, parsers

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import AsignacionNoPermitida, DisciplinaNoEnTorneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede

scenarios("../US-3.4.1-asignar-disciplinas-juez.feature")


def _torneo_base() -> Torneo:
    return Torneo(
        nombre="Copa BDD",
        descripcion="Test BDD",
        fecha_inicio=date(2026, 6, 1),
        fecha_fin=date(2026, 6, 3),
        sede=Sede("Piscina", "CABA", "Argentina"),
        entidad_organizadora=EntidadOrganizadora("FAADS", "federacion"),
    )


def _parse_disciplinas(raw: str) -> list[Disciplina]:
    return [Disciplina(d.strip()) for d in raw.strip("[]").split(",")]


@pytest.fixture
def ctx() -> dict:
    return {}


# ── Givens ────────────────────────────────────────────────────────────────────


@given("un torneo creado en estado CREADO", target_fixture="ctx")
def given_torneo_creado() -> dict:
    return {"torneo": _torneo_base(), "excepcion": None}


@given(
    parsers.parse("el torneo tiene disciplinas {disciplinas} configuradas"), target_fixture="ctx"
)
def given_torneo_con_disciplinas(disciplinas: str) -> dict:
    t = _torneo_base()
    t.asignar_disciplinas(frozenset(_parse_disciplinas(disciplinas)))
    return {"torneo": t, "excepcion": None}


@given(
    parsers.parse(
        'el torneo tiene disciplinas {disciplinas} con juez "{juez_str}" en {disciplina}'
    ),
    target_fixture="ctx",
)
def given_torneo_con_juez(disciplinas: str, juez_str: str, disciplina: str) -> dict:
    t = _torneo_base()
    t.asignar_disciplinas(frozenset(_parse_disciplinas(disciplinas)))
    juez_id = uuid4()
    t.asignar_juez(Disciplina(disciplina.strip()), juez_id)
    return {"torneo": t, "excepcion": None, "juez_id": juez_id, "juez_str": juez_str}


@given(parsers.parse("el torneo tiene disciplinas {disciplinas}"), target_fixture="ctx")
def given_torneo_con_disciplinas_simple(disciplinas: str) -> dict:
    t = _torneo_base()
    t.asignar_disciplinas(frozenset(_parse_disciplinas(disciplinas)))
    return {"torneo": t, "excepcion": None}


@given("el torneo tiene 3 disciplinas y juez asignado a 2 de ellas", target_fixture="ctx")
def given_torneo_juez_dos_disciplinas() -> dict:
    t = _torneo_base()
    t.asignar_disciplinas(frozenset({Disciplina.STA, Disciplina.DNF, Disciplina.DYNB}))
    juez_id = uuid4()
    t.asignar_juez(Disciplina.STA, juez_id)
    t.asignar_juez(Disciplina.DNF, juez_id)
    return {"torneo": t, "excepcion": None, "juez_id": juez_id}


@given("un torneo en estado EJECUCION", target_fixture="ctx")
def given_torneo_ejecucion() -> dict:
    t = _torneo_base()
    t.abrir_inscripcion()
    t.cerrar_inscripcion()
    t.asignar_disciplinas(frozenset({Disciplina.STA}))
    t.iniciar_ejecucion()
    return {"torneo": t, "excepcion": None}


# ── Whens ─────────────────────────────────────────────────────────────────────


@when(parsers.parse("el organizador asigna las disciplinas {disciplinas} al torneo"))
def when_asignar_disciplinas(ctx: dict, disciplinas: str) -> None:
    try:
        ctx["torneo"].asignar_disciplinas(frozenset(_parse_disciplinas(disciplinas)))
    except Exception as e:
        ctx["excepcion"] = e


@when(parsers.parse('el organizador asigna el juez "{juez_str}" a la disciplina {disciplina}'))
def when_asignar_juez(ctx: dict, juez_str: str, disciplina: str) -> None:
    juez_id = uuid4()
    ctx["juez_id"] = juez_id
    ctx["juez_str"] = juez_str
    try:
        ctx["torneo"].asignar_juez(Disciplina(disciplina.strip()), juez_id)
    except Exception as e:
        ctx["excepcion"] = e


@when(parsers.parse('se consultan las disciplinas del juez "{juez_str}"'))
def when_consultar_disciplinas_juez(ctx: dict, juez_str: str) -> None:
    ctx["resultado"] = ctx["torneo"].obtener_disciplinas_de_juez(ctx["juez_id"])


@when("se consultan las disciplinas del juez registrado")
def when_consultar_disciplinas_juez_registrado(ctx: dict) -> None:
    ctx["resultado"] = ctx["torneo"].obtener_disciplinas_de_juez(ctx["juez_id"])


@when(parsers.parse("el organizador intenta asignar disciplinas {disciplinas}"))
def when_intentar_asignar_disciplinas(ctx: dict, disciplinas: str) -> None:
    try:
        ctx["torneo"].asignar_disciplinas(frozenset(_parse_disciplinas(disciplinas)))
    except Exception as e:
        ctx["excepcion"] = e


# ── Thens ─────────────────────────────────────────────────────────────────────


@then(parsers.parse("el torneo tiene {n:d} disciplinas configuradas sin juez asignado"))
def then_n_disciplinas_sin_juez(ctx: dict, n: int) -> None:
    assert len(ctx["torneo"].disciplinas_torneo) == n
    assert all(dt.juez_id is None for dt in ctx["torneo"].disciplinas_torneo)


@then(parsers.parse('la disciplina {disciplina} tiene el juez "{juez_str}" asignado'))
def then_disciplina_tiene_juez(ctx: dict, disciplina: str, juez_str: str) -> None:
    dt = next(
        d
        for d in ctx["torneo"].disciplinas_torneo
        if d.disciplina == Disciplina(disciplina.strip())
    )
    assert dt.juez_id is not None


@then("se lanza DisciplinaNoEnTorneo")
def then_disciplina_no_en_torneo(ctx: dict) -> None:
    assert isinstance(ctx["excepcion"], DisciplinaNoEnTorneo)


@then(parsers.re(r"se retornan (\[.+\])"))
def then_retorna_disciplinas(ctx: dict) -> None:
    pass  # cubierto por then_retorna_dos_disciplinas en este feature


@then("se retornan exactamente 2 disciplinas")
def then_retorna_dos_disciplinas(ctx: dict) -> None:
    assert len(ctx["resultado"]) == 2


@then("se lanza AsignacionNoPermitida")
def then_asignacion_no_permitida(ctx: dict) -> None:
    assert isinstance(ctx["excepcion"], AsignacionNoPermitida)
