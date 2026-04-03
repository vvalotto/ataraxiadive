"""Value Object TarjetaAsignacion — valida la asignacion de tarjetas."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from competencia.domain.exceptions import DistanciaBlackoutObligatoria, MotivoObligatorio
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta


@dataclass(frozen=True)
class TarjetaAsignacion:
    """Encapsula tipo, motivo y distancia de blackout como un solo concepto."""

    tipo: TipoTarjeta
    motivo: str | None
    distancia_blackout: Decimal | None

    def __post_init__(self) -> None:
        if self.tipo in (TipoTarjeta.Amarilla, TipoTarjeta.Roja) and not self.motivo:
            raise MotivoObligatorio(
                f"Tarjeta {self.tipo.value} requiere motivo obligatorio (INV-P-11)"
            )

        if self.motivo == "black-out" and (
            self.distancia_blackout is None or self.distancia_blackout <= 0
        ):
            raise DistanciaBlackoutObligatoria(
                "Tarjeta roja por black-out requiere distancia_blackout > 0 (RF-EJ-07)"
            )
