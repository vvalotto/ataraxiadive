"""Value Object EntradaGrilla — una fila de la Grilla de Salida."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class EntradaGrilla:
    """Representa la asignación de un atleta en la Grilla de Salida.

    Inmutable. Contiene la posición, andarivel y OT programado calculados
    para una Performance específica dentro de una competencia.

    Attributes:
        performance_id: Identificador de la Performance.
        atleta_id: Identificador del atleta.
        posicion: Número de orden en la grilla (1-based).
        andarivel: Carril asignado al atleta (1-based).
        ot_programado: Timestamp calculado del Official Top.
    """

    performance_id: UUID
    atleta_id: UUID
    posicion: int
    andarivel: int
    ot_programado: datetime
