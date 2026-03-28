"""Value Object EntradaRanking — una línea del ranking de la disciplina."""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True)
class EntradaRanking:
    """Una entrada en el ranking de la disciplina.

    Attributes:
        posicion: Posición en el ranking (1-based). Comparten posición en empate.
        atleta_id: Identificador del participante.
        rp: Marca efectiva registrada. None para DNS y tarjeta roja.
        unidad: Unidad de medida del RP ("Segundos", "Metros"). None si no hay RP.
        tarjeta: Tipo de tarjeta asignada ("Blanca", "Amarilla", "Roja"). None para DNS.
        es_dns: True si el atleta no se presentó (Did Not Start).
        en_podio: True si la posición está en el podio (pos 1, 2 o 3).
    """

    posicion: int
    atleta_id: UUID
    rp: Decimal | None
    unidad: str | None
    tarjeta: str | None
    es_dns: bool
    en_podio: bool
