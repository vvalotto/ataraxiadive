"""Puerto AndarivelesActivosPort — consulta del estado de andariveles en ejecución."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from competencia.domain.value_objects.disciplina import Disciplina


@dataclass(frozen=True)
class AndarivelesActivosData:
    """DTO con el estado de un andarivel en un instante dado.

    Attributes:
        numero: Número de andarivel (1, 2, 3, ...).
        ocupado: True si hay una Performance en estado Llamada en este andarivel.
        atleta_id: Identificador del atleta activo, None si libre.
        performance_id: Identificador de la Performance activa, None si libre.
        ot_programado: OT programado del atleta activo, None si libre.
    """

    numero: int
    ocupado: bool
    atleta_id: UUID | None
    performance_id: UUID | None
    ot_programado: datetime | None


class AndarivelesActivosPort(ABC):
    """Puerto para consultar el estado de andariveles durante la ejecución.

    La implementación concreta (AndarivelesActivosAdapter) lee los streams
    performance-{competencia_id}-* del Event Store, reconstituye cada
    Performance y proyecta el estado de cada andarivel.

    Requerido por:
        LlamarAtletaHandler: verificación de INV-C-05 (conflicto de andarivel).
        ObtenerAndarivelesActivosHandler: endpoint READ de andariveles.
    """

    @abstractmethod
    async def get_andariveles_activos(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        andariveles: int,
    ) -> list[AndarivelesActivosData]:
        """Retorna el estado de cada andarivel para la competencia y disciplina.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina en ejecución.
            andariveles: Número total de andariveles configurados en la grilla.

        Returns:
            Lista de AndarivelesActivosData con un elemento por andarivel (1..N).
        """

    @abstractmethod
    async def is_andarivel_activo(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
        numero_andarivel: int,
    ) -> bool:
        """Indica si el andarivel tiene una Performance en estado Llamada.

        Usado por LlamarAtletaHandler para verificar INV-C-05 antes de llamar.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina en ejecución.
            numero_andarivel: Número de andarivel a verificar.

        Returns:
            True si el andarivel está ocupado (Performance en Llamada).
        """
