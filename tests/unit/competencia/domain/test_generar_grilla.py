"""Tests unitarios de Competencia.generar_grilla() — US-2.1.2."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from decimal import Decimal
from uuid import UUID, uuid4

import pytest

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.exceptions import (
    GrillaYaConfirmada,
    IntervaloNoConfigurado,
    SinPerformancesParaGrilla,
)
from competencia.domain.events.grilla_de_salida_generada import GrillaDeSalidaGenerada
from competencia.domain.ports.performances_ap_port import PerformancesAPData
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.disciplina_descriptor import DisciplinaDescriptor
from competencia.domain.value_objects.unidad_medida import UnidadMedida

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000001")
OT_INICIO = datetime(2026, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

_DESC_STA = DisciplinaDescriptor.para(Disciplina.STA)
_DESC_DNF = DisciplinaDescriptor.para(Disciplina.DNF)


def _make_competencia(disciplina: Disciplina = Disciplina.STA) -> Competencia:
    c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=disciplina)
    c.configurar_intervalo_ot(9, "org-01")
    c.pull_events()  # limpiar eventos de configuración
    return c


def _perf(atleta_id: str, valor_ap: str, unidad: UnidadMedida) -> PerformancesAPData:
    return PerformancesAPData(
        performance_id=uuid4(),
        atleta_id=UUID(atleta_id),
        valor_ap=Decimal(valor_ap),
        unidad=unidad,
    )


def _sta(atleta_id: str, segundos: str) -> PerformancesAPData:
    return _perf(atleta_id, segundos, UnidadMedida.Segundos)


def _dnf(atleta_id: str, metros: str) -> PerformancesAPData:
    return _perf(atleta_id, metros, UnidadMedida.Metros)


A001 = "00000000-0000-0000-0000-000000000011"
A002 = "00000000-0000-0000-0000-000000000012"
A003 = "00000000-0000-0000-0000-000000000013"


# ── Invariantes ───────────────────────────────────────────────────────────────


class TestInvariantes:
    def test_sin_intervalo_lanza_intervalo_no_configurado(self) -> None:
        c = Competencia(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.STA)
        with pytest.raises(IntervaloNoConfigurado):
            c.generar_grilla(OT_INICIO, [_sta(A001, "330")], _DESC_STA)

    def test_sin_performances_lanza_sin_performances(self) -> None:
        c = _make_competencia()
        with pytest.raises(SinPerformancesParaGrilla):
            c.generar_grilla(OT_INICIO, [], _DESC_STA)

    def test_grilla_confirmada_lanza_excepcion(self) -> None:
        c = Competencia.reconstitute(
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
                {
                    "event_type": "GrillaConfirmada",
                    "payload": {"competencia_id": str(COMPETENCIA_ID)},
                },
            ],
        )
        with pytest.raises(GrillaYaConfirmada):
            c.generar_grilla(OT_INICIO, [_sta(A001, "330")], _DESC_STA)


# ── Ordenamiento STA (tiempo, menor→mayor) ────────────────────────────────────


class TestOrdenamientoSTA:
    def test_orden_menor_a_mayor_por_ap(self) -> None:
        c = _make_competencia(Disciplina.STA)
        performances = [
            _sta(A001, "330"),  # 5:30
            _sta(A002, "360"),  # 6:00 — mayor, debe ir último
            _sta(A003, "285"),  # 4:45 — menor, debe ir primero
        ]
        c.generar_grilla(OT_INICIO, performances, _DESC_STA)
        grilla = c.grilla
        atletas_orden = [str(e.atleta_id) for e in grilla]
        assert atletas_orden == [A003, A001, A002]

    def test_posiciones_1_based(self) -> None:
        c = _make_competencia(Disciplina.STA)
        c.generar_grilla(OT_INICIO, [_sta(A001, "330"), _sta(A002, "360")], _DESC_STA)
        posiciones = [e.posicion for e in c.grilla]
        assert posiciones == [1, 2]

    def test_ot_primera_posicion_es_ot_inicio(self) -> None:
        c = _make_competencia(Disciplina.STA)
        c.generar_grilla(OT_INICIO, [_sta(A001, "330")], _DESC_STA)
        assert c.grilla[0].ot_programado == OT_INICIO

    def test_ot_segunda_posicion_suma_intervalo(self) -> None:
        c = _make_competencia(Disciplina.STA)
        c.generar_grilla(OT_INICIO, [_sta(A002, "360"), _sta(A001, "330")], _DESC_STA)
        expected = OT_INICIO + timedelta(minutes=9)
        assert c.grilla[1].ot_programado == expected

    def test_ot_tercera_posicion_suma_dos_intervalos(self) -> None:
        c = _make_competencia(Disciplina.STA)
        perfs = [_sta(A001, "330"), _sta(A002, "360"), _sta(A003, "285")]
        c.generar_grilla(OT_INICIO, perfs, _DESC_STA)
        expected = OT_INICIO + timedelta(minutes=18)
        assert c.grilla[2].ot_programado == expected


# ── Ordenamiento DNF (distancia, menor→mayor) ─────────────────────────────────


class TestOrdenamientoDNF:
    def test_orden_menor_a_mayor_por_ap(self) -> None:
        c = _make_competencia(Disciplina.DNF)
        performances = [
            _dnf(A001, "80"),
            _dnf(A002, "60"),  # menor — debe ir primero
            _dnf(A003, "100"),  # mayor — debe ir último
        ]
        c.generar_grilla(OT_INICIO, performances, _DESC_DNF)
        atletas_orden = [str(e.atleta_id) for e in c.grilla]
        assert atletas_orden == [A002, A001, A003]


# ── Evento generado ───────────────────────────────────────────────────────────


class TestEventoGenerado:
    def test_emite_un_evento(self) -> None:
        c = _make_competencia()
        c.generar_grilla(OT_INICIO, [_sta(A001, "330")], _DESC_STA)
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], GrillaDeSalidaGenerada)

    def test_evento_contiene_datos_correctos(self) -> None:
        c = _make_competencia()
        c.generar_grilla(OT_INICIO, [_sta(A001, "330")], _DESC_STA)
        event = c.pull_events()[0]
        assert isinstance(event, GrillaDeSalidaGenerada)
        assert event.competencia_id == str(COMPETENCIA_ID)
        assert event.disciplina == "STA"
        assert len(event.performances) == 1
        assert event.performances[0]["posicion"] == 1

    def test_regeneracion_emite_nuevo_evento(self) -> None:
        c = _make_competencia()
        c.generar_grilla(OT_INICIO, [_sta(A001, "330")], _DESC_STA)
        c.pull_events()
        c.generar_grilla(OT_INICIO, [_sta(A001, "330"), _sta(A002, "360")], _DESC_STA)
        events = c.pull_events()
        assert len(events) == 1
        assert isinstance(events[0], GrillaDeSalidaGenerada)
        assert len(events[0].performances) == 2


# ── Andarivel ─────────────────────────────────────────────────────────────────


class TestAndarivel:
    def test_un_andarivel_todos_en_andarivel_1(self) -> None:
        c = _make_competencia()
        perfs = [_sta(A001, "330"), _sta(A002, "360"), _sta(A003, "285")]
        c.generar_grilla(OT_INICIO, perfs, _DESC_STA, andariveles=1)
        assert all(e.andarivel == 1 for e in c.grilla)


# ── Reconstitución ────────────────────────────────────────────────────────────


class TestReconstitucion:
    def test_reconstituye_grilla_desde_evento(self) -> None:
        c = _make_competencia()
        perfs = [_sta(A001, "330"), _sta(A002, "360")]
        c.generar_grilla(OT_INICIO, perfs, _DESC_STA)
        event = c.pull_events()[0]
        assert isinstance(event, GrillaDeSalidaGenerada)

        # Reconstruir desde payload
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
                {
                    "event_type": "GrillaDeSalidaGenerada",
                    "payload": event.to_payload(),
                },
            ],
        )
        assert len(c2.grilla) == 2
        assert c2.grilla[0].posicion == 1
