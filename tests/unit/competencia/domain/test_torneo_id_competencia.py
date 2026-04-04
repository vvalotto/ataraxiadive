"""Tests unitarios — torneo_id en Competencia (US-3.3.1)."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.value_objects.disciplina import Disciplina

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
TORNEO_ID = UUID("00000000-0000-0000-0000-000000000099")
DISCIPLINA = Disciplina.STA


class TestTorneoIdInvariantesCT01:
    """INV-CT-01: torneo_id es opcional — backward compat total."""

    def test_competencia_sin_torneo_id_tiene_none(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        assert c.torneo_id is None

    def test_configurar_intervalo_sin_torneo_id_mantiene_none(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        c.configurar_intervalo_ot(intervalo_minutos=9, configurado_por="org-01")
        assert c.torneo_id is None

    def test_eventos_existentes_sin_torneo_id_no_rompen(self) -> None:
        """Streams SP1/SP2 sin torneo_id en payload — backward compat."""
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        evento_viejo = {
            "event_type": "IntervaloOTConfigurado",
            "payload": {
                "competencia_id": str(COMPETENCIA_ID),
                "disciplina": DISCIPLINA.value,
                "intervalo_minutos": 9,
                "configurado_por": "org-01",
                "occurred_at": "2026-01-01T00:00:00",
                # sin torneo_id — stream SP1/SP2
            },
        }
        c._apply_stored(evento_viejo)
        assert c.torneo_id is None
        assert c.intervalo is not None
        assert c.intervalo.minutos == 9


class TestTorneoIdInvariantesCT02:
    """INV-CT-02: si torneo_id se provee, se persiste en el evento."""

    def test_configurar_con_torneo_id_actualiza_propiedad(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        c.configurar_intervalo_ot(
            intervalo_minutos=9, configurado_por="org-01", torneo_id=TORNEO_ID
        )
        assert c.torneo_id == TORNEO_ID

    def test_evento_emitido_contiene_torneo_id(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        c.configurar_intervalo_ot(
            intervalo_minutos=9, configurado_por="org-01", torneo_id=TORNEO_ID
        )
        events = c.pull_events()
        assert len(events) == 1
        payload = events[0].to_payload()
        assert payload["torneo_id"] == str(TORNEO_ID)

    def test_evento_emitido_sin_torneo_id_tiene_none(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        c.configurar_intervalo_ot(intervalo_minutos=9, configurado_por="org-01")
        events = c.pull_events()
        payload = events[0].to_payload()
        assert payload["torneo_id"] is None

    def test_reconstitute_desde_evento_con_torneo_id(self) -> None:
        evento = {
            "event_type": "IntervaloOTConfigurado",
            "payload": {
                "competencia_id": str(COMPETENCIA_ID),
                "disciplina": DISCIPLINA.value,
                "intervalo_minutos": 9,
                "configurado_por": "org-01",
                "torneo_id": str(TORNEO_ID),
                "occurred_at": "2026-01-01T00:00:00",
            },
        }
        c = Competencia.reconstitute(
            competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA, events=[evento]
        )
        assert c.torneo_id == TORNEO_ID

    def test_reconfiguracion_no_sobreescribe_torneo_id_con_none(self) -> None:
        """Reconfigurar sin pasar torneo_id no borra el torneo_id existente."""
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=DISCIPLINA)
        c.configurar_intervalo_ot(
            intervalo_minutos=9, configurado_por="org-01", torneo_id=TORNEO_ID
        )
        c.pull_events()
        c.configurar_intervalo_ot(intervalo_minutos=12, configurado_por="org-01")
        assert c.torneo_id == TORNEO_ID
