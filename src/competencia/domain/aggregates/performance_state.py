"""Helpers de reconstitucion y aplicacion de eventos para Performance."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import Any

from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.resolucion_tarjeta import ResolucionTarjeta
from competencia.domain.value_objects.rp_final import RPFinal
from competencia.domain.value_objects.unidad_medida import UnidadMedida


def apply_stored(performance: Any, event: dict[str, Any]) -> None:
    """Aplica un evento almacenado al estado interno del aggregate."""
    payload = parse_payload(event["payload"])
    handlers = {
        "APRegistrado": apply_ap_registrado,
        "AtletaLlamado": apply_atleta_llamado,
        "ResultadoRegistrado": apply_resultado_registrado,
        "DNSRegistrado": apply_dns_registrado,
        "TarjetaAsignada": apply_tarjeta_asignada,
        "RevisionResuelta": apply_revision_resuelta,
        "ResultadoCorregido": apply_resultado_corregido,
        "ResultadoCorregidoTrasDNS": apply_resultado_corregido_tras_dns,
    }
    handler = handlers.get(event["event_type"])
    if handler is not None:
        handler(performance, payload)


def apply_ap_registrado(performance: Any, payload: dict[str, Any]) -> None:
    performance._ap = AP(
        valor=Decimal(payload["valor_ap"]),
        unidad=UnidadMedida(payload["unidad"]),
    )
    performance._estado = EstadoPerformance.AnunciadaAP


def apply_atleta_llamado(performance: Any, payload: dict[str, Any]) -> None:
    performance._estado = EstadoPerformance.Llamada
    performance._ot_programado = datetime.fromisoformat(payload["ot_programado"])
    performance._posicion_grilla = payload["posicion_grilla"]
    performance._andarivel = payload.get("andarivel", 1)


def apply_resultado_registrado(performance: Any, payload: dict[str, Any]) -> None:
    performance._aplicar_rp_final(RPFinal.desde_medicion(Decimal(payload["valor_rp"])))
    performance._estado = EstadoPerformance.ResultadoRegistrado


def apply_dns_registrado(performance: Any, _payload: dict[str, Any]) -> None:
    performance._estado = EstadoPerformance.DNS


def apply_tarjeta_asignada(performance: Any, payload: dict[str, Any]) -> None:
    resolucion = ResolucionTarjeta.desde_payload(payload)
    if payload.get("tipo") == "Amarilla":
        performance._tarjeta = resolucion.tipo
        performance._motivo_dq = resolucion.motivo_dq
        performance._motivo_texto = resolucion.motivo_texto
        performance._distancia_blackout = resolucion.distancia_blackout
        performance._penalizaciones = resolucion.penalizaciones
        performance._estado = EstadoPerformance.EnRevision
        performance._aplicar_rp_final(resolucion.rp_final)
        return
    performance._aplicar_resolucion_tarjeta(resolucion)


def apply_revision_resuelta(performance: Any, payload: dict[str, Any]) -> None:
    performance._aplicar_resolucion_tarjeta(ResolucionTarjeta.desde_payload(payload))


def apply_resultado_corregido(performance: Any, payload: dict[str, Any]) -> None:
    performance._aplicar_rp_final(
        RPFinal.desde_medicion(Decimal(payload["valor_rp_nuevo"]), performance._penalizaciones)
    )


def apply_resultado_corregido_tras_dns(performance: Any, payload: dict[str, Any]) -> None:
    performance._aplicar_rp_final(RPFinal.desde_medicion(Decimal(payload["valor_rp"])))
    performance._estado = EstadoPerformance.ResultadoRegistrado


def parse_payload(payload: Any) -> dict[str, Any]:
    """Parsea el payload del Event Store (puede ser str JSON o dict)."""
    if isinstance(payload, str):
        return json.loads(payload)  # type: ignore[no-any-return]
    return payload  # type: ignore[return-value]
