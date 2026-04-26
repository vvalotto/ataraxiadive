"""Step definitions BDD — US-5.6.3: RankingCompetencia con puntos FAAS por categoría."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest
from pytest_bdd import given, parsers, scenarios, then, when

from registro.domain.value_objects.categoria import Categoria
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from resultados.domain.services.algoritmo_faas import AlgoritmoPuntajeFAAS
from shared.domain.value_objects.disciplina import Disciplina

scenarios("../US-5.6.3-ranking-puntos-faas.feature")


# ── Fixture de contexto ───────────────────────────────────────────────────────


@pytest.fixture
def ctx() -> dict:
    return {
        "algoritmo": None,
        "ranking": None,
        "resultados": [],
        "atleta_ids": {},
    }


# ── Background ────────────────────────────────────────────────────────────────


@given("un algoritmo FAAS inyectado en el aggregate")
def step_algoritmo_faas(ctx: dict) -> None:
    ctx["algoritmo"] = AlgoritmoPuntajeFAAS()


# ── Given ─────────────────────────────────────────────────────────────────────


@given(
    "una disciplina DNF con Ana (70m Blanca, SENIOR_FEMENINO) y Luis (56m Blanca, SENIOR_MASCULINO)"
)
def step_ana_y_luis_dnf(ctx: dict) -> None:
    ana_id = uuid4()
    luis_id = uuid4()
    ctx["atleta_ids"]["Ana"] = ana_id
    ctx["atleta_ids"]["Luis"] = luis_id
    ctx["resultados"] = [
        ResultadoFinal(
            atleta_id=ana_id,
            rp=Decimal("70"),
            unidad="Metros",
            tarjeta="Blanca",
            es_dns=False,
            categoria=Categoria.SENIOR_FEMENINO,
        ),
        ResultadoFinal(
            atleta_id=luis_id,
            rp=Decimal("56"),
            unidad="Metros",
            tarjeta="Blanca",
            es_dns=False,
            categoria=Categoria.SENIOR_MASCULINO,
        ),
    ]
    ctx["ranking"] = RankingCompetencia(competencia_id=uuid4(), disciplina=Disciplina.DNF)


@given("atletas en tres categorias con resultados DNF")
def step_atletas_tres_categorias(ctx: dict, datatable: list) -> None:
    _CATS = {
        "SENIOR_MASCULINO": Categoria.SENIOR_MASCULINO,
        "SENIOR_FEMENINO": Categoria.SENIOR_FEMENINO,
        "MASTER_MASCULINO": Categoria.MASTER_MASCULINO,
    }
    resultados = []
    for row in datatable[1:]:
        nombre, cat_str, rp_str, tarjeta = (
            row[0].strip(),
            row[1].strip(),
            row[2].strip(),
            row[3].strip(),
        )
        atleta_id = uuid4()
        ctx["atleta_ids"][nombre] = atleta_id
        resultados.append(
            ResultadoFinal(
                atleta_id=atleta_id,
                rp=Decimal(rp_str),
                unidad="Metros",
                tarjeta=tarjeta,
                es_dns=False,
                categoria=_CATS[cat_str],
            )
        )
    ctx["resultados"] = resultados
    ctx["ranking"] = RankingCompetencia(competencia_id=uuid4(), disciplina=Disciplina.DNF)


@given("Pedro con DNS en DNF categoria SENIOR_MASCULINO")
def step_pedro_dns(ctx: dict) -> None:
    pedro_id = uuid4()
    ctx["atleta_ids"]["Pedro"] = pedro_id
    ctx["resultados"].append(
        ResultadoFinal(
            atleta_id=pedro_id,
            rp=None,
            unidad=None,
            tarjeta=None,
            es_dns=True,
            categoria=Categoria.SENIOR_MASCULINO,
        )
    )
    if ctx.get("ranking") is None:
        ctx["ranking"] = RankingCompetencia(competencia_id=uuid4(), disciplina=Disciplina.DNF)


@given("Luis con RP 60m Blanca en DNF categoria SENIOR_MASCULINO")
def step_luis_60m(ctx: dict) -> None:
    luis_id = uuid4()
    ctx["atleta_ids"]["Luis"] = luis_id
    ctx["resultados"].append(
        ResultadoFinal(
            atleta_id=luis_id,
            rp=Decimal("60"),
            unidad="Metros",
            tarjeta="Blanca",
            es_dns=False,
            categoria=Categoria.SENIOR_MASCULINO,
        )
    )


@given("un ranking DNF calculado con algoritmo FAAS para Ana (70m) y Luis (56m)")
def step_ranking_calculado_para_reconstitucion(ctx: dict) -> None:
    ana_id = uuid4()
    luis_id = uuid4()
    ctx["atleta_ids"]["Ana"] = ana_id
    ctx["atleta_ids"]["Luis"] = luis_id
    cid = uuid4()
    ctx["competencia_id"] = cid
    resultados = [
        ResultadoFinal(
            atleta_id=ana_id,
            rp=Decimal("70"),
            unidad="Metros",
            tarjeta="Blanca",
            es_dns=False,
            categoria=Categoria.SENIOR_FEMENINO,
        ),
        ResultadoFinal(
            atleta_id=luis_id,
            rp=Decimal("56"),
            unidad="Metros",
            tarjeta="Blanca",
            es_dns=False,
            categoria=Categoria.SENIOR_MASCULINO,
        ),
    ]
    ranking = RankingCompetencia(competencia_id=cid, disciplina=Disciplina.DNF)
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())
    ctx["ranking"] = ranking


# ── When ──────────────────────────────────────────────────────────────────────


@when("se calcula el ranking con algoritmo FAAS")
def step_calcular_con_faas(ctx: dict) -> None:
    ctx["ranking"].calcular(ctx["resultados"], ctx["algoritmo"])


@when("se serializa y reconstituye el aggregate desde el event store")
def step_serializar_y_reconstituir(ctx: dict) -> None:
    ranking = ctx["ranking"]
    events = ranking.pull_events()
    raw = [{"event_type": e.event_type, "payload": e.to_payload()} for e in events]
    ctx["ranking_original_puntos"] = {e.atleta_id: e.puntos for e in ranking.entries}
    ctx["ranking_reconstituido"] = RankingCompetencia.reconstitute(
        competencia_id=ctx["competencia_id"],
        disciplina=Disciplina.DNF,
        events=raw,
    )


# ── Then ──────────────────────────────────────────────────────────────────────


@then("Ana tiene puntos = 100.00 en su EntradaRanking")
def step_ana_100(ctx: dict) -> None:
    ana_id = ctx["atleta_ids"]["Ana"]
    entry = next(e for e in ctx["ranking"].entries if e.atleta_id == ana_id)
    assert entry.puntos == Decimal("100.00"), f"Expected 100.00, got {entry.puntos}"


@then("Luis tiene puntos = 80.00 en su EntradaRanking")
def step_luis_80(ctx: dict) -> None:
    luis_id = ctx["atleta_ids"]["Luis"]
    entry = next(e for e in ctx["ranking"].entries if e.atleta_id == luis_id)
    assert entry.puntos == Decimal("80.00"), f"Expected 80.00, got {entry.puntos}"


@then("la posicion 1 en SENIOR_MASCULINO corresponde al atleta con mas puntos")
def step_pos1_senior_masculino(ctx: dict) -> None:
    sm = [e for e in ctx["ranking"].entries if e.categoria == Categoria.SENIOR_MASCULINO]
    pos1 = [e for e in sm if e.posicion == 1]
    assert len(pos1) >= 1
    max_puntos = max(e.puntos for e in sm if e.en_podio or e.posicion == 1)
    assert all(e.puntos == max_puntos for e in pos1)


@then("la posicion 1 en SENIOR_FEMENINO corresponde al atleta con mas puntos")
def step_pos1_senior_femenino(ctx: dict) -> None:
    sf = [e for e in ctx["ranking"].entries if e.categoria == Categoria.SENIOR_FEMENINO]
    pos1 = [e for e in sf if e.posicion == 1]
    assert len(pos1) >= 1
    max_puntos = max(e.puntos for e in sf if e.en_podio or e.posicion == 1)
    assert all(e.puntos == max_puntos for e in pos1)


@then("Pedro tiene puntos = 0.00")
def step_pedro_puntos_cero(ctx: dict) -> None:
    pedro_id = ctx["atleta_ids"]["Pedro"]
    entry = next(e for e in ctx["ranking"].entries if e.atleta_id == pedro_id)
    assert entry.puntos == Decimal("0.00"), f"Expected 0.00, got {entry.puntos}"


@then("Pedro no tiene posicion de podio")
def step_pedro_sin_podio(ctx: dict) -> None:
    pedro_id = ctx["atleta_ids"]["Pedro"]
    entry = next(e for e in ctx["ranking"].entries if e.atleta_id == pedro_id)
    assert entry.en_podio is False


@then("el aggregate reconstituido tiene los mismos puntos que el original")
def step_puntos_iguales_tras_reconstitucion(ctx: dict) -> None:
    reconstituido = ctx["ranking_reconstituido"]
    original_puntos = ctx["ranking_original_puntos"]
    for entry in reconstituido.entries:
        assert entry.puntos == original_puntos[entry.atleta_id], (
            f"Atleta {entry.atleta_id}: original={original_puntos[entry.atleta_id]}, "
            f"reconstituido={entry.puntos}"
        )


@then("la reconstitucion no require recalcular")
def step_reconstitucion_sin_recalculo(ctx: dict) -> None:
    reconstituido = ctx["ranking_reconstituido"]
    assert reconstituido.calculado is True
    assert len(reconstituido.pull_events()) == 0
