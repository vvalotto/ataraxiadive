"""Value Object EntradaOverall — una línea del ranking general del torneo."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria


@dataclass(frozen=True)
class EntradaOverall:
    """Una entrada en el ranking overall del torneo.

    Attributes:
        posicion: Posición overall (1-based). Empates comparten posición.
        atleta_id: Identificador del atleta.
        categoria: Categoría competitiva del atleta.
        puntos_overall: Suma de puntos FAAS de todas las disciplinas (INV-5.6.4-01).
        detalle: Mapa disciplina → puntos FAAS aportados.
        en_podio: True si la posición overall está en el podio.
    """

    posicion: int
    atleta_id: UUID
    categoria: Categoria
    puntos_overall: Decimal
    detalle: dict[str, Decimal]
    en_podio: bool
