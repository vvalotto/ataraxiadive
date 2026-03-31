from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from uuid import UUID, uuid4

from registro.domain.exceptions import PlazoCancelacionVencido
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina


@dataclass
class Inscripcion:
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]
    inscripcion_id: UUID = field(default_factory=uuid4)
    estado: EstadoInscripcion = EstadoInscripcion.ACTIVA
    fecha_inscripcion: datetime = field(default_factory=datetime.utcnow)

    def cancelar(self, fecha_actual: date, fecha_inicio_torneo: date) -> None:
        """INV-I-03: solo cancela si fecha_actual < fecha_inicio_torneo."""
        if fecha_actual >= fecha_inicio_torneo:
            raise PlazoCancelacionVencido("No se puede cancelar el día del torneo o después")
        self.estado = EstadoInscripcion.CANCELADA
