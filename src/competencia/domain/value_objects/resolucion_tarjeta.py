"""Value Object ResolucionTarjeta — resultado derivado de una asignacion de tarjeta."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any

from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica
from competencia.domain.value_objects.rp_final import RPFinal
from competencia.domain.value_objects.tarjeta_asignacion import TarjetaAsignacion
from competencia.domain.value_objects.tipo_penalizacion import TipoPenalizacion
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta


@dataclass(frozen=True)
class ResolucionTarjeta:
    """Agrupa el estado derivado de una tarjeta ya validada."""

    tipo: TipoTarjeta
    motivo_dq: MotivoDQ | None
    motivo_texto: str | None
    distancia_blackout: Decimal | None
    penalizaciones: tuple[PenalizacionTecnica, ...]
    rp_final: RPFinal

    @classmethod
    def desde_asignacion(
        cls, asignacion: TarjetaAsignacion, rp_medido: Decimal | None
    ) -> "ResolucionTarjeta":
        """Resuelve tarjeta y RP final desde la asignacion validada."""
        return cls(
            tipo=asignacion.tipo,
            motivo_dq=asignacion.motivo_dq,
            motivo_texto=asignacion.motivo_texto,
            distancia_blackout=asignacion.distancia_blackout,
            penalizaciones=asignacion.penalizaciones,
            rp_final=RPFinal.desde_medicion(rp_medido, asignacion.penalizaciones),
        )

    @classmethod
    def desde_payload(cls, payload: dict[str, Any]) -> "ResolucionTarjeta":
        """Reconstituye la resolucion desde payload nuevo o legacy."""
        motivo_dq = cls._restaurar_motivo_dq(payload)
        motivo_texto = payload.get("motivo_texto")
        if motivo_dq is None and isinstance(payload.get("motivo"), str):
            motivo_texto = payload["motivo"]

        penalizaciones = tuple(
            PenalizacionTecnica(
                tipo=TipoPenalizacion(item["tipo"]),
                deduccion=Decimal(item["deduccion"]),
            )
            for item in payload.get("penalizaciones", [])
        )

        distancia_blackout = (
            Decimal(payload["distancia_blackout"])
            if payload.get("distancia_blackout") is not None
            else None
        )
        rp_medido = Decimal(payload["rp_medido"]) if payload.get("rp_medido") is not None else None
        rp_penalizado = (
            Decimal(payload["rp_penalizado"])
            if payload.get("rp_penalizado") is not None
            else None
        )

        return cls(
            tipo=TipoTarjeta(payload["tipo"]),
            motivo_dq=motivo_dq,
            motivo_texto=motivo_texto,
            distancia_blackout=distancia_blackout,
            penalizaciones=penalizaciones,
            rp_final=RPFinal(medido=rp_medido, penalizado=rp_penalizado),
        )

    def to_event_payload(self, *, asignada_por: str, asignada_en: str) -> dict[str, Any]:
        """Serializa el payload de TarjetaAsignada preservando el contrato actual."""
        return {
            "tipo": self.tipo.value,
            "motivo_dq_codigo": self.motivo_dq.value if self.motivo_dq else None,
            "motivo_texto": self.motivo_texto,
            "asignada_por": asignada_por,
            "asignada_en": asignada_en,
            "distancia_blackout": (
                str(self.distancia_blackout) if self.distancia_blackout is not None else None
            ),
            "penalizaciones": tuple(item.to_payload() for item in self.penalizaciones),
            "rp_medido": str(self.rp_final.medido) if self.rp_final.medido is not None else None,
            "rp_penalizado": (
                str(self.rp_final.penalizado) if self.rp_final.penalizado is not None else None
            ),
        }

    @property
    def rp_observable(self) -> Decimal | None:
        """RP final que debe reflejar el aggregate."""
        return self.rp_final.observable

    @staticmethod
    def _restaurar_motivo_dq(payload: dict[str, Any]) -> MotivoDQ | None:
        motivo_dq_codigo = payload.get("motivo_dq_codigo")
        legacy_motivo = payload.get("motivo")
        if motivo_dq_codigo:
            return MotivoDQ(motivo_dq_codigo)
        if legacy_motivo == "black-out":
            return MotivoDQ.BKO_SUPERFICIE
        return None
