"""Tests unitarios del aggregate RankingOverall — US-5.6.4 (puntos FAAS)."""

from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from registro.domain.value_objects.categoria import Categoria
from resultados.domain.aggregates.ranking_overall import RankingOverall
from resultados.domain.exceptions import DisciplinasNoFinalizadas
from resultados.domain.value_objects.entrada_ranking import EntradaRanking
from shared.domain.value_objects.disciplina import Disciplina


def _entry(
    atleta_id=None,
    categoria: Categoria = Categoria.SENIOR_MASCULINO,
    puntos: str = "0.00",
    tarjeta: str = "Blanca",
    es_dns: bool = False,
) -> EntradaRanking:
    return EntradaRanking(
        posicion=1,
        atleta_id=atleta_id or uuid4(),
        categoria=categoria,
        rp=None,
        unidad=None,
        tarjeta=tarjeta,
        es_dns=es_dns,
        en_podio=True,
        puntos=Decimal(puntos),
    )


# ── INV-5.6.4-01: puntos_overall = Σ puntos_disciplina ───────────────────────


def test_calcular_overall_suma_puntos_faas() -> None:
    atleta_a = uuid4()
    atleta_b = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.DNF: [
                _entry(atleta_a, puntos="100.00"),
                _entry(atleta_b, puntos="80.00"),
            ],
            Disciplina.STA: [
                _entry(atleta_a, puntos="75.00"),
                _entry(atleta_b, puntos="95.00"),
            ],
        },
    )

    by_id = {e.atleta_id: e for e in entries}
    assert by_id[atleta_a].puntos_overall == Decimal("175.00")
    assert by_id[atleta_b].puntos_overall == Decimal("175.00")


def test_calcular_overall_ausente_aporta_cero_puntos() -> None:
    """INV-5.6.4-01: atleta no presente en una disciplina aporta 0 puntos."""
    atleta_a = uuid4()
    atleta_b = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.DNF: [
                _entry(atleta_a, puntos="80.00"),
                _entry(atleta_b, puntos="80.00"),
            ],
            Disciplina.STA: [
                _entry(atleta_b, puntos="60.00"),
            ],
        },
    )

    by_id = {e.atleta_id: e for e in entries}
    assert by_id[atleta_a].puntos_overall == Decimal("80.00")
    assert by_id[atleta_b].puntos_overall == Decimal("140.00")


# ── INV-5.6.4-02: orden DESC por puntos_overall ──────────────────────────────


def test_calcular_overall_ordena_por_puntos_desc() -> None:
    atleta_a = uuid4()
    atleta_b = uuid4()
    atleta_c = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.STA: [
                _entry(atleta_a, puntos="100.00"),
                _entry(atleta_b, puntos="80.00"),
                _entry(atleta_c, puntos="60.00"),
            ],
        },
    )

    by_id = {e.atleta_id: e for e in entries}
    assert by_id[atleta_a].posicion == 1
    assert by_id[atleta_b].posicion == 2
    assert by_id[atleta_c].posicion == 3


# ── INV-5.6.4-03: empate comparte posición ───────────────────────────────────


def test_calcular_overall_empate_comparte_posicion() -> None:
    atleta_a = uuid4()
    atleta_b = uuid4()
    atleta_c = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.DNF: [
                _entry(atleta_a, puntos="100.00"),
                _entry(atleta_b, puntos="80.00"),
            ],
            Disciplina.STA: [
                _entry(atleta_a, puntos="75.00"),
                _entry(atleta_b, puntos="95.00"),
                _entry(atleta_c, puntos="50.00"),
            ],
        },
    )

    by_id = {e.atleta_id: e for e in entries}
    assert by_id[atleta_a].puntos_overall == Decimal("175.00")
    assert by_id[atleta_b].puntos_overall == Decimal("175.00")
    assert by_id[atleta_a].posicion == 1
    assert by_id[atleta_b].posicion == 1
    assert by_id[atleta_c].posicion == 3


# ── INV-5.6.4-04: rechaza si alguna disciplina no está finalizada ─────────────


def test_calcular_overall_rechaza_disciplinas_sin_finalizar() -> None:
    ranking = RankingOverall(uuid4())

    with pytest.raises(DisciplinasNoFinalizadas):
        ranking.calcular(
            ranking.torneo_id,
            {
                Disciplina.DNF: [_entry(puntos="80.00")],
                Disciplina.STA: [],
            },
        )


def test_calcular_overall_sin_disciplinas_no_persiste_evento() -> None:
    ranking = RankingOverall(uuid4())

    result = ranking.calcular(ranking.torneo_id, {})

    assert result == []
    assert ranking.pull_events() == []


# ── INV-5.6.4-05: precisión 2 decimales ──────────────────────────────────────


def test_calcular_overall_precision_dos_decimales() -> None:
    atleta_a = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {Disciplina.STA: [_entry(atleta_a, puntos="75.50")]},
    )

    assert entries[0].puntos_overall == Decimal("75.50")


# ── Agrupación por categoría ──────────────────────────────────────────────────


def test_calcular_overall_segmenta_por_categoria() -> None:
    atleta_sf = uuid4()
    atleta_mm = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.STA: [
                _entry(atleta_sf, Categoria.SENIOR_FEMENINO, "100.00"),
                _entry(atleta_mm, Categoria.MASTER_MASCULINO, "80.00"),
            ],
            Disciplina.DNF: [
                _entry(atleta_sf, Categoria.SENIOR_FEMENINO, "75.00"),
                _entry(atleta_mm, Categoria.MASTER_MASCULINO, "60.00"),
            ],
        },
    )

    senior_f = [e for e in entries if e.categoria == Categoria.SENIOR_FEMENINO]
    master_m = [e for e in entries if e.categoria == Categoria.MASTER_MASCULINO]

    assert len(senior_f) == 1
    assert senior_f[0].posicion == 1
    assert senior_f[0].puntos_overall == Decimal("175.00")
    assert len(master_m) == 1
    assert master_m[0].posicion == 1
    assert master_m[0].puntos_overall == Decimal("140.00")


# ── Detalle por disciplina ────────────────────────────────────────────────────


def test_calcular_overall_detalle_contiene_puntos_por_disciplina() -> None:
    atleta_a = uuid4()
    ranking = RankingOverall(uuid4())

    entries = ranking.calcular(
        ranking.torneo_id,
        {
            Disciplina.DNF: [_entry(atleta_a, puntos="100.00")],
            Disciplina.STA: [_entry(atleta_a, puntos="75.00")],
        },
    )

    assert entries[0].detalle == {
        "DNF": Decimal("100.00"),
        "STA": Decimal("75.00"),
    }


# ── Reconstitución ────────────────────────────────────────────────────────────


def test_reconstitute_recupera_estado_desde_evento() -> None:
    torneo_id = uuid4()
    atleta_id = uuid4()
    ranking = RankingOverall(torneo_id)
    ranking.calcular(
        torneo_id,
        {Disciplina.STA: [_entry(atleta_id, puntos="100.00")]},
    )
    event = ranking.pull_events()[0]

    reconstituido = RankingOverall.reconstitute(
        torneo_id,
        [{"event_type": event.event_type, "payload": event.to_payload()}],
    )

    assert len(reconstituido.entries) == 1
    assert reconstituido.entries[0].atleta_id == atleta_id
    assert reconstituido.entries[0].puntos_overall == Decimal("100.00")
    assert reconstituido.calculado is True


def test_reconstitute_evento_legacy_sin_puntos_overall_usa_cero() -> None:
    """Backward compat: eventos con schema antiguo (puntaje/detalle int) no rompen."""
    torneo_id = uuid4()
    atleta_id = uuid4()

    reconstituido = RankingOverall.reconstitute(
        torneo_id,
        [
            {
                "event_type": "RankingOverallCalculado",
                "payload": {
                    "torneo_id": str(torneo_id),
                    "disciplinas": ["STA"],
                    "total": 1,
                    "entries": [
                        {
                            "posicion": 1,
                            "atleta_id": str(atleta_id),
                            "categoria": "SENIOR_MASCULINO",
                            "puntaje": 3,
                            "detalle": {"STA": 1},
                            "en_podio": True,
                        }
                    ],
                    "calculado_en": "2026-04-01T12:00:00+00:00",
                    "occurred_at": "2026-04-01T12:00:00+00:00",
                },
            }
        ],
    )

    assert reconstituido.calculado is True
    assert reconstituido.entries[0].puntos_overall == Decimal("0.00")
