"""Tests unitarios de Competencia.finalizar() — US-2.4.1 / INV-C-04."""

from __future__ import annotations

from datetime import datetime
from uuid import uuid4

import pytest

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.events.competencia_finalizada import CompetenciaFinalizada
from competencia.domain.exceptions import CompetenciaNoFinalizable
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia

_CID = uuid4()
_DISC = Disciplina.STA


def _competencia_en_ejecucion() -> Competencia:
    """Crea una Competencia en estado EnEjecucion via reconstitución mínima."""
    events = [
        {
            "event_type": "GrillaConfirmada",
            "payload": {
                "competencia_id": str(_CID),
                "disciplina": _DISC.value,
                "confirmada_en": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
            },
        },
        {
            "event_type": "CompetenciaIniciada",
            "payload": {
                "competencia_id": str(_CID),
                "disciplina": _DISC.value,
                "juez_id": "juez-1",
                "iniciada_en": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
            },
        },
    ]
    return Competencia.reconstitute(
        competencia_id=_CID,
        disciplina=_DISC,
        events=events,
    )


# ── Tests ─────────────────────────────────────────────────────────────────────


def test_finalizar_emite_evento() -> None:
    """Finalizar cuando todas las performances terminaron emite CompetenciaFinalizada."""
    competencia = _competencia_en_ejecucion()

    competencia.finalizar(total_performances=3, ejecutadas=2, dns_count=1)

    eventos = competencia.pull_events()
    assert len(eventos) == 1
    assert isinstance(eventos[0], CompetenciaFinalizada)


def test_finalizar_transiciona_a_finalizada() -> None:
    """Estado pasa a Finalizada tras finalizar()."""
    competencia = _competencia_en_ejecucion()
    competencia.finalizar(total_performances=3, ejecutadas=3, dns_count=0)

    assert competencia.estado == EstadoCompetencia.Finalizada


def test_finalizar_payload_correcto() -> None:
    """El payload de CompetenciaFinalizada contiene los contadores correctos."""
    competencia = _competencia_en_ejecucion()
    competencia.finalizar(total_performances=4, ejecutadas=3, dns_count=1)

    evento = competencia.pull_events()[0]
    assert isinstance(evento, CompetenciaFinalizada)
    assert evento.total_performances == 4
    assert evento.ejecutadas == 3
    assert evento.dns_count == 1
    assert evento.competencia_id == str(_CID)
    assert evento.disciplina == _DISC.value


def test_finalizar_rechaza_si_quedan_pendientes() -> None:
    """INV-C-04: CompetenciaNoFinalizable si quedan performances sin terminar."""
    competencia = _competencia_en_ejecucion()

    with pytest.raises(CompetenciaNoFinalizable):
        competencia.finalizar(total_performances=3, ejecutadas=1, dns_count=1)


def test_finalizar_rechaza_con_mensaje_descriptivo() -> None:
    """El mensaje de CompetenciaNoFinalizable indica cuántas performances faltan."""
    competencia = _competencia_en_ejecucion()

    with pytest.raises(CompetenciaNoFinalizable, match="1 performance"):
        competencia.finalizar(total_performances=3, ejecutadas=2, dns_count=0)


def test_reconstitute_aplica_competencia_finalizada() -> None:
    """La reconstitución aplica CompetenciaFinalizada y refleja estado Finalizada."""
    events = [
        {
            "event_type": "GrillaConfirmada",
            "payload": {
                "competencia_id": str(_CID),
                "disciplina": _DISC.value,
                "confirmada_en": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 3, 22, 9, 0, 0).isoformat(),
            },
        },
        {
            "event_type": "CompetenciaIniciada",
            "payload": {
                "competencia_id": str(_CID),
                "disciplina": _DISC.value,
                "juez_id": "juez-1",
                "iniciada_en": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 3, 22, 10, 0, 0).isoformat(),
            },
        },
        {
            "event_type": "CompetenciaFinalizada",
            "payload": {
                "competencia_id": str(_CID),
                "disciplina": _DISC.value,
                "total_performances": 2,
                "ejecutadas": 1,
                "dns_count": 1,
                "finalizada_en": datetime(2026, 3, 22, 12, 0, 0).isoformat(),
                "occurred_at": datetime(2026, 3, 22, 12, 0, 0).isoformat(),
            },
        },
    ]
    competencia = Competencia.reconstitute(competencia_id=_CID, disciplina=_DISC, events=events)

    assert competencia.estado == EstadoCompetencia.Finalizada
