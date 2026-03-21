"""Tests unitarios del aggregate Performance — US-1.2.1."""
from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

import pytest

from competencia.domain.aggregates.performance import Performance
from competencia.domain.value_objects.ap import ValorAPInvalido
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida


# ── Fixtures ──────────────────────────────────────────────────────────────────


@pytest.fixture
def performance() -> Performance:
    """Performance vacía lista para registrarAP."""
    return Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.STA,
    )


# ── registrarAP — camino feliz ────────────────────────────────────────────────


def test_registrar_ap_emite_evento(performance: Performance) -> None:
    """registrarAP emite exactamente un evento APRegistrado."""
    performance.registrarAP(Decimal("330"), UnidadMedida.Segundos)

    events = performance.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "APRegistrado"


def test_registrar_ap_establece_estado_anunciada(performance: Performance) -> None:
    """registrarAP transiciona al estado AnunciadaAP."""
    performance.registrarAP(Decimal("330"), UnidadMedida.Segundos)

    assert performance.estado == EstadoPerformance.AnunciadaAP


def test_registrar_ap_persiste_valor_correcto(performance: Performance) -> None:
    """El evento APRegistrado contiene el valor y unidad declarados."""
    valor = Decimal("5.50")
    performance.registrarAP(valor, UnidadMedida.Metros)

    events = performance.pull_events()
    payload = events[0].to_payload()
    assert payload["valor_ap"] == str(valor)
    assert payload["unidad"] == UnidadMedida.Metros.value
    assert payload["disciplina"] == Disciplina.STA.value


def test_registrar_ap_pull_events_vacia_lista(performance: Performance) -> None:
    """pull_events() limpia la lista de eventos pendientes."""
    performance.registrarAP(Decimal("300"), UnidadMedida.Segundos)

    performance.pull_events()  # primera extracción
    assert performance.pull_events() == []


# ── INV-P-01: valorAP > 0 ────────────────────────────────────────────────────


def test_registrar_ap_valor_cero_lanza_excepcion(performance: Performance) -> None:
    """INV-P-01: valor=0 lanza ValorAPInvalido."""
    with pytest.raises(ValorAPInvalido):
        performance.registrarAP(Decimal("0"), UnidadMedida.Segundos)


def test_registrar_ap_valor_negativo_lanza_excepcion(performance: Performance) -> None:
    """INV-P-01: valor negativo lanza ValorAPInvalido."""
    with pytest.raises(ValorAPInvalido):
        performance.registrarAP(Decimal("-1"), UnidadMedida.Metros)


def test_registrar_ap_valor_invalido_no_emite_eventos(performance: Performance) -> None:
    """Si el valor es inválido no quedan eventos pendientes."""
    with pytest.raises(ValorAPInvalido):
        performance.registrarAP(Decimal("0"), UnidadMedida.Segundos)

    assert performance.pull_events() == []


# ── reconstitute ──────────────────────────────────────────────────────────────


def test_reconstitute_desde_eventos_restaura_estado() -> None:
    """reconstitute reconstruye estado AnunciadaAP desde APRegistrado."""
    pid = uuid4()
    cid = uuid4()
    part_id = uuid4()

    perf = Performance(
        performance_id=pid,
        competencia_id=cid,
        participante_id=part_id,
        disciplina=Disciplina.STA,
    )
    perf.registrarAP(Decimal("330"), UnidadMedida.Segundos)
    events = perf.pull_events()

    raw_events = [
        {
            "event_type": e.event_type,
            "payload": e.to_payload(),
        }
        for e in events
    ]

    restored = Performance.reconstitute(raw_events)

    assert restored.estado == EstadoPerformance.AnunciadaAP
    assert restored.ap is not None
    assert restored.ap.valor == Decimal("330")
    assert restored.ap.unidad == UnidadMedida.Segundos


def test_reconstitute_sin_eventos_lanza_error() -> None:
    """reconstitute con lista vacía lanza ValueError."""
    with pytest.raises(ValueError, match="sin eventos"):
        Performance.reconstitute([])


def test_reconstitute_primer_evento_incorrecto_lanza_error() -> None:
    """reconstitute con evento incorrecto lanza ValueError."""
    with pytest.raises(ValueError, match="APRegistrado"):
        Performance.reconstitute([{"event_type": "OtroEvento", "payload": {}}])
