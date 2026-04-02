"""Tests unitarios del aggregate RankingOverall — US-3.5.1."""

from __future__ import annotations

from uuid import uuid4

from resultados.domain.aggregates.ranking_overall import RankingOverall
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.value_objects.disciplina import Disciplina


def _entry(posicion: int, atleta_id=None) -> EntradaRanking:
    return EntradaRanking(
        posicion=posicion,
        atleta_id=atleta_id or uuid4(),
        rp=None,
        unidad=None,
        tarjeta="Blanca",
        es_dns=False,
        en_podio=posicion <= 3,
    )


def test_calcular_overall_suma_posiciones_y_empates() -> None:
    atleta_a = uuid4()
    atleta_b = uuid4()
    atleta_c = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.STA: [_entry(1, atleta_a), _entry(2, atleta_b), _entry(3, atleta_c)],
            Disciplina.DNF: [_entry(2, atleta_a), _entry(1, atleta_b), _entry(3, atleta_c)],
        },
    )

    by_id = {entry.atleta_id: entry for entry in entries}
    assert by_id[atleta_a].puntaje == 3
    assert by_id[atleta_a].posicion == 1
    assert by_id[atleta_b].puntaje == 3
    assert by_id[atleta_b].posicion == 1
    assert by_id[atleta_c].puntaje == 6
    assert by_id[atleta_c].posicion == 3


def test_calcular_overall_penaliza_ausente_con_ultimo_mas_uno() -> None:
    atleta_a = uuid4()
    atleta_b = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.STA: [_entry(1, atleta_a), _entry(2, atleta_b)],
            Disciplina.DNF: [_entry(1, atleta_b)],
        },
    )

    by_id = {entry.atleta_id: entry for entry in entries}
    assert by_id[atleta_a].detalle == {"STA": 1, "DNF": 2}
    assert by_id[atleta_a].puntaje == 3
    assert by_id[atleta_b].puntaje == 3


def test_calcular_overall_excluye_disciplinas_sin_ranking() -> None:
    atleta_a = uuid4()
    atleta_b = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.STA: [_entry(1, atleta_a), _entry(2, atleta_b)],
            Disciplina.DNF: [],
        },
    )

    assert len(entries) == 2
    assert entries[0].puntaje == 1
    assert entries[1].puntaje == 2


def test_calcular_overall_sin_rankings_devuelve_vacio() -> None:
    ranking = RankingOverall(uuid4())
    assert ranking.calcular(ranking.torneo_id, {}) == []
    assert ranking.pull_events() == []


def test_reconstitute_recupera_estado_desde_evento() -> None:
    torneo_id = uuid4()
    atleta_id = uuid4()
    ranking = RankingOverall(torneo_id)
    ranking.calcular(
        torneo_id,
        {Disciplina.STA: [_entry(1, atleta_id)]},
    )
    event = ranking.pull_events()[0]

    reconstituido = RankingOverall.reconstitute(
        torneo_id,
        [{"event_type": event.event_type, "payload": event.to_payload()}],
    )

    assert len(reconstituido.entries) == 1
    assert reconstituido.entries[0].atleta_id == atleta_id
    assert reconstituido.calculado is True
