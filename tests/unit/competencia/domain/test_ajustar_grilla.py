"""Tests unitarios de Competencia.ajustar_grilla() — US-2.1.3."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import (
    GrillaNoGenerada,
    GrillaYaConfirmada,
    PerformanceNoEncontrada,
)
from competencia.domain.events.grilla_de_salida_ajustada import GrillaDeSalidaAjustada
from competencia.domain.ports.performances_ap_port import PerformancesAPData
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

A001 = UUID("00000000-0000-0000-0000-000000000011")
A002 = UUID("00000000-0000-0000-0000-000000000012")
A003 = UUID("00000000-0000-0000-0000-000000000013")

P_A001 = uuid4()
P_A002 = uuid4()
P_A003 = uuid4()


def _make_competencia_con_grilla() -> Competencia:
    """Crea una Competencia STA con grilla generada: A002(pos=1), A001(pos=2), A003(pos=3)."""
    c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
    c.configurar_intervalo_ot(9, "org-01")
    performances = [
        PerformancesAPData(performance_id=P_A001, atleta_id=A001, valor_ap=Decimal("330"), unidad=UnidadMedida.Segundos),
        PerformancesAPData(performance_id=P_A002, atleta_id=A002, valor_ap=Decimal("360"), unidad=UnidadMedida.Segundos),
        PerformancesAPData(performance_id=P_A003, atleta_id=A003, valor_ap=Decimal("285"), unidad=UnidadMedida.Segundos),
    ]
    c.generar_grilla(OT_INICIO, performances)
    c.pull_events()  # limpiar eventos previos
    return c


def _find_entrada(competencia: Competencia, performance_id: UUID):  # type: ignore[return]
    for e in competencia.grilla:
        if e.performance_id == performance_id:
            return e


# ── Invariantes ───────────────────────────────────────────────────────────────


class TestInvariantes:
    def test_grilla_no_generada_lanza_excepcion(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
        c.configurar_intervalo_ot(9, "org-01")
        c.pull_events()
        with pytest.raises(GrillaNoGenerada):
            c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])

    def test_grilla_confirmada_lanza_excepcion(self) -> None:
        c = _make_competencia_con_grilla()
        c._grilla_confirmada = True  # forzar estado confirmado
        with pytest.raises(GrillaYaConfirmada):
            c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])

    def test_performance_no_encontrada_lanza_excepcion(self) -> None:
        c = _make_competencia_con_grilla()
        pid_desconocido = uuid4()
        with pytest.raises(PerformanceNoEncontrada):
            c.ajustar_grilla([CambioGrilla(performance_id=pid_desconocido, campo="posicion", valor_nuevo=1)])


# ── Ajuste de posición ────────────────────────────────────────────────────────


class TestAjustePosicion:
    def test_mover_a001_a_posicion_1_reordena_grilla(self) -> None:
        c = _make_competencia_con_grilla()
        # Grilla inicial: A002(pos=1), A001(pos=2), A003(pos=3)
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        entry = _find_entrada(c, P_A001)
        assert entry.posicion == 1

    def test_ajuste_posicion_recalcula_ot_primera_posicion(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        entry = _find_entrada(c, P_A001)
        assert entry.ot_programado == OT_INICIO

    def test_ajuste_posicion_recalcula_ot_segunda_posicion(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        entry = _find_entrada(c, P_A002)
        assert entry.ot_programado == OT_INICIO + timedelta(minutes=9)

    def test_atleta_sin_cambio_posicion_mantiene_ot_relativo(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        entry = _find_entrada(c, P_A003)
        assert entry.posicion == 3
        assert entry.ot_programado == OT_INICIO + timedelta(minutes=18)


# ── Ajuste de andarivel ───────────────────────────────────────────────────────


class TestAjusteAndarivel:
    def test_cambiar_andarivel_actualiza_entrada(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A002, campo="andarivel", valor_nuevo=2)])
        entry = _find_entrada(c, P_A002)
        assert entry.andarivel == 2

    def test_cambio_andarivel_no_afecta_ot(self) -> None:
        c = _make_competencia_con_grilla()
        ot_antes = _find_entrada(c, P_A002).ot_programado
        c.ajustar_grilla([CambioGrilla(performance_id=P_A002, campo="andarivel", valor_nuevo=2)])
        ot_despues = _find_entrada(c, P_A002).ot_programado
        assert ot_antes == ot_despues

    def test_cambio_andarivel_no_afecta_otros_atletas(self) -> None:
        c = _make_competencia_con_grilla()
        andarivel_a001_antes = _find_entrada(c, P_A001).andarivel
        andarivel_a003_antes = _find_entrada(c, P_A003).andarivel
        c.ajustar_grilla([CambioGrilla(performance_id=P_A002, campo="andarivel", valor_nuevo=2)])
        assert _find_entrada(c, P_A001).andarivel == andarivel_a001_antes
        assert _find_entrada(c, P_A003).andarivel == andarivel_a003_antes


# ── Evento generado ───────────────────────────────────────────────────────────


class TestEventoGenerado:
    def test_emite_grilla_de_salida_ajustada(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], GrillaDeSalidaAjustada)

    def test_evento_contiene_cambios_correctos(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        event = c.pull_events()[0]
        assert isinstance(event, GrillaDeSalidaAjustada)
        assert event.competencia_id == str(COMPETENCIA_ID)
        cambios_perf = [ch for ch in event.cambios if ch["performance_id"] == str(P_A001)]
        assert len(cambios_perf) == 1
        assert cambios_perf[0]["campo"] == "posicion"
        assert cambios_perf[0]["valor_nuevo"] == 1

    def test_ajuste_acumulativo_emite_nuevo_evento(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        c.pull_events()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A002, campo="andarivel", valor_nuevo=2)])
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], GrillaDeSalidaAjustada)


# ── Reconstitución ────────────────────────────────────────────────────────────


class TestReconstitucion:
    def test_reconstituye_grilla_desde_evento_ajustada(self) -> None:
        c = _make_competencia_con_grilla()
        c.ajustar_grilla([CambioGrilla(performance_id=P_A001, campo="posicion", valor_nuevo=1)])
        event_ajuste = c.pull_events()[0]
        assert isinstance(event_ajuste, GrillaDeSalidaAjustada)

        grilla_generada_payload = {
            "competencia_id": str(COMPETENCIA_ID),
            "disciplina": "STA",
            "ot_inicio": OT_INICIO.isoformat(),
            "performances": [
                {"performance_id": str(P_A002), "atleta_id": str(A002), "posicion": 1, "andarivel": 1, "ot_programado": OT_INICIO.isoformat()},
                {"performance_id": str(P_A001), "atleta_id": str(A001), "posicion": 2, "andarivel": 1, "ot_programado": (OT_INICIO + timedelta(minutes=9)).isoformat()},
                {"performance_id": str(P_A003), "atleta_id": str(A003), "posicion": 3, "andarivel": 1, "ot_programado": (OT_INICIO + timedelta(minutes=18)).isoformat()},
            ],
            "generada_en": OT_INICIO.isoformat(),
            "occurred_at": OT_INICIO.isoformat(),
        }

        c2 = Competencia.reconstitute(
            COMPETENCIA_ID,
            Disciplina.STA,
            [
                {
                    "event_type": "IntervaloOTConfigurado",
                    "payload": {
                        "competencia_id": str(COMPETENCIA_ID),
                        "disciplina": "STA",
                        "intervalo_minutos": 9,
                        "configurado_por": "org",
                        "occurred_at": "2026-01-01T00:00:00+00:00",
                    },
                },
                {"event_type": "GrillaDeSalidaGenerada", "payload": grilla_generada_payload},
                {"event_type": "GrillaDeSalidaAjustada", "payload": event_ajuste.to_payload()},
            ],
        )
        entry = _find_entrada(c2, P_A001)
        assert entry.posicion == 1
        assert entry.ot_programado == OT_INICIO
