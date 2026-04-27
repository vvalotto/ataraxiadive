"""Step definitions BDD — US-5.6.4: RankingOverall con puntos acumulados."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest
from pytest_bdd import given, scenarios, then, when

from registro.domain.value_objects.categoria import Categoria
from resultados.domain.aggregates.ranking_overall import RankingOverall
from resultados.domain.exceptions import DisciplinasNoFinalizadas
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.value_objects.disciplina import Disciplina

scenarios("../US-5.6.4-ranking-overall-puntos.feature")


# ── Fixture de contexto ───────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict:
    return {
        "ranking": None,
        "rankings": {},
        "entries": [],
        "error": None,
        "atleta_ids": {},
    }


# ── Helpers ───────────────────────────────────────────────────────────────────


def _entry(
    atleta_id,
    categoria: Categoria,
    puntos: str,
    tarjeta: str = "Blanca",
    es_dns: bool = False,
) -> EntradaRanking:
    return EntradaRanking(
        posicion=1,
        atleta_id=atleta_id,
        categoria=categoria,
        rp=None,
        unidad=None,
        tarjeta=None if es_dns else tarjeta,
        es_dns=es_dns,
        en_podio=True,
        puntos=Decimal(puntos),
    )


# ── Background ────────────────────────────────────────────────────────────────


@given("un torneo con dos disciplinas DNF y STA")
def step_torneo_dos_disciplinas(ctx: dict) -> None:
    ctx["ranking"] = RankingOverall(uuid4())


# ── Givens ────────────────────────────────────────────────────────────────────


@given("Ana con 100.00 puntos en DNF y 75.00 en STA en SENIOR_FEMENINO")
def step_ana_dnf_sta(ctx: dict) -> None:
    ana_id = ctx["atleta_ids"].setdefault("Ana", uuid4())
    ctx["rankings"].setdefault(Disciplina.DNF, []).append(
        _entry(ana_id, Categoria.SENIOR_FEMENINO, "100.00")
    )
    ctx["rankings"].setdefault(Disciplina.STA, []).append(
        _entry(ana_id, Categoria.SENIOR_FEMENINO, "75.00")
    )


@given("Maria con 75.00 puntos en DNF y 100.00 en STA en SENIOR_FEMENINO")
def step_maria_dnf_sta(ctx: dict) -> None:
    maria_id = ctx["atleta_ids"].setdefault("Maria", uuid4())
    ctx["rankings"].setdefault(Disciplina.DNF, []).append(
        _entry(maria_id, Categoria.SENIOR_FEMENINO, "75.00")
    )
    ctx["rankings"].setdefault(Disciplina.STA, []).append(
        _entry(maria_id, Categoria.SENIOR_FEMENINO, "100.00")
    )


@given("Luis con 80.00 puntos en DNF y DNS en STA en SENIOR_MASCULINO")
def step_luis_dnf_dns_sta(ctx: dict) -> None:
    luis_id = ctx["atleta_ids"].setdefault("Luis", uuid4())
    ctx["rankings"].setdefault(Disciplina.DNF, []).append(
        _entry(luis_id, Categoria.SENIOR_MASCULINO, "80.00")
    )
    ctx["rankings"].setdefault(Disciplina.STA, []).append(
        _entry(luis_id, Categoria.SENIOR_MASCULINO, "0.00", es_dns=True)
    )


@given("solo DNF tiene ranking calculado para el torneo")
def step_solo_dnf_calculado(ctx: dict) -> None:
    atleta_id = uuid4()
    ctx["rankings"][Disciplina.DNF] = [_entry(atleta_id, Categoria.SENIOR_FEMENINO, "100.00")]
    ctx["rankings"][Disciplina.STA] = []


@given("un atleta en SENIOR_MASCULINO con 140.00 puntos totales")
def step_atleta_sm(ctx: dict) -> None:
    sm_id = ctx["atleta_ids"].setdefault("SM", uuid4())
    ctx["rankings"].setdefault(Disciplina.DNF, []).append(
        _entry(sm_id, Categoria.SENIOR_MASCULINO, "80.00")
    )
    ctx["rankings"].setdefault(Disciplina.STA, []).append(
        _entry(sm_id, Categoria.SENIOR_MASCULINO, "60.00")
    )


@given("una atleta en SENIOR_FEMENINO con 175.00 puntos totales")
def step_atleta_sf(ctx: dict) -> None:
    sf_id = ctx["atleta_ids"].setdefault("SF", uuid4())
    ctx["rankings"].setdefault(Disciplina.DNF, []).append(
        _entry(sf_id, Categoria.SENIOR_FEMENINO, "100.00")
    )
    ctx["rankings"].setdefault(Disciplina.STA, []).append(
        _entry(sf_id, Categoria.SENIOR_FEMENINO, "75.00")
    )


# ── Whens ─────────────────────────────────────────────────────────────────────


@when("se calcula el overall")
def step_calcular_overall(ctx: dict) -> None:
    torneo_id = ctx["ranking"].torneo_id
    ctx["entries"] = ctx["ranking"].calcular(torneo_id, ctx["rankings"])


@when("se intenta calcular el overall con DNF y STA")
def step_intentar_calcular_incompleto(ctx: dict) -> None:
    torneo_id = ctx["ranking"].torneo_id
    try:
        ctx["ranking"].calcular(torneo_id, ctx["rankings"])
    except DisciplinasNoFinalizadas as exc:
        ctx["error"] = exc


# ── Thens ─────────────────────────────────────────────────────────────────────


@then("Ana tiene puntos_overall igual a 175.00")
def step_then_ana_175(ctx: dict) -> None:
    ana_id = ctx["atleta_ids"]["Ana"]
    by_id = {e.atleta_id: e for e in ctx["entries"]}
    assert by_id[ana_id].puntos_overall == Decimal("175.00")


@then("Luis tiene puntos_overall igual a 80.00")
def step_then_luis_80(ctx: dict) -> None:
    luis_id = ctx["atleta_ids"]["Luis"]
    by_id = {e.atleta_id: e for e in ctx["entries"]}
    assert by_id[luis_id].puntos_overall == Decimal("80.00")


@then("Ana y Maria aparecen con posicion 1")
def step_then_empate_pos_1(ctx: dict) -> None:
    ana_id = ctx["atleta_ids"]["Ana"]
    maria_id = ctx["atleta_ids"]["Maria"]
    by_id = {e.atleta_id: e for e in ctx["entries"]}
    assert by_id[ana_id].posicion == 1
    assert by_id[maria_id].posicion == 1


@then("el sistema rechaza la operacion con DisciplinasNoFinalizadas")
def step_then_rechaza(ctx: dict) -> None:
    assert isinstance(ctx["error"], DisciplinasNoFinalizadas)


@then("las entradas estan separadas por categoria")
def step_then_separadas_por_categoria(ctx: dict) -> None:
    categorias = {e.categoria for e in ctx["entries"]}
    assert Categoria.SENIOR_MASCULINO in categorias
    assert Categoria.SENIOR_FEMENINO in categorias


@then("el primero de cada categoria tiene la mayor puntuacion")
def step_then_primero_mayor(ctx: dict) -> None:
    sm = [e for e in ctx["entries"] if e.categoria == Categoria.SENIOR_MASCULINO]
    sf = [e for e in ctx["entries"] if e.categoria == Categoria.SENIOR_FEMENINO]
    assert sm[0].posicion == 1
    assert sm[0].puntos_overall == Decimal("140.00")
    assert sf[0].posicion == 1
    assert sf[0].puntos_overall == Decimal("175.00")
