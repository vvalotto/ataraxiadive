"""Factories de eventos de dominio para Performance."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from competencia.domain.events.ap_registrado import APRegistrado
from competencia.domain.events.atleta_llamado import AtletaLlamado
from competencia.domain.events.dns_registrado import DNSRegistrado
from competencia.domain.events.resultado_corregido import ResultadoCorregido
from competencia.domain.events.resultado_corregido_tras_dns import ResultadoCorregidoTrasDNS
from competencia.domain.events.resultado_registrado import ResultadoRegistrado
from competencia.domain.events.revision_resuelta import RevisionResuelta
from competencia.domain.events.tarjeta_asignada import TarjetaAsignada
from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.resolucion_tarjeta import ResolucionTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida


def crear_ap_registrado(
    *,
    performance_id: UUID,
    competencia_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    ap: AP,
) -> APRegistrado:
    return APRegistrado(
        event_type="APRegistrado",
        aggregate_id=str(performance_id),
        occurred_at=APRegistrado.now(),
        performance_id=str(performance_id),
        competencia_id=str(competencia_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        valor_ap=str(ap.valor),
        unidad=ap.unidad.value,
    )


def crear_atleta_llamado(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    ot_programado: datetime,
    posicion_grilla: int,
    andarivel: int,
) -> AtletaLlamado:
    now = AtletaLlamado.now()
    return AtletaLlamado(
        event_type="AtletaLlamado",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        posicion_grilla=posicion_grilla,
        ot_programado=ot_programado.isoformat(),
        llamado_en=now.isoformat(),
        andarivel=andarivel,
    )


def crear_resultado_registrado(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    valor_rp: Decimal,
    unidad: UnidadMedida,
    registrado_por: str,
) -> ResultadoRegistrado:
    now = ResultadoRegistrado.now()
    return ResultadoRegistrado(
        event_type="ResultadoRegistrado",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        valor_rp=str(valor_rp),
        unidad=unidad.value,
        registrado_por=registrado_por,
        registrado_en=now.isoformat(),
    )


def crear_dns_registrado(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    ot_programado: datetime | None,
    registrado_por: str,
) -> DNSRegistrado:
    now = DNSRegistrado.now()
    return DNSRegistrado(
        event_type="DNSRegistrado",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        ot_programado=ot_programado.isoformat() if ot_programado else "",
        registrado_por=registrado_por,
        registrado_en=now.isoformat(),
    )


def crear_resultado_corregido(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    valor_rp_anterior: Decimal | None,
    valor_rp_nuevo: Decimal,
    unidad: UnidadMedida,
    motivo: str,
    registrado_por: str,
) -> ResultadoCorregido:
    now = ResultadoCorregido.now()
    return ResultadoCorregido(
        event_type="ResultadoCorregido",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        valor_rp_anterior=str(valor_rp_anterior) if valor_rp_anterior is not None else "",
        valor_rp_nuevo=str(valor_rp_nuevo),
        unidad=unidad.value,
        motivo=motivo,
        registrado_por=registrado_por,
        corregido_en=now.isoformat(),
    )


def crear_resultado_corregido_tras_dns(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    valor_rp: Decimal,
    unidad: UnidadMedida,
    registrado_por: str,
    motivo_correccion: str,
) -> ResultadoCorregidoTrasDNS:
    now = ResultadoCorregidoTrasDNS.now()
    return ResultadoCorregidoTrasDNS(
        event_type="ResultadoCorregidoTrasDNS",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        valor_rp=str(valor_rp),
        unidad=unidad.value,
        registrado_por=registrado_por,
        motivo_correccion=motivo_correccion,
        corregido_en=now.isoformat(),
    )


def crear_tarjeta_asignada(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    resolucion: ResolucionTarjeta,
    asignada_por: str,
) -> TarjetaAsignada:
    now = TarjetaAsignada.now()
    return TarjetaAsignada(
        event_type="TarjetaAsignada",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        **resolucion.to_event_payload(
            asignada_por=asignada_por,
            asignada_en=now.isoformat(),
        ),
    )


def crear_revision_resuelta(
    *,
    performance_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
    resolucion: ResolucionTarjeta,
    resuelta_por: str,
) -> RevisionResuelta:
    now = RevisionResuelta.now()
    return RevisionResuelta(
        event_type="RevisionResuelta",
        aggregate_id=str(performance_id),
        occurred_at=now,
        performance_id=str(performance_id),
        participante_id=str(participante_id),
        disciplina=disciplina.value,
        **resolucion.to_event_payload(
            asignada_por=resuelta_por,
            asignada_en=now.isoformat(),
        ),
    )
