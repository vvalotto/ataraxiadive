"""Value Object EntradaOverall — una línea del ranking general del torneo."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from registro.domain.value_objects.categoria import Categoria


@dataclass(frozen=True)
class EntradaOverall:
    """Una entrada en el ranking overall del torneo.

    Attributes:
        posicion: Posición overall (1-based). Empates comparten posición.
        atleta_id: Identificador del atleta.
        categoria: Categoría competitiva del atleta.
        puntaje: Suma de posiciones por disciplina (menor es mejor).
        detalle: Mapa disciplina -> posición utilizada en la suma.
        en_podio: True si la posición overall está en el podio.
    """

    posicion: int
    atleta_id: UUID
    categoria: Categoria
    puntaje: int
    detalle: dict[str, int]
    en_podio: bool
