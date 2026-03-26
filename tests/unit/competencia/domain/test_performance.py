"""Tests unitarios del aggregate Performance — US-1.2.1 a US-1.4.1."""
from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import uuid4

import pytest

from competencia.domain.aggregates.performance import Performance
from competencia.domain.exceptions import (
    DistanciaBlackoutObligatoria,
    EstadoInvalidoParaAsignarTarjeta,
    EstadoInvalidoParaCorregirResultado,
    EstadoInvalidoParaLlamar,
    EstadoInvalidoParaRegistrarDNS,
    EstadoInvalidoParaRegistrarResultado,
    MotivoObligatorio,
)
from competencia.domain.value_objects.ap import ValorAPInvalido
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida

OT = datetime(2026, 3, 22, 10, 30, 0)


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


# ── llamar() — camino feliz ───────────────────────────────────────────────────


@pytest.fixture
def performance_anunciada() -> Performance:
    """Performance con AP registrado, lista para ser llamada."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.STA,
    )
    p.registrarAP(Decimal("330"), UnidadMedida.Segundos)
    p.pull_events()  # limpiar eventos pendientes de registrarAP
    return p


def test_llamar_emite_evento_atleta_llamado(performance_anunciada: Performance) -> None:
    """llamar() emite exactamente un evento AtletaLlamado."""
    performance_anunciada.llamar(OT, posicion_grilla=3)

    events = performance_anunciada.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "AtletaLlamado"


def test_llamar_transiciona_a_estado_llamada(performance_anunciada: Performance) -> None:
    """llamar() transiciona al estado Llamada."""
    performance_anunciada.llamar(OT, posicion_grilla=1)

    assert performance_anunciada.estado == EstadoPerformance.Llamada


def test_llamar_payload_contiene_datos_correctos(performance_anunciada: Performance) -> None:
    """El evento AtletaLlamado contiene posicion_grilla y ot_programado correctos."""
    performance_anunciada.llamar(OT, posicion_grilla=5)

    events = performance_anunciada.pull_events()
    payload = events[0].to_payload()
    assert payload["posicion_grilla"] == 5
    assert payload["ot_programado"] == OT.isoformat()


# ── llamar() — invariantes ────────────────────────────────────────────────────


def test_llamar_en_estado_no_anunciada_lanza_excepcion(performance_anunciada: Performance) -> None:
    """INV: llamar() sobre Performance ya en Llamada lanza EstadoInvalidoParaLlamar."""
    performance_anunciada.llamar(OT, posicion_grilla=1)
    performance_anunciada.pull_events()

    with pytest.raises(EstadoInvalidoParaLlamar):
        performance_anunciada.llamar(OT, posicion_grilla=2)


def test_llamar_estado_invalido_no_emite_eventos(performance_anunciada: Performance) -> None:
    """Si el estado es inválido no quedan eventos pendientes."""
    performance_anunciada.llamar(OT, posicion_grilla=1)
    performance_anunciada.pull_events()

    with pytest.raises(EstadoInvalidoParaLlamar):
        performance_anunciada.llamar(OT, posicion_grilla=2)

    assert performance_anunciada.pull_events() == []


# ── reconstitute con AtletaLlamado ───────────────────────────────────────────


def test_performance_id_propiedad(performance: Performance) -> None:
    """performance_id retorna el UUID asignado en construcción."""
    pid = uuid4()
    p = Performance(
        performance_id=pid,
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.STA,
    )
    assert p.performance_id == pid


def test_reconstitute_payload_como_string_json() -> None:
    """_parse_payload maneja payload serializado como string JSON."""
    import json as _json

    pid = uuid4()
    cid = uuid4()
    part_id = uuid4()
    p = Performance(
        performance_id=pid, competencia_id=cid, participante_id=part_id, disciplina=Disciplina.STA
    )
    p.registrarAP(Decimal("330"), UnidadMedida.Segundos)
    events = p.pull_events()

    # Simular payload guardado como string (como lo hace SQLite)
    raw = [{"event_type": e.event_type, "payload": _json.dumps(e.to_payload())} for e in events]
    restored = Performance.reconstitute(raw)

    assert restored.estado == EstadoPerformance.AnunciadaAP


def test_reconstitute_con_atleta_llamado_restaura_estado_llamada() -> None:
    """reconstitute con APRegistrado + AtletaLlamado restaura estado Llamada."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.STA,
    )
    p.registrarAP(Decimal("330"), UnidadMedida.Segundos)
    ap_events = p.pull_events()

    p.llamar(OT, posicion_grilla=2)
    llamar_events = p.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap_events + llamar_events
    ]
    restored = Performance.reconstitute(raw)

    assert restored.estado == EstadoPerformance.Llamada


# ── registrar_resultado() — camino feliz ──────────────────────────────────────


@pytest.fixture
def performance_llamada() -> Performance:
    """Performance en estado Llamada, lista para registrar resultado."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    p.registrarAP(Decimal("50"), UnidadMedida.Metros)
    p.pull_events()
    p.llamar(OT, posicion_grilla=1)
    p.pull_events()
    return p


def test_registrar_resultado_emite_evento(performance_llamada: Performance) -> None:
    """registrar_resultado() emite exactamente un evento ResultadoRegistrado."""
    performance_llamada.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")

    events = performance_llamada.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "ResultadoRegistrado"


def test_registrar_resultado_transiciona_a_resultado_registrado(
    performance_llamada: Performance,
) -> None:
    """registrar_resultado() transiciona al estado ResultadoRegistrado."""
    performance_llamada.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")

    assert performance_llamada.estado == EstadoPerformance.ResultadoRegistrado


def test_registrar_resultado_payload_correcto(performance_llamada: Performance) -> None:
    """El evento ResultadoRegistrado contiene valorRP, unidad y registradoPor correctos."""
    valor = Decimal("48.3")
    performance_llamada.registrar_resultado(valor, UnidadMedida.Metros, "juez-007")

    events = performance_llamada.pull_events()
    payload = events[0].to_payload()
    assert payload["valor_rp"] == str(valor)
    assert payload["unidad"] == UnidadMedida.Metros.value
    assert payload["registrado_por"] == "juez-007"


def test_registrar_resultado_persiste_rp_en_aggregate(performance_llamada: Performance) -> None:
    """registrar_resultado() actualiza la propiedad rp del aggregate."""
    valor = Decimal("50.5")
    performance_llamada.registrar_resultado(valor, UnidadMedida.Metros, "juez-001")

    assert performance_llamada.rp == valor


def test_registrar_resultado_pull_events_vacia_lista(performance_llamada: Performance) -> None:
    """pull_events() limpia la lista de eventos pendientes."""
    performance_llamada.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")

    performance_llamada.pull_events()
    assert performance_llamada.pull_events() == []


# ── registrar_resultado() — INV-P-06 ─────────────────────────────────────────


def test_registrar_resultado_desde_anunciada_lanza_excepcion(
    performance: Performance,
) -> None:
    """INV-P-06: registrar_resultado() desde AnunciadaAP lanza EstadoInvalidoParaRegistrarResultado."""
    performance.registrarAP(Decimal("50"), UnidadMedida.Metros)
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaRegistrarResultado):
        performance.registrar_resultado(Decimal("50"), UnidadMedida.Metros, "juez-001")


def test_registrar_resultado_desde_estado_invalido_no_emite_eventos(
    performance: Performance,
) -> None:
    """Si el estado es inválido, no quedan eventos pendientes."""
    performance.registrarAP(Decimal("50"), UnidadMedida.Metros)
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaRegistrarResultado):
        performance.registrar_resultado(Decimal("50"), UnidadMedida.Metros, "juez-001")

    assert performance.pull_events() == []


# ── reconstitute con ResultadoRegistrado ──────────────────────────────────────


def test_reconstitute_con_resultado_registrado_restaura_estado() -> None:
    """reconstitute con AP + Llamado + ResultadoRegistrado restaura estado correcto."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    p.registrarAP(Decimal("50"), UnidadMedida.Metros)
    ap_events = p.pull_events()

    p.llamar(OT, posicion_grilla=1)
    llamar_events = p.pull_events()

    p.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")
    resultado_events = p.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap_events + llamar_events + resultado_events
    ]
    restored = Performance.reconstitute(raw)

    assert restored.estado == EstadoPerformance.ResultadoRegistrado
    assert restored.rp == Decimal("50.5")


# ── asignar_tarjeta() — fixtures ──────────────────────────────────────────────


@pytest.fixture
def performance_con_resultado() -> Performance:
    """Performance en estado ResultadoRegistrado, lista para asignar tarjeta."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    p.registrarAP(Decimal("50"), UnidadMedida.Metros)
    p.pull_events()
    p.llamar(OT, posicion_grilla=1)
    p.pull_events()
    p.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")
    p.pull_events()
    return p


# ── asignar_tarjeta() — camino feliz ──────────────────────────────────────────


def test_asignar_tarjeta_blanca_emite_evento(performance_con_resultado: Performance) -> None:
    """asignar_tarjeta(Blanca) emite exactamente un evento TarjetaAsignada."""
    performance_con_resultado.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")

    events = performance_con_resultado.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "TarjetaAsignada"


def test_asignar_tarjeta_blanca_transiciona_a_ejecutada(
    performance_con_resultado: Performance,
) -> None:
    """asignar_tarjeta(Blanca) transiciona al estado Ejecutada."""
    performance_con_resultado.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")

    assert performance_con_resultado.estado == EstadoPerformance.Ejecutada


def test_asignar_tarjeta_blanca_payload_correcto(performance_con_resultado: Performance) -> None:
    """TarjetaAsignada (Blanca) contiene tipo, motivo=null y asignadaPor correctos."""
    performance_con_resultado.asignar_tarjeta(TipoTarjeta.Blanca, "juez-007")

    events = performance_con_resultado.pull_events()
    payload = events[0].to_payload()
    assert payload["tipo"] == "Blanca"
    assert payload["motivo"] is None
    assert payload["asignada_por"] == "juez-007"


def test_asignar_tarjeta_amarilla_con_motivo(performance_con_resultado: Performance) -> None:
    """asignar_tarjeta(Amarilla, motivo) emite TarjetaAsignada con motivo correcto."""
    performance_con_resultado.asignar_tarjeta(
        TipoTarjeta.Amarilla, "juez-001", motivo="superficie sin protocolo"
    )

    events = performance_con_resultado.pull_events()
    payload = events[0].to_payload()
    assert payload["tipo"] == "Amarilla"
    assert payload["motivo"] == "superficie sin protocolo"
    assert performance_con_resultado.estado == EstadoPerformance.Ejecutada


def test_asignar_tarjeta_roja_con_motivo(performance_con_resultado: Performance) -> None:
    """asignar_tarjeta(Roja, motivo) emite TarjetaAsignada con motivo correcto."""
    performance_con_resultado.asignar_tarjeta(
        TipoTarjeta.Roja, "juez-001", motivo="tiempo excedido"
    )

    events = performance_con_resultado.pull_events()
    payload = events[0].to_payload()
    assert payload["tipo"] == "Roja"
    assert payload["motivo"] == "tiempo excedido"
    assert performance_con_resultado.estado == EstadoPerformance.Ejecutada


def test_asignar_tarjeta_persiste_tarjeta_en_aggregate(
    performance_con_resultado: Performance,
) -> None:
    """asignar_tarjeta() actualiza la propiedad tarjeta del aggregate."""
    performance_con_resultado.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")

    assert performance_con_resultado.tarjeta == TipoTarjeta.Blanca


def test_asignar_tarjeta_pull_events_vacia_lista(performance_con_resultado: Performance) -> None:
    """pull_events() limpia la lista tras asignar tarjeta."""
    performance_con_resultado.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")

    performance_con_resultado.pull_events()
    assert performance_con_resultado.pull_events() == []


# ── asignar_tarjeta() — INV-P-11: motivo obligatorio ─────────────────────────


def test_asignar_tarjeta_amarilla_sin_motivo_lanza_excepcion(
    performance_con_resultado: Performance,
) -> None:
    """INV-P-11: tarjeta Amarilla sin motivo lanza MotivoObligatorio."""
    with pytest.raises(MotivoObligatorio):
        performance_con_resultado.asignar_tarjeta(TipoTarjeta.Amarilla, "juez-001")


def test_asignar_tarjeta_roja_sin_motivo_lanza_excepcion(
    performance_con_resultado: Performance,
) -> None:
    """INV-P-11: tarjeta Roja sin motivo lanza MotivoObligatorio."""
    with pytest.raises(MotivoObligatorio):
        performance_con_resultado.asignar_tarjeta(TipoTarjeta.Roja, "juez-001")


def test_asignar_tarjeta_motivo_obligatorio_no_emite_eventos(
    performance_con_resultado: Performance,
) -> None:
    """Si INV-P-11 falla, no quedan eventos pendientes."""
    with pytest.raises(MotivoObligatorio):
        performance_con_resultado.asignar_tarjeta(TipoTarjeta.Amarilla, "juez-001")

    assert performance_con_resultado.pull_events() == []


# ── asignar_tarjeta() — INV-P-07: estado incorrecto ──────────────────────────


def test_asignar_tarjeta_desde_llamada_lanza_excepcion(performance_llamada: Performance) -> None:
    """INV-P-07: asignar tarjeta desde Llamada lanza EstadoInvalidoParaAsignarTarjeta."""
    with pytest.raises(EstadoInvalidoParaAsignarTarjeta):
        performance_llamada.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")


def test_asignar_tarjeta_estado_invalido_no_emite_eventos(
    performance_llamada: Performance,
) -> None:
    """Si el estado es inválido, no quedan eventos pendientes."""
    with pytest.raises(EstadoInvalidoParaAsignarTarjeta):
        performance_llamada.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")

    assert performance_llamada.pull_events() == []


# ── reconstitute con TarjetaAsignada ─────────────────────────────────────────


def test_reconstitute_con_tarjeta_asignada_restaura_estado() -> None:
    """reconstitute con stream completo restaura estado Ejecutada y tarjeta."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    p.registrarAP(Decimal("50"), UnidadMedida.Metros)
    ap_evs = p.pull_events()

    p.llamar(OT, posicion_grilla=1)
    llamar_evs = p.pull_events()

    p.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")
    res_evs = p.pull_events()

    p.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")
    tarjeta_evs = p.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap_evs + llamar_evs + res_evs + tarjeta_evs
    ]
    restored = Performance.reconstitute(raw)

    assert restored.estado == EstadoPerformance.Ejecutada
    assert restored.tarjeta == TipoTarjeta.Blanca


def test_reconstitute_tarjeta_roja_restaura_tipo() -> None:
    """reconstitute con TarjetaAsignada=Roja restaura el tipo de tarjeta correcto."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    p.registrarAP(Decimal("50"), UnidadMedida.Metros)
    ap_evs = p.pull_events()
    p.llamar(OT, posicion_grilla=1)
    llamar_evs = p.pull_events()
    p.registrar_resultado(Decimal("30"), UnidadMedida.Metros, "juez-001")
    res_evs = p.pull_events()
    p.asignar_tarjeta(TipoTarjeta.Roja, "juez-001", motivo="tiempo excedido")
    tarjeta_evs = p.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap_evs + llamar_evs + res_evs + tarjeta_evs
    ]
    restored = Performance.reconstitute(raw)

    assert restored.tarjeta == TipoTarjeta.Roja
    assert restored.estado == EstadoPerformance.Ejecutada


# ── registrar_dns() — camino feliz ────────────────────────────────────────────


def test_registrar_dns_emite_evento(performance_llamada: Performance) -> None:
    """registrar_dns() emite exactamente un evento DNSRegistrado."""
    performance_llamada.registrar_dns("juez-001")

    events = performance_llamada.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "DNSRegistrado"


def test_registrar_dns_transiciona_a_dns(performance_llamada: Performance) -> None:
    """registrar_dns() transiciona al estado DNS."""
    performance_llamada.registrar_dns("juez-001")

    assert performance_llamada.estado == EstadoPerformance.DNS


def test_registrar_dns_payload_contiene_datos_correctos(
    performance_llamada: Performance,
) -> None:
    """El evento DNSRegistrado contiene registradoPor y ot_programado correctos."""
    performance_llamada.registrar_dns("juez-007")

    events = performance_llamada.pull_events()
    payload = events[0].to_payload()
    assert payload["registrado_por"] == "juez-007"
    assert payload["ot_programado"] == OT.isoformat()


def test_registrar_dns_pull_events_vacia_lista(performance_llamada: Performance) -> None:
    """pull_events() limpia la lista tras registrar DNS."""
    performance_llamada.registrar_dns("juez-001")

    performance_llamada.pull_events()
    assert performance_llamada.pull_events() == []


# ── registrar_dns() — INV-P-08 ────────────────────────────────────────────────


def test_registrar_dns_desde_anunciada_lanza_excepcion(
    performance_anunciada: Performance,
) -> None:
    """INV-P-08: registrar_dns() desde AnunciadaAP lanza EstadoInvalidoParaRegistrarDNS."""
    with pytest.raises(EstadoInvalidoParaRegistrarDNS):
        performance_anunciada.registrar_dns("juez-001")


def test_registrar_dns_desde_resultado_registrado_lanza_excepcion(
    performance_llamada: Performance,
) -> None:
    """INV-P-09: registrar_dns() desde ResultadoRegistrado lanza EstadoInvalidoParaRegistrarDNS."""
    performance_llamada.registrar_resultado(Decimal("50.5"), UnidadMedida.Metros, "juez-001")
    performance_llamada.pull_events()

    with pytest.raises(EstadoInvalidoParaRegistrarDNS):
        performance_llamada.registrar_dns("juez-001")


def test_registrar_dns_estado_invalido_no_emite_eventos(
    performance_anunciada: Performance,
) -> None:
    """Si el estado es inválido, no quedan eventos pendientes."""
    with pytest.raises(EstadoInvalidoParaRegistrarDNS):
        performance_anunciada.registrar_dns("juez-001")

    assert performance_anunciada.pull_events() == []


# ── reconstitute con DNSRegistrado ───────────────────────────────────────────


def test_reconstitute_con_dns_registrado_restaura_estado() -> None:
    """reconstitute con AP + Llamado + DNS restaura estado DNS."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.DNF,
    )
    p.registrarAP(Decimal("50"), UnidadMedida.Metros)
    ap_evs = p.pull_events()
    p.llamar(OT, posicion_grilla=1)
    llamar_evs = p.pull_events()
    p.registrar_dns("juez-001")
    dns_evs = p.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap_evs + llamar_evs + dns_evs
    ]
    restored = Performance.reconstitute(raw)

    assert restored.estado == EstadoPerformance.DNS


# ── Fixtures para corregir_resultado ─────────────────────────────────────────


@pytest.fixture
def performance_ejecutada() -> Performance:
    """Performance en estado Ejecutada (AP + Llamada + Resultado + Tarjeta Blanca)."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.STA,
    )
    p.registrarAP(Decimal("90"), UnidadMedida.Metros)
    p.pull_events()
    p.llamar(OT, posicion_grilla=1)
    p.pull_events()
    p.registrar_resultado(Decimal("89.5"), UnidadMedida.Metros, "juez-001")
    p.pull_events()
    p.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")
    p.pull_events()
    return p


# ── corregir_resultado — camino feliz ─────────────────────────────────────────


def test_corregir_resultado_emite_evento(performance_ejecutada: Performance) -> None:
    """corregir_resultado() emite exactamente un evento ResultadoCorregido."""
    performance_ejecutada.corregir_resultado(
        Decimal("90.0"), UnidadMedida.Metros, "juez-001", "Error de lectura"
    )

    events = performance_ejecutada.pull_events()
    assert len(events) == 1
    assert events[0].event_type == "ResultadoCorregido"


def test_corregir_resultado_actualiza_rp(performance_ejecutada: Performance) -> None:
    """corregir_resultado() actualiza self._rp al nuevo valor."""
    performance_ejecutada.corregir_resultado(
        Decimal("90.0"), UnidadMedida.Metros, "juez-001", "Error de lectura"
    )

    assert performance_ejecutada.rp == Decimal("90.0")


def test_corregir_resultado_estado_permanece_ejecutada(
    performance_ejecutada: Performance,
) -> None:
    """corregir_resultado() no cambia el estado — permanece Ejecutada."""
    performance_ejecutada.corregir_resultado(
        Decimal("90.0"), UnidadMedida.Metros, "juez-001", "Error de lectura"
    )
    performance_ejecutada.pull_events()

    assert performance_ejecutada.estado == EstadoPerformance.Ejecutada


def test_corregir_resultado_payload_correcto(performance_ejecutada: Performance) -> None:
    """El payload de ResultadoCorregido contiene valor anterior, nuevo, motivo y juez."""
    performance_ejecutada.corregir_resultado(
        Decimal("90.0"), UnidadMedida.Metros, "juez-007", "Corrección de planilla"
    )

    event = performance_ejecutada.pull_events()[0]
    payload = event.to_payload()
    assert payload["valor_rp_anterior"] == "89.5"
    assert payload["valor_rp_nuevo"] == "90.0"
    assert payload["motivo"] == "Corrección de planilla"
    assert payload["registrado_por"] == "juez-007"


# ── corregir_resultado — INV-P-12/13 ─────────────────────────────────────────


def test_corregir_resultado_desde_anunciada_lanza_excepcion(
    performance: Performance,
) -> None:
    """INV-P-12: corregir_resultado() desde estado inicial lanza EstadoInvalidoParaCorregirResultado."""
    performance.registrarAP(Decimal("90"), UnidadMedida.Metros)
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        performance.corregir_resultado(
            Decimal("90.0"), UnidadMedida.Metros, "juez-001", "motivo"
        )


def test_corregir_resultado_desde_llamada_lanza_excepcion(
    performance: Performance,
) -> None:
    """INV-P-12: corregir_resultado() desde Llamada lanza EstadoInvalidoParaCorregirResultado."""
    performance.registrarAP(Decimal("90"), UnidadMedida.Metros)
    performance.pull_events()
    performance.llamar(OT, posicion_grilla=1)
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        performance.corregir_resultado(
            Decimal("90.0"), UnidadMedida.Metros, "juez-001", "motivo"
        )


def test_corregir_resultado_desde_dns_lanza_excepcion(
    performance: Performance,
) -> None:
    """INV-P-13: corregir_resultado() desde DNS lanza EstadoInvalidoParaCorregirResultado."""
    performance.registrarAP(Decimal("90"), UnidadMedida.Metros)
    performance.pull_events()
    performance.llamar(OT, posicion_grilla=1)
    performance.pull_events()
    performance.registrar_dns("juez-001")
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        performance.corregir_resultado(
            Decimal("90.0"), UnidadMedida.Metros, "juez-001", "motivo"
        )


def test_corregir_resultado_sin_motivo_lanza_excepcion(
    performance_ejecutada: Performance,
) -> None:
    """INV-P-12: motivo ausente lanza MotivoObligatorio."""
    with pytest.raises(MotivoObligatorio):
        performance_ejecutada.corregir_resultado(
            Decimal("90.0"), UnidadMedida.Metros, "juez-001", ""
        )


def test_corregir_resultado_estado_invalido_no_emite_eventos(
    performance: Performance,
) -> None:
    """Si el estado es inválido, no quedan eventos pendientes."""
    performance.registrarAP(Decimal("90"), UnidadMedida.Metros)
    performance.pull_events()

    with pytest.raises(EstadoInvalidoParaCorregirResultado):
        performance.corregir_resultado(
            Decimal("90.0"), UnidadMedida.Metros, "juez-001", "motivo"
        )

    assert performance.pull_events() == []


# ── reconstitute con ResultadoCorregido ──────────────────────────────────────


def test_reconstitute_con_resultado_corregido_restaura_rp() -> None:
    """reconstitute con AP + Llamada + Resultado + Tarjeta + Corrección restaura RP corregido."""
    p = Performance(
        performance_id=uuid4(),
        competencia_id=uuid4(),
        participante_id=uuid4(),
        disciplina=Disciplina.STA,
    )
    p.registrarAP(Decimal("90"), UnidadMedida.Metros)
    ap_evs = p.pull_events()
    p.llamar(OT, posicion_grilla=1)
    llamar_evs = p.pull_events()
    p.registrar_resultado(Decimal("89.5"), UnidadMedida.Metros, "juez-001")
    resultado_evs = p.pull_events()
    p.asignar_tarjeta(TipoTarjeta.Blanca, "juez-001")
    tarjeta_evs = p.pull_events()
    p.corregir_resultado(Decimal("90.0"), UnidadMedida.Metros, "juez-001", "Error de planilla")
    correccion_evs = p.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap_evs + llamar_evs + resultado_evs + tarjeta_evs + correccion_evs
    ]
    restored = Performance.reconstitute(raw)

    assert restored.estado == EstadoPerformance.Ejecutada
    assert restored.rp == Decimal("90.0")


# ── US-1.4.1: asignar_tarjeta() — black-out con distancia ────────────────────


def test_blackout_con_distancia_valida_emite_evento(
    performance_con_resultado: Performance,
) -> None:
    """Black-out con distancia válida emite TarjetaAsignada con distancia_blackout."""
    performance_con_resultado.asignar_tarjeta(
        TipoTarjeta.Roja, "juez-001", motivo="black-out", distancia_blackout=Decimal("45.5")
    )
    events = performance_con_resultado.pull_events()
    assert len(events) == 1
    payload = events[0].to_payload()
    assert payload["distancia_blackout"] == "45.5"
    assert payload["motivo"] == "black-out"
    assert payload["tipo"] == TipoTarjeta.Roja.value


def test_blackout_con_distancia_valida_estado_ejecutada(
    performance_con_resultado: Performance,
) -> None:
    """Black-out con distancia válida transiciona a Ejecutada."""
    performance_con_resultado.asignar_tarjeta(
        TipoTarjeta.Roja, "juez-001", motivo="black-out", distancia_blackout=Decimal("45.5")
    )
    assert performance_con_resultado.estado == EstadoPerformance.Ejecutada
    assert performance_con_resultado.distancia_blackout == Decimal("45.5")


def test_blackout_sin_distancia_lanza_excepcion(
    performance_con_resultado: Performance,
) -> None:
    """Black-out sin distancia_blackout lanza DistanciaBlackoutObligatoria (RF-EJ-07)."""
    with pytest.raises(DistanciaBlackoutObligatoria):
        performance_con_resultado.asignar_tarjeta(
            TipoTarjeta.Roja, "juez-001", motivo="black-out"
        )


def test_blackout_con_distancia_cero_lanza_excepcion(
    performance_con_resultado: Performance,
) -> None:
    """Black-out con distancia_blackout=0 lanza DistanciaBlackoutObligatoria (RF-EJ-07)."""
    with pytest.raises(DistanciaBlackoutObligatoria):
        performance_con_resultado.asignar_tarjeta(
            TipoTarjeta.Roja, "juez-001", motivo="black-out", distancia_blackout=Decimal("0")
        )


def test_blackout_no_emite_eventos_si_falla(
    performance_con_resultado: Performance,
) -> None:
    """Black-out inválido no emite eventos."""
    with pytest.raises(DistanciaBlackoutObligatoria):
        performance_con_resultado.asignar_tarjeta(
            TipoTarjeta.Roja, "juez-001", motivo="black-out"
        )
    assert performance_con_resultado.pull_events() == []


def test_tarjeta_roja_sin_blackout_sigue_funcionando(
    performance_con_resultado: Performance,
) -> None:
    """Tarjeta roja con motivo distinto a black-out funciona sin distancia (regresión)."""
    performance_con_resultado.asignar_tarjeta(
        TipoTarjeta.Roja, "juez-001", motivo="tiempo excedido"
    )
    events = performance_con_resultado.pull_events()
    assert len(events) == 1
    payload = events[0].to_payload()
    assert payload["distancia_blackout"] is None


def test_reconstitute_con_blackout_restaura_distancia(
    performance_con_resultado: Performance,
) -> None:
    """reconstitute restaura distancia_blackout desde el payload del evento."""
    performance_con_resultado.asignar_tarjeta(
        TipoTarjeta.Roja, "juez-001", motivo="black-out", distancia_blackout=Decimal("38.2")
    )
    ap_evs = performance_con_resultado._events[:-1] if hasattr(performance_con_resultado, '_events') else []
    tarjeta_evs = performance_con_resultado.pull_events()

    # Reconstituir desde cero usando reconstitute
    p2 = Performance(
        performance_id=performance_con_resultado.performance_id,
        competencia_id=uuid4(),
        participante_id=performance_con_resultado.participante_id,
        disciplina=Disciplina.STA,
    )
    p2.registrarAP(Decimal("90"), UnidadMedida.Metros)
    ap = p2.pull_events()
    p2.llamar(OT, posicion_grilla=1)
    llamar = p2.pull_events()
    p2.registrar_resultado(Decimal("38.2"), UnidadMedida.Metros, "juez-001")
    resultado = p2.pull_events()
    p2.asignar_tarjeta(
        TipoTarjeta.Roja, "juez-001", motivo="black-out", distancia_blackout=Decimal("38.2")
    )
    tarjeta = p2.pull_events()

    raw = [
        {"event_type": e.event_type, "payload": e.to_payload()}
        for e in ap + llamar + resultado + tarjeta
    ]
    restored = Performance.reconstitute(raw)
    assert restored.distancia_blackout == Decimal("38.2")
    assert restored.estado == EstadoPerformance.Ejecutada
