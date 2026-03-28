"""Tests unitarios del aggregate RankingCompetencia — US-2.4.2."""
from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from competencia.domain.value_objects.disciplina import Disciplina
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.exceptions import ResultadosIncompletos
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal


# ── Helpers ───────────────────────────────────────────────────────────────────


def _resultado(
    rp: str | None = "330",
    unidad: str | None = "Segundos",
    tarjeta: str | None = "Blanca",
    es_dns: bool = False,
    atleta_id: UUID | None = None,
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=Decimal(rp) if rp is not None else None,
        unidad=unidad,
        tarjeta=tarjeta,
        es_dns=es_dns,
    )


def _dns(atleta_id: UUID | None = None) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=None,
        unidad=None,
        tarjeta=None,
        es_dns=True,
    )


def _make_ranking(competencia_id: UUID | None = None) -> RankingCompetencia:
    return RankingCompetencia(
        competencia_id=competencia_id or uuid4(),
        disciplina=Disciplina.STA,
    )


# ── calcular — validaciones ───────────────────────────────────────────────────


def test_calcular_sin_resultados_lanza_resultados_incompletos() -> None:
    ranking = _make_ranking()
    with pytest.raises(ResultadosIncompletos):
        ranking.calcular([], None)


# ── calcular — ordenamiento básico ───────────────────────────────────────────


def test_calcular_orden_descendente_por_rp() -> None:
    """Mayor RP → posición 1."""
    atleta_a = uuid4()
    atleta_b = uuid4()
    atleta_c = uuid4()

    resultados = [
        _resultado("200", atleta_id=atleta_b),
        _resultado("330", atleta_id=atleta_a),
        _resultado("150", atleta_id=atleta_c),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].atleta_id == atleta_a
    assert entries[0].posicion == 1
    assert entries[1].atleta_id == atleta_b
    assert entries[1].posicion == 2
    assert entries[2].atleta_id == atleta_c
    assert entries[2].posicion == 3


def test_calcular_emite_resultados_calculados() -> None:
    ranking = _make_ranking()
    ranking.calcular([_resultado()], None)

    events = ranking.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "ResultadosCalculados"


def test_calcular_marca_calculado() -> None:
    ranking = _make_ranking()
    ranking.calcular([_resultado()], None)

    assert ranking.calculado is True


# ── calcular — empates ────────────────────────────────────────────────────────


def test_calcular_empate_comparte_posicion() -> None:
    """Dos atletas con el mismo RP comparten posición."""
    atleta_a = uuid4()
    atleta_b = uuid4()

    resultados = [
        _resultado("300", atleta_id=atleta_a),
        _resultado("300", atleta_id=atleta_b),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].posicion == 1
    assert entries[1].posicion == 1


def test_calcular_empate_omite_siguiente_posicion() -> None:
    """Tras dos atletas empatados en 1°, el siguiente es 3°."""
    atleta_a = uuid4()
    atleta_b = uuid4()
    atleta_c = uuid4()

    resultados = [
        _resultado("300", atleta_id=atleta_a),
        _resultado("300", atleta_id=atleta_b),
        _resultado("200", atleta_id=atleta_c),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[2].posicion == 3
    assert entries[2].atleta_id == atleta_c


def test_calcular_empate_en_segundo_lugar() -> None:
    """Empate en 2°: el siguiente recibe posición 4."""
    atleta_1 = uuid4()
    atleta_2a = uuid4()
    atleta_2b = uuid4()
    atleta_4 = uuid4()

    resultados = [
        _resultado("400", atleta_id=atleta_1),
        _resultado("300", atleta_id=atleta_2a),
        _resultado("300", atleta_id=atleta_2b),
        _resultado("100", atleta_id=atleta_4),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].posicion == 1
    assert entries[1].posicion == 2
    assert entries[2].posicion == 2
    assert entries[3].posicion == 4


# ── calcular — podio ──────────────────────────────────────────────────────────


def test_calcular_podio_posiciones_1_2_3() -> None:
    resultados = [
        _resultado("400"),
        _resultado("300"),
        _resultado("200"),
        _resultado("100"),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].en_podio is True
    assert entries[1].en_podio is True
    assert entries[2].en_podio is True
    assert entries[3].en_podio is False


def test_calcular_empate_en_podio_todos_en_podio() -> None:
    """Empate en posición 1 → ambos en podio."""
    resultados = [
        _resultado("300"),
        _resultado("300"),
        _resultado("100"),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].en_podio is True
    assert entries[1].en_podio is True
    # Tercer atleta queda en posición 3 (empate en 1 consume 1 y 2)
    assert entries[2].posicion == 3
    assert entries[2].en_podio is True


# ── calcular — inválidos al final ─────────────────────────────────────────────


def test_calcular_dns_va_al_final() -> None:
    atleta_valido = uuid4()
    atleta_dns = uuid4()

    resultados = [
        _dns(atleta_id=atleta_dns),
        _resultado("300", atleta_id=atleta_valido),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].atleta_id == atleta_valido
    assert entries[1].atleta_id == atleta_dns
    assert entries[1].es_dns is True


def test_calcular_tarjeta_roja_va_al_final() -> None:
    atleta_valido = uuid4()
    atleta_rojo = uuid4()

    resultados = [
        _resultado("100", tarjeta="Roja", atleta_id=atleta_rojo),
        _resultado("300", atleta_id=atleta_valido),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert entries[0].atleta_id == atleta_valido
    assert entries[1].atleta_id == atleta_rojo


def test_calcular_invalidos_no_en_podio() -> None:
    resultados = [
        _dns(),
        _resultado("100", tarjeta="Roja"),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    for entry in ranking.entries:
        assert entry.en_podio is False


def test_calcular_solo_dns() -> None:
    """Solo DNS: no hay válidos, todos al final con posición incremental."""
    resultados = [_dns(), _dns()]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    entries = ranking.entries
    assert len(entries) == 2
    assert all(e.es_dns for e in entries)


# ── reconstitución ────────────────────────────────────────────────────────────


def test_reconstitute_desde_evento_restaura_entries() -> None:
    """Reconstitute desde EventStore reconstruye el estado correctamente."""
    cid = uuid4()
    atleta_a = uuid4()
    atleta_b = uuid4()

    resultados = [
        _resultado("330", atleta_id=atleta_a),
        _resultado("200", atleta_id=atleta_b),
    ]

    # Calcular y extraer eventos
    ranking = RankingCompetencia(competencia_id=cid, disciplina=Disciplina.STA)
    ranking.calcular(resultados, None)
    events = ranking.pull_events()

    # Serializar como haría el event store
    raw_events = [
        {"event_type": e.event_type, "payload": e.to_payload()} for e in events
    ]

    # Reconstituir
    ranking2 = RankingCompetencia.reconstitute(
        competencia_id=cid,
        disciplina=Disciplina.STA,
        events=raw_events,
    )

    assert ranking2.calculado is True
    assert len(ranking2.entries) == 2
    assert ranking2.entries[0].atleta_id == atleta_a
    assert ranking2.entries[0].posicion == 1
    assert ranking2.entries[1].atleta_id == atleta_b
    assert ranking2.entries[1].posicion == 2
