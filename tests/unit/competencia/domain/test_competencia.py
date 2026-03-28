"""Tests unitarios del aggregate Competencia — US-2.1.1."""
from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import GrillaYaConfirmada
from competencia.domain.events.intervalo_ot_configurado import IntervaloOTConfigurado
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.intervalo_disciplina import IntervaloInvalido

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
DISCIPLINA = Disciplina.STA
CONFIGURADO_POR = "organizador-01"


def _make_competencia() -> Competencia:
    return Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)


# ── Estado inicial ────────────────────────────────────────────────────────────


class TestEstadoInicial:
    def test_estado_inicial_es_preparacion(self) -> None:
        c = _make_competencia()
        assert c.estado == EstadoCompetencia.Preparacion

    def test_intervalo_inicial_es_none(self) -> None:
        c = _make_competencia()
        assert c.intervalo is None

    def test_disciplina_asignada(self) -> None:
        c = _make_competencia()
        assert c.disciplina == DISCIPLINA


# ── Configurar intervalo ──────────────────────────────────────────────────────


class TestConfigurarIntervaloOT:
    def test_configurar_intervalo_exitosamente(self) -> None:
        c = _make_competencia()
        c.configurar_intervalo_ot(9, CONFIGURADO_POR)
        assert c.intervalo is not None
        assert c.intervalo.minutos == 9

    def test_emite_evento_intervalo_ot_configurado(self) -> None:
        c = _make_competencia()
        c.configurar_intervalo_ot(9, CONFIGURADO_POR)
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], IntervaloOTConfigurado)

    def test_evento_tiene_datos_correctos(self) -> None:
        c = _make_competencia()
        c.configurar_intervalo_ot(9, CONFIGURADO_POR)
        event = c.pull_events()[0]
        assert isinstance(event, IntervaloOTConfigurado)
        assert event.competencia_id == str(COMPETENCIA_ID)
        assert event.disciplina == DISCIPLINA.value
        assert event.intervalo_minutos == 9
        assert event.configurado_por == CONFIGURADO_POR

    def test_estado_sigue_siendo_preparacion(self) -> None:
        c = _make_competencia()
        c.configurar_intervalo_ot(9, CONFIGURADO_POR)
        assert c.estado == EstadoCompetencia.Preparacion

    def test_reconfiguracion_permitida(self) -> None:
        c = _make_competencia()
        c.configurar_intervalo_ot(7, CONFIGURADO_POR)
        c.pull_events()  # limpiar
        c.configurar_intervalo_ot(10, CONFIGURADO_POR)
        assert c.intervalo is not None
        assert c.intervalo.minutos == 10
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], IntervaloOTConfigurado)
        assert events[0].intervalo_minutos == 10

    def test_rechazo_intervalo_cero(self) -> None:
        c = _make_competencia()
        with pytest.raises(IntervaloInvalido):
            c.configurar_intervalo_ot(0, CONFIGURADO_POR)

    def test_rechazo_intervalo_negativo(self) -> None:
        c = _make_competencia()
        with pytest.raises(IntervaloInvalido):
            c.configurar_intervalo_ot(-5, CONFIGURADO_POR)

    def test_rechazo_grilla_ya_confirmada(self) -> None:
        c = _make_competencia()
        # Simular que ya se emitió GrillaConfirmada reconstituyendo con ese evento
        c_reconstituida = Competencia.reconstitute(
            competencia_id=COMPETENCIA_ID,
            disciplina=DISCIPLINA,
            events=[
                {
                    "event_type": "GrillaConfirmada",
                    "payload": {"competencia_id": str(COMPETENCIA_ID)},
                }
            ],
        )
        with pytest.raises(GrillaYaConfirmada):
            c_reconstituida.configurar_intervalo_ot(9, CONFIGURADO_POR)

    def test_intervalo_estado_no_cambia_tras_rechazo(self) -> None:
        c = _make_competencia()
        with pytest.raises(IntervaloInvalido):
            c.configurar_intervalo_ot(0, CONFIGURADO_POR)
        assert c.intervalo is None
        assert len(c.pull_events()) == 0


# ── Reconstitución desde eventos ──────────────────────────────────────────────


class TestReconstitucion:
    def test_reconstituye_con_intervalo_configurado(self) -> None:
        events = [
            {
                "event_type": "IntervaloOTConfigurado",
                "payload": {
                    "competencia_id": str(COMPETENCIA_ID),
                    "disciplina": DISCIPLINA.value,
                    "intervalo_minutos": 9,
                    "configurado_por": CONFIGURADO_POR,
                    "occurred_at": "2026-01-01T00:00:00+00:00",
                },
            }
        ]
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.intervalo is not None
        assert c.intervalo.minutos == 9

    def test_reconstituye_con_lista_vacia(self) -> None:
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, [])
        assert c.intervalo is None
        assert c.estado == EstadoCompetencia.Preparacion

    def test_reconstituye_ultima_reconfiguracion(self) -> None:
        events = [
            {
                "event_type": "IntervaloOTConfigurado",
                "payload": {
                    "competencia_id": str(COMPETENCIA_ID),
                    "disciplina": DISCIPLINA.value,
                    "intervalo_minutos": 7,
                    "configurado_por": CONFIGURADO_POR,
                    "occurred_at": "2026-01-01T00:00:00+00:00",
                },
            },
            {
                "event_type": "IntervaloOTConfigurado",
                "payload": {
                    "competencia_id": str(COMPETENCIA_ID),
                    "disciplina": DISCIPLINA.value,
                    "intervalo_minutos": 10,
                    "configurado_por": CONFIGURADO_POR,
                    "occurred_at": "2026-01-01T00:01:00+00:00",
                },
            },
        ]
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.intervalo is not None
        assert c.intervalo.minutos == 10

    def test_reconstituye_grilla_confirmada(self) -> None:
        events = [
            {
                "event_type": "GrillaConfirmada",
                "payload": {"competencia_id": str(COMPETENCIA_ID)},
            }
        ]
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        with pytest.raises(GrillaYaConfirmada):
            c.configurar_intervalo_ot(9, CONFIGURADO_POR)

    def test_ignora_eventos_desconocidos(self) -> None:
        events = [
            {
                "event_type": "EventoDesconocido",
                "payload": {"foo": "bar"},
            }
        ]
        c = Competencia.reconstitute(COMPETENCIA_ID, DISCIPLINA, events)
        assert c.intervalo is None
