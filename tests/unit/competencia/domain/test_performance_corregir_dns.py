"""Tests unitarios de correccion de resultado tras DNS — US-ADJ-7.1."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import (
    EstadoInvalidoParaCorregirResultadoTrasDNS,
    MotivoObligatorio,
)
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida

OT = datetime(2026, 3, 23, 10, 30, 0)


def _performance_en_dns() -> Performance:
    performance = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    performance.registrar_ap(Decimal("50"), UnidadMedida.Metros)
    performance.pull_events()
    performance.llamar(OT, posicion_grilla=1)
    performance.pull_events()
    performance.registrar_dns("juez-001")
    performance.pull_events()
    return performance


def _performance_en_llamada() -> Performance:
    performance = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    performance.registrar_ap(Decimal("50"), UnidadMedida.Metros)
    performance.pull_events()
    performance.llamar(OT, posicion_grilla=1)
    performance.pull_events()
    return performance


def test_corregir_resultado_tras_dns_emite_evento_y_deja_resultado_registrado() -> None:
    performance = _performance_en_dns()

    performance.corregir_resultado_tras_dns(
        valor_rp=Decimal("50.25"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-002",
        motivo_correccion="DNS cargado por error",
    )

    events = performance.pull_events()
    assert events[0].event_type == "ResultadoCorregidoTrasDNS"
    assert performance.estado == EstadoPerformance.ResultadoRegistrado
    assert performance.rp == Decimal("50.25")


def test_corregir_resultado_tras_dns_payload_auditable() -> None:
    performance = _performance_en_dns()

    performance.corregir_resultado_tras_dns(
        valor_rp=Decimal("49.9"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-007",
        motivo_correccion="El atleta se presento y ejecuto",
    )

    payload = performance.pull_events()[0].to_payload()
    assert payload["valor_rp"] == "49.9"
    assert payload["unidad"] == "Metros"
    assert payload["registrado_por"] == "juez-007"
    assert payload["motivo_correccion"] == "El atleta se presento y ejecuto"


def test_corregir_resultado_tras_dns_permite_asignar_tarjeta() -> None:
    performance = _performance_en_dns()
    performance.corregir_resultado_tras_dns(
        valor_rp=Decimal("51.0"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-002",
        motivo_correccion="Correccion operativa",
    )
    performance.pull_events()

    performance.asignar_tarjeta(TipoTarjeta.Blanca, "juez-002")

    assert performance.estado == EstadoPerformance.Ejecutada
    assert performance.tarjeta == TipoTarjeta.Blanca


def test_corregir_resultado_tras_dns_desde_ejecutada_lanza_error() -> None:
    performance = _performance_en_dns()
    performance.corregir_resultado_tras_dns(
        valor_rp=Decimal("51.0"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-002",
        motivo_correccion="Correccion operativa",
    )
    performance.pull_events()
    performance.asignar_tarjeta(TipoTarjeta.Blanca, "juez-002")
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaCorregirResultadoTrasDNS):
        performance.corregir_resultado_tras_dns(
            valor_rp=Decimal("52.0"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-002",
            motivo_correccion="Nuevo ajuste",
        )


def test_corregir_resultado_tras_dns_desde_llamada_lanza_error() -> None:
    performance = _performance_en_llamada()

    with pytest.raises(EstadoInvalidoParaCorregirResultadoTrasDNS):
        performance.corregir_resultado_tras_dns(
            valor_rp=Decimal("51.0"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-002",
            motivo_correccion="Correccion operativa",
        )


def test_corregir_resultado_tras_dns_requiere_motivo() -> None:
    performance = _performance_en_dns()

    with pytest.raises(MotivoObligatorio):
        performance.corregir_resultado_tras_dns(
            valor_rp=Decimal("51.0"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-002",
            motivo_correccion=" ",
        )


def test_corregir_resultado_tras_dns_rechaza_rp_negativo() -> None:
    performance = _performance_en_dns()

    with pytest.raises(ValueError, match="mayor o igual a 0"):
        performance.corregir_resultado_tras_dns(
            valor_rp=Decimal("-1"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez-002",
            motivo_correccion="Correccion operativa",
        )


def test_replay_resultado_corregido_tras_dns_reconstruye_resultado_registrado() -> None:
    performance = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    stored_events = []
    performance.registrar_ap(Decimal("50"), UnidadMedida.Metros)
    stored_events.extend(performance.pull_events())
    performance.llamar(OT, posicion_grilla=1)
    stored_events.extend(performance.pull_events())
    performance.registrar_dns("juez-001")
    stored_events.extend(performance.pull_events())
    performance.corregir_resultado_tras_dns(
        valor_rp=Decimal("50.25"),
        unidad=UnidadMedida.Metros,
        registrado_por="juez-002",
        motivo_correccion="DNS cargado por error",
    )
    stored_events.extend(performance.pull_events())
    raw_events = [
        {"event_type": event.event_type, "payload": event.to_payload()} for event in stored_events
    ]

    restored = Performance.reconstitute(raw_events)

    assert restored.estado == EstadoPerformance.ResultadoRegistrado
    assert restored.rp == Decimal("50.25")
