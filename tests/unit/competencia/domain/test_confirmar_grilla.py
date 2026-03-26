"""Tests unitarios de Competencia.confirmar_grilla() e iniciar_competencia() — US-2.1.4."""
from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.events.competencia_iniciada import CompetenciaIniciada
from competencia.domain.events.grilla_confirmada import GrillaConfirmada
from competencia.domain.exceptions import (
    CompetenciaNoConfirmada,
    GrillaNoGenerada,
    GrillaYaConfirmada,
)
from competencia.domain.ports.performances_ap_port import PerformancesAPData
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.unidad_medida import UnidadMedida

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000002")
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
A001 = "00000000-0000-0000-0000-000000000011"
A002 = "00000000-0000-0000-0000-000000000012"


def _make_competencia_con_grilla() -> Competencia:
    """Retorna una Competencia con grilla generada pero no confirmada."""
    c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
    c.configurar_intervalo_ot(9, "org-01")
    performances = [
        PerformancesAPData(
            performance_id=uuid4(),
            atleta_id=UUID(A001),
            valor_ap=Decimal("300"),
            unidad=UnidadMedida.Segundos,
        ),
        PerformancesAPData(
            performance_id=uuid4(),
            atleta_id=UUID(A002),
            valor_ap=Decimal("240"),
            unidad=UnidadMedida.Segundos,
        ),
    ]
    c.generar_grilla(OT_INICIO, performances, DisciplinaDescriptor.para(Disciplina.STA))
    c.pull_events()  # limpiar eventos anteriores
    return c


def _make_competencia_confirmada() -> Competencia:
    """Retorna una Competencia con grilla confirmada."""
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    c.pull_events()
    return c


# ── confirmar_grilla ───────────────────────────────────────────────────────────


def test_confirmar_grilla_emite_grilla_confirmada() -> None:
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    eventos = c.pull_events()
    assert len(eventos) == 1
    assert isinstance(eventos[0], GrillaConfirmada)


def test_confirmar_grilla_cambia_estado_a_confirmada() -> None:
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    assert c.estado == EstadoCompetencia.Confirmada


def test_confirmar_grilla_activa_flag_grilla_confirmada() -> None:
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    assert c.grilla_confirmada is True


def test_confirmar_grilla_sin_grilla_lanza_grilla_no_generada() -> None:
    c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
    with pytest.raises(GrillaNoGenerada):
        c.confirmar_grilla()


def test_confirmar_grilla_dos_veces_lanza_grilla_ya_confirmada() -> None:
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    c.pull_events()
    with pytest.raises(GrillaYaConfirmada):
        c.confirmar_grilla()


def test_grilla_confirmada_payload_tiene_campos_correctos() -> None:
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    evento = c.pull_events()[0]
    assert isinstance(evento, GrillaConfirmada)
    payload = evento.to_payload()
    assert payload["competencia_id"] == str(COMPETENCIA_ID)
    assert payload["disciplina"] == "STA"
    assert "confirmada_en" in payload


# ── iniciar_competencia ────────────────────────────────────────────────────────


def test_iniciar_competencia_emite_competencia_iniciada() -> None:
    c = _make_competencia_confirmada()
    c.iniciar_competencia("juez-01")
    eventos = c.pull_events()
    assert len(eventos) == 1
    assert isinstance(eventos[0], CompetenciaIniciada)


def test_iniciar_competencia_cambia_estado_a_en_ejecucion() -> None:
    c = _make_competencia_confirmada()
    c.iniciar_competencia("juez-01")
    assert c.estado == EstadoCompetencia.EnEjecucion


def test_iniciar_competencia_sin_confirmar_lanza_competencia_no_confirmada() -> None:
    c = _make_competencia_con_grilla()  # estado Preparacion
    with pytest.raises(CompetenciaNoConfirmada):
        c.iniciar_competencia("juez-01")


def test_iniciar_competencia_desde_preparacion_lanza_error() -> None:
    c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
    with pytest.raises(CompetenciaNoConfirmada):
        c.iniciar_competencia("juez-01")


def test_competencia_iniciada_payload_tiene_campos_correctos() -> None:
    c = _make_competencia_confirmada()
    c.iniciar_competencia("juez-42")
    evento = c.pull_events()[0]
    assert isinstance(evento, CompetenciaIniciada)
    payload = evento.to_payload()
    assert payload["competencia_id"] == str(COMPETENCIA_ID)
    assert payload["disciplina"] == "STA"
    assert payload["juez_id"] == "juez-42"
    assert "iniciada_en" in payload


# ── reconstitución ─────────────────────────────────────────────────────────────


def test_reconstitution_restaura_estado_confirmada() -> None:
    c = _make_competencia_con_grilla()
    c.confirmar_grilla()
    eventos_raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in c.pull_events()
    ]
    c2 = Competencia.reconstitute(
        competencia_id=COMPETENCIA_ID,
        disciplina=Disciplina.STA,
        events=eventos_raw,
    )
    # Solo tiene GrillaConfirmada en el stream recortado — estado depende del evento
    assert c2.grilla_confirmada is True


def test_reconstitution_restaura_estado_en_ejecucion() -> None:
    c = _make_competencia_confirmada()
    c.iniciar_competencia("juez-01")
    evento = c.pull_events()[0]
    raw = [{"event_type": evento.event_type, "payload": evento.to_payload()}]
    # Reconstituimos solo con el evento de inicio; estado previo ya era EnEjecucion
    c_fresh = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
    c_fresh._apply_stored(raw[0])  # pylint: disable=protected-access
    assert c_fresh.estado == EstadoCompetencia.EnEjecucion
