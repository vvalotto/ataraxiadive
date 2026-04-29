from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from registro.domain.exceptions import DisciplinaNoInscripta, PlazoCancelacionVencido
from registro.domain.value_objects.ap_declarado import APDeclarado
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
    ap_por_disciplina: dict[Disciplina, APDeclarado] = field(default_factory=dict)

    def cancelar(self, fecha_actual: date, fecha_inicio_torneo: date) -> None:
        """INV-I-03: solo cancela si fecha_actual < fecha_inicio_torneo."""
        if fecha_actual >= fecha_inicio_torneo:
            raise PlazoCancelacionVencido("No se puede cancelar el día del torneo o después")
        self.estado = EstadoInscripcion.CANCELADA

    def declarar_ap(self, disciplina: Disciplina, valor: Decimal) -> APDeclarado:
        if disciplina not in self.disciplinas:
            raise DisciplinaNoInscripta(f"La disciplina {disciplina.value} no pertenece a la inscripción")
        ap = APDeclarado.desde_disciplina(disciplina, valor)
        self.ap_por_disciplina[disciplina] = ap
        return ap

    def obtener_ap(self, disciplina: Disciplina) -> APDeclarado | None:
        return self.ap_por_disciplina.get(disciplina)

    def tiene_ap_completo(self) -> bool:
        return all(self.obtener_ap(disciplina) is not None for disciplina in self.disciplinas)
