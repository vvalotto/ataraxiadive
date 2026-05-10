"""Step definitions BDD — US-5.6.1: Algoritmo de puntaje FAAS."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from resultados.domain.services.algoritmo_faas import AlgoritmoPuntajeFAAS
from shared.domain.value_objects.disciplina import Disciplina

scenarios("../US-5.6.1-algoritmo-puntaje-faas.feature")


@pytest.fixture
def ctx() -> dict:
    return {
        "atletas": {"Ana": uuid4(), "Luis": uuid4(), "Pedro": uuid4()},
        "resultados": [],
        "disciplina": Disciplina.DNF,
        "puntos": {},
    }


def _mk(
    ctx: dict, nombre: str, rp: Decimal | None, tarjeta: str | None, es_dns: bool = False
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=ctx["atletas"][nombre],
        rp=rp,
        unidad="Metros" if rp is not None else None,
        tarjeta=tarjeta,
        es_dns=es_dns,
    )


# ---------------------------------------------------------------------------
# Given
# ---------------------------------------------------------------------------


@given("atletas identificados por UUIDs conocidos")
def step_atletas(ctx: dict) -> None:
    pass


@given(parsers.parse("una disciplina de tipo distancia {disc}"))
def step_disc_distancia(ctx: dict, disc: str) -> None:
    ctx["disciplina"] = Disciplina(disc)


@given(parsers.parse("una disciplina de tipo tiempo {disc}"))
def step_disc_tiempo(ctx: dict, disc: str) -> None:
    ctx["disciplina"] = Disciplina(disc)


@given(parsers.parse("los resultados son: Ana {ra} metros Blanca, Luis {rl} metros Blanca"))
def step_res_dos_distancia(ctx: dict, ra: str, rl: str) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Ana", Decimal(ra), "Blanca"),
        _mk(ctx, "Luis", Decimal(rl), "Blanca"),
    ]


@given(parsers.parse("los resultados son: Luis {rl} segundos Blanca, Ana {ra} segundos Blanca"))
def step_res_dos_tiempo(ctx: dict, rl: str, ra: str) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Luis", Decimal(rl), "Blanca"),
        _mk(ctx, "Ana", Decimal(ra), "Blanca"),
    ]


@given(parsers.parse("los resultados son: Ana {ra} metros Blanca, Pedro DNS"))
def step_res_ana_pedro_dns(ctx: dict, ra: str) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Ana", Decimal(ra), "Blanca"),
        _mk(ctx, "Pedro", None, None, es_dns=True),
    ]


@given(parsers.parse("los resultados son: Ana {ra} metros Blanca, Luis {rl} metros Roja"))
def step_res_ana_luis_roja(ctx: dict, ra: str, rl: str) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Ana", Decimal(ra), "Blanca"),
        _mk(ctx, "Luis", Decimal(rl), "Roja"),
    ]


@given(parsers.parse("los resultados son: Ana {sa} segundos Blanca, Luis {sl} segundos Blanca"))
def step_res_tiempo_iguales(ctx: dict, sa: str, sl: str) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Ana", Decimal(sa), "Blanca"),
        _mk(ctx, "Luis", Decimal(sl), "Blanca"),
    ]


@given("los resultados son: Ana DNS, Luis Roja")
def step_res_todos_invalidos(ctx: dict) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Ana", None, None, es_dns=True),
        _mk(ctx, "Luis", Decimal("60"), "Roja"),
    ]


@given("no hay resultados")
def step_sin_resultados(ctx: dict) -> None:
    ctx["resultados"] = []


@given(
    parsers.parse(
        "los resultados son: Ana {ra} metros Blanca, Luis {rl} metros Blanca, Pedro {rp2} metros Blanca"
    )
)
def step_res_tres(ctx: dict, ra: str, rl: str, rp2: str) -> None:
    ctx["resultados"] = [
        _mk(ctx, "Ana", Decimal(ra), "Blanca"),
        _mk(ctx, "Luis", Decimal(rl), "Blanca"),
        _mk(ctx, "Pedro", Decimal(rp2), "Blanca"),
    ]


# ---------------------------------------------------------------------------
# When
# ---------------------------------------------------------------------------


@when("se calcula el puntaje FAAS")
def step_calcular(ctx: dict) -> None:
    ctx["puntos"] = AlgoritmoPuntajeFAAS().calcular(ctx["resultados"], ctx["disciplina"])


# ---------------------------------------------------------------------------
# Then
# ---------------------------------------------------------------------------


@then(parsers.parse("{nombre} recibe {pts} puntos"))
def step_recibe_puntos(ctx: dict, nombre: str, pts: str) -> None:
    atleta_id = ctx["atletas"][nombre]
    obtenido = ctx["puntos"][atleta_id]
    assert obtenido == Decimal(pts), f"{nombre}: esperado {pts}, obtenido {obtenido}"


@then("el resultado es un diccionario vacio")
def step_dict_vacio(ctx: dict) -> None:
    assert ctx["puntos"] == {}
