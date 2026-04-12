"""Value Object TarjetaAsignacion — valida la asignacion de tarjetas."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal

from competencia.domain.exceptions import (
    DisciplinaNoAdmitePenalizaciones,
    DistanciaBlackoutNoAplica,
    DistanciaBlackoutObligatoria,
    MotivoDQObligatorio,
    MotivoObligatorio,
    PenalizacionesObligatorias,
)
from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta


@dataclass(frozen=True)
class TarjetaAsignacion:
    """Encapsula tipo, motivo y distancia de blackout como un solo concepto."""

    tipo: TipoTarjeta
    motivo_dq: MotivoDQ | None
    motivo_texto: str | None
    distancia_blackout: Decimal | None
    penalizaciones: tuple[PenalizacionTecnica, ...] = ()
    es_disciplina_tiempo: bool = False

    def __post_init__(self) -> None:
        self._validar_penalizaciones()
        self._validar_motivos()
        self._validar_distancia_blackout()

    def _validar_penalizaciones(self) -> None:
        if self.tipo == TipoTarjeta.BlancaConPenalizaciones and not self.penalizaciones:
            raise PenalizacionesObligatorias(
                "Tarjeta BlancaConPenalizaciones requiere al menos una penalizacion"
            )
        if self.tipo != TipoTarjeta.BlancaConPenalizaciones and self.penalizaciones:
            raise DisciplinaNoAdmitePenalizaciones(
                f"Tarjeta {self.tipo.value} no acepta penalizaciones tecnicas"
            )

    def _validar_motivos(self) -> None:
        if self.tipo == TipoTarjeta.Amarilla and not self.motivo_texto:
            raise MotivoObligatorio(
                f"Tarjeta {self.tipo.value} requiere motivo en texto obligatorio (INV-P-11b)"
            )
        if self.tipo == TipoTarjeta.Roja and self.motivo_dq is None:
            raise MotivoDQObligatorio(
                f"Tarjeta {self.tipo.value} requiere MotivoDQ obligatorio (INV-P-11)"
            )
        if self.tipo != TipoTarjeta.Amarilla and self.motivo_texto:
            raise MotivoDQObligatorio(
                f"Tarjeta {self.tipo.value} no acepta motivo_texto en nuevas asignaciones"
            )

    def _validar_distancia_blackout(self) -> None:
        if self.motivo_dq is not None and self.motivo_dq.requiere_distancia_blackout():
            # En disciplinas de tiempo (STA) no hay desplazamiento: distancia_blackout no aplica
            if not self.es_disciplina_tiempo:
                if self.distancia_blackout is None or self.distancia_blackout <= 0:
                    raise DistanciaBlackoutObligatoria(
                        "Tarjeta roja por blackout requiere distancia_blackout > 0 (INV-DQ-01)"
                    )
            return
        if self.distancia_blackout is not None:
            raise DistanciaBlackoutNoAplica(
                "distancia_blackout solo aplica a motivos BKO (INV-DQ-02)"
            )
