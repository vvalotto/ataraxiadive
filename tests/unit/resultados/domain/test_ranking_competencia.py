"""Tests unitarios del aggregate RankingCompetencia — US-2.4.2 / US-5.6.3."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from registro.domain.value_objects.categoria import Categoria
from shared.domain.value_objects.disciplina import Disciplina
from resultados.domain.aggregates.ranking_competencia import RankingCompetencia
from resultados.domain.exceptions import ResultadosIncompletos
from resultados.domain.ports.resultados_competencia_port import ResultadoFinal
from resultados.domain.services.algoritmo_faas import AlgoritmoPuntajeFAAS

# ── Helpers ───────────────────────────────────────────────────────────────────


def _resultado(
    rp: str | None = "330",
    unidad: str | None = "Segundos",
    tarjeta: str | None = "Blanca",
    es_dns: bool = False,
    atleta_id: UUID | None = None,
    categoria: Categoria = Categoria.SENIOR_MASCULINO,
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=Decimal(rp) if rp is not None else None,
        unidad=unidad,
        tarjeta=tarjeta,
        es_dns=es_dns,
        categoria=categoria,
    )


def _dns(
    atleta_id: UUID | None = None,
    categoria: Categoria = Categoria.SENIOR_MASCULINO,
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=None,
        unidad=None,
        tarjeta=None,
        es_dns=True,
        categoria=categoria,
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


def test_calcular_segmenta_por_categoria_y_reinicia_posiciones() -> None:
    atleta_sf_1 = uuid4()
    atleta_sf_2 = uuid4()
    atleta_mm_1 = uuid4()

    resultados = [
        _resultado("277", atleta_id=atleta_sf_1, categoria=Categoria.SENIOR_FEMENINO),
        _resultado("225", atleta_id=atleta_sf_2, categoria=Categoria.SENIOR_FEMENINO),
        _resultado("196", atleta_id=atleta_mm_1, categoria=Categoria.MASTER_MASCULINO),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    senior_f = [e for e in ranking.entries if e.categoria == Categoria.SENIOR_FEMENINO]
    master_m = [e for e in ranking.entries if e.categoria == Categoria.MASTER_MASCULINO]

    assert [e.posicion for e in senior_f] == [1, 2]
    assert [e.atleta_id for e in senior_f] == [atleta_sf_1, atleta_sf_2]
    assert [e.posicion for e in master_m] == [1]
    assert master_m[0].atleta_id == atleta_mm_1


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
    raw_events = [{"event_type": e.event_type, "payload": e.to_payload()} for e in events]

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


def test_calcular_blanca_con_penalizaciones_es_valida_y_ordena_por_rp() -> None:
    atleta_penalizado = uuid4()
    atleta_valido = uuid4()

    resultados = [
        _resultado("66", tarjeta="BlancaConPenalizaciones", atleta_id=atleta_penalizado),
        _resultado("70", tarjeta="Blanca", atleta_id=atleta_valido),
    ]

    ranking = _make_ranking()
    ranking.calcular(resultados, None)

    assert ranking.entries[0].atleta_id == atleta_valido
    assert ranking.entries[1].atleta_id == atleta_penalizado


# ── US-5.6.3 — path FAAS con puntos ──────────────────────────────────────────


def _make_ranking_dnf(competencia_id: UUID | None = None) -> RankingCompetencia:
    return RankingCompetencia(
        competencia_id=competencia_id or uuid4(),
        disciplina=Disciplina.DNF,
    )


def _resultado_dnf(
    rp: str,
    tarjeta: str = "Blanca",
    atleta_id: UUID | None = None,
    categoria: Categoria = Categoria.SENIOR_MASCULINO,
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=Decimal(rp),
        unidad="Metros",
        tarjeta=tarjeta,
        es_dns=False,
        categoria=categoria,
    )


def _dns_dnf(
    atleta_id: UUID | None = None,
    categoria: Categoria = Categoria.SENIOR_MASCULINO,
) -> ResultadoFinal:
    return ResultadoFinal(
        atleta_id=atleta_id or uuid4(),
        rp=None,
        unidad=None,
        tarjeta=None,
        es_dns=True,
        categoria=categoria,
    )


def test_calcular_con_faas_incluye_puntos_en_entradas() -> None:
    """Ana (70m) → 100.00 pts; Luis (56m) → 80.00 pts (INV-5.6.3-01)."""
    ana = uuid4()
    luis = uuid4()
    resultados = [
        _resultado_dnf("70", atleta_id=ana, categoria=Categoria.SENIOR_FEMENINO),
        _resultado_dnf("56", atleta_id=luis, categoria=Categoria.SENIOR_MASCULINO),
    ]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())

    by_id = {e.atleta_id: e for e in ranking.entries}
    assert by_id[ana].puntos == Decimal("100.00")
    assert by_id[luis].puntos == Decimal("80.00")


def test_calcular_con_faas_ordena_por_puntos_desc_dentro_de_categoria() -> None:
    """Dentro de cada categoría, la posición se asigna por puntos desc."""
    atleta_a = uuid4()  # 80m → 100 pts
    atleta_b = uuid4()  # 60m → 75 pts
    resultados = [
        _resultado_dnf("60", atleta_id=atleta_b),
        _resultado_dnf("80", atleta_id=atleta_a),
    ]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())

    entries = ranking.entries
    assert entries[0].atleta_id == atleta_a
    assert entries[0].posicion == 1
    assert entries[1].atleta_id == atleta_b
    assert entries[1].posicion == 2


def test_calcular_con_faas_empate_puntos_comparte_posicion() -> None:
    """Dos atletas con mismo RP → mismo puntos → comparten posición (INV-5.6.3-02)."""
    atleta_a = uuid4()
    atleta_b = uuid4()
    resultados = [
        _resultado_dnf("70", atleta_id=atleta_a),
        _resultado_dnf("70", atleta_id=atleta_b),
    ]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())

    assert ranking.entries[0].posicion == 1
    assert ranking.entries[1].posicion == 1
    assert ranking.entries[0].puntos == Decimal("100.00")
    assert ranking.entries[1].puntos == Decimal("100.00")


def test_calcular_con_faas_dns_puntos_cero_sin_podio() -> None:
    """DNS → puntos=0.00, en_podio=False (INV-5.6.3-03)."""
    pedro = uuid4()
    luis = uuid4()
    resultados = [
        _dns_dnf(atleta_id=pedro),
        _resultado_dnf("60", atleta_id=luis),
    ]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())

    by_id = {e.atleta_id: e for e in ranking.entries}
    assert by_id[pedro].puntos == Decimal("0.00")
    assert by_id[pedro].en_podio is False
    assert by_id[luis].puntos == Decimal("100.00")


def test_calcular_con_faas_roja_puntos_cero_sin_podio() -> None:
    """Tarjeta roja → puntos=0.00, en_podio=False (INV-5.6.3-03)."""
    rojo = uuid4()
    blanco = uuid4()
    resultados = [
        _resultado_dnf("50", tarjeta="Roja", atleta_id=rojo),
        _resultado_dnf("70", atleta_id=blanco),
    ]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())

    by_id = {e.atleta_id: e for e in ranking.entries}
    assert by_id[rojo].puntos == Decimal("0.00")
    assert by_id[rojo].en_podio is False


def test_calcular_legacy_sin_algoritmo_puntos_son_cero() -> None:
    """Path legacy (algoritmo=None): puntos siempre 0.00, ordenamiento por RP."""
    atleta_a = uuid4()
    atleta_b = uuid4()
    resultados = [
        _resultado_dnf("50", atleta_id=atleta_b),
        _resultado_dnf("80", atleta_id=atleta_a),
    ]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, None)

    assert all(e.puntos == Decimal("0.00") for e in ranking.entries)
    assert ranking.entries[0].atleta_id == atleta_a  # mayor RP = primero


def test_serializar_entrada_incluye_puntos() -> None:
    """La serialización del evento incluye el campo puntos (INV-5.6.3-05)."""
    ana = uuid4()
    resultados = [_resultado_dnf("70", atleta_id=ana, categoria=Categoria.SENIOR_FEMENINO)]

    ranking = _make_ranking_dnf()
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())
    events = ranking.pull_events()

    payload = events[0].to_payload()
    assert "puntos" in payload["entries"][0]
    assert payload["entries"][0]["puntos"] == "100.00"


def test_reconstitute_restaura_puntos_del_evento() -> None:
    """Reconstitución desde event store recupera puntos sin recalcular."""
    cid = uuid4()
    ana = uuid4()
    resultados = [_resultado_dnf("70", atleta_id=ana, categoria=Categoria.SENIOR_FEMENINO)]

    ranking = RankingCompetencia(competencia_id=cid, disciplina=Disciplina.DNF)
    ranking.calcular(resultados, AlgoritmoPuntajeFAAS())
    events = ranking.pull_events()

    raw = [{"event_type": e.event_type, "payload": e.to_payload()} for e in events]
    ranking2 = RankingCompetencia.reconstitute(
        competencia_id=cid, disciplina=Disciplina.DNF, events=raw
    )

    assert ranking2.entries[0].puntos == Decimal("100.00")


def test_deserializacion_legacy_sin_puntos_usa_fallback_cero() -> None:
    """Eventos legacy sin campo puntos se deserializan con puntos=0.00."""
    cid = uuid4()
    ana = uuid4()

    # Construir evento legacy sin campo puntos
    raw = [
        {
            "event_type": "ResultadosCalculados",
            "payload": {
                "competencia_id": str(cid),
                "disciplina": "DNF",
                "total": 1,
                "entries": [
                    {
                        "posicion": 1,
                        "atleta_id": str(ana),
                        "categoria": "SENIOR_FEMENINO",
                        "rp": "70",
                        "unidad": "Metros",
                        "tarjeta": "Blanca",
                        "es_dns": False,
                        "en_podio": True,
                        # sin campo "puntos"
                    }
                ],
                "calculado_en": "2026-04-26T10:00:00",
                "occurred_at": "2026-04-26T10:00:00",
            },
        }
    ]

    ranking = RankingCompetencia.reconstitute(
        competencia_id=cid, disciplina=Disciplina.DNF, events=raw
    )
    assert ranking.entries[0].puntos == Decimal("0.00")
