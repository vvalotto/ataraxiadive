"""Helpers de reconstitucion y aplicacion de eventos para Performance."""

from __future__ import annotations

import json
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Any
from uuid import UUID

from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.resolucion_tarjeta import ResolucionTarjeta
from competencia.domain.value_objects.rp_final import RPFinal
from competencia.domain.value_objects.unidad_medida import UnidadMedida

if TYPE_CHECKING:
    from competencia.domain.aggregates.performance import Performance


def reconstituir_performance(events: list[dict[str, Any]]) -> "Performance":
    """Reconstruye Performance desde su stream de eventos."""
    if not events:
        raise ValueError("No se puede reconstituir Performance sin eventos")

    first_payload = parse_payload(events[0]["payload"])
    if events[0]["event_type"] != "APRegistrado":
        raise ValueError(
            f"El primer evento debe ser APRegistrado, recibido: {events[0]['event_type']}"
        )

    from competencia.domain.aggregates.performance import Performance

    performance = Performance(
        performance_id=UUID(first_payload["performance_id"]),
        competencia_id=UUID(first_payload["competencia_id"]),
        participante_id=UUID(first_payload["participante_id"]),
        disciplina=Disciplina(first_payload["disciplina"]),
    )

    for event in events:
        apply_stored(performance, event)

    return performance


def apply_stored(performance: "Performance", event: dict[str, Any]) -> None:
    """Aplica un evento almacenado al estado interno del aggregate."""
    payload = parse_payload(event["payload"])
    handlers = {
        "APRegistrado": apply_ap_registrado,
        "AtletaLlamado": apply_atleta_llamado,
        "ResultadoRegistrado": apply_resultado_registrado,
        "DNSRegistrado": apply_dns_registrado,
        "TarjetaAsignada": apply_tarjeta_asignada,
        "ResultadoCorregido": apply_resultado_corregido,
    }
    handler = handlers.get(event["event_type"])
    if handler is not None:
        handler(performance, payload)


def apply_ap_registrado(performance: "Performance", payload: dict[str, Any]) -> None:
    performance._ap = AP(
        valor=Decimal(payload["valor_ap"]),
        unidad=UnidadMedida(payload["unidad"]),
    )
    performance._estado = EstadoPerformance.AnunciadaAP


def apply_atleta_llamado(performance: "Performance", payload: dict[str, Any]) -> None:
    performance._estado = EstadoPerformance.Llamada
    performance._ot_programado = datetime.fromisoformat(payload["ot_programado"])
    performance._posicion_grilla = payload["posicion_grilla"]
    performance._andarivel = payload.get("andarivel", 1)


def apply_resultado_registrado(performance: "Performance", payload: dict[str, Any]) -> None:
    performance._aplicar_rp_final(RPFinal.desde_medicion(Decimal(payload["valor_rp"])))
    performance._estado = EstadoPerformance.ResultadoRegistrado


def apply_dns_registrado(performance: "Performance", _payload: dict[str, Any]) -> None:
    performance._estado = EstadoPerformance.DNS


def apply_tarjeta_asignada(performance: "Performance", payload: dict[str, Any]) -> None:
    performance._aplicar_resolucion_tarjeta(ResolucionTarjeta.desde_payload(payload))


def apply_resultado_corregido(performance: "Performance", payload: dict[str, Any]) -> None:
    performance._aplicar_rp_final(
        RPFinal.desde_medicion(Decimal(payload["valor_rp_nuevo"]), performance._penalizaciones)
    )


def parse_payload(payload: Any) -> dict[str, Any]:
    """Parsea el payload del Event Store (puede ser str JSON o dict)."""
    if isinstance(payload, str):
        return json.loads(payload)  # type: ignore[no-any-return]
    return payload  # type: ignore[return-value]
