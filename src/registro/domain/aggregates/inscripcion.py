from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Mapping
from uuid import UUID, uuid4

from registro.domain.exceptions import DisciplinaNoInscripta, PlazoCancelacionVencido
from registro.domain.value_objects.ap_declarado import APDeclarado
from registro.domain.value_objects.estado_aceptacion import EstadoAceptacion
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from shared.domain.value_objects.disciplina import Disciplina
from shared.domain.value_objects.unidad_medida import UnidadMedida


@dataclass
class Inscripcion:
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: frozenset[Disciplina]
    inscripcion_id: UUID = field(default_factory=uuid4)
    estado: EstadoInscripcion = EstadoInscripcion.ACTIVA
    fecha_inscripcion: datetime = field(default_factory=datetime.utcnow)
    ap_por_disciplina: dict[Disciplina, APDeclarado] = field(default_factory=dict)
    apto_medico_path: str | None = None
    constancia_pago_path: str | None = None
    estado_aceptacion: EstadoAceptacion = EstadoAceptacion.ACEPTADO

    @classmethod
    def from_row(cls, data: Mapping[str, Any]) -> Inscripcion:
        """Reconstituye una inscripcion desde datos planos persistidos."""
        return cls(
            inscripcion_id=UUID(data["inscripcion_id"]),
            atleta_id=UUID(data["atleta_id"]),
            torneo_id=UUID(data["torneo_id"]),
            disciplinas=frozenset(Disciplina(d) for d in json.loads(data["disciplinas"])),
            estado=EstadoInscripcion(data["estado"]),
            fecha_inscripcion=datetime.fromisoformat(data["fecha_inscripcion"]),
            ap_por_disciplina=_parse_ap_por_disciplina(data.get("ap_por_disciplina")),
            apto_medico_path=data.get("apto_medico_path"),
            constancia_pago_path=data.get("constancia_pago_path"),
            estado_aceptacion=EstadoAceptacion(
                data.get("estado_aceptacion") or EstadoAceptacion.ACEPTADO
            ),
        )

    def cancelar(self, fecha_actual: date, fecha_inicio_torneo: date) -> None:
        """INV-I-03: solo cancela si fecha_actual < fecha_inicio_torneo."""
        if fecha_actual >= fecha_inicio_torneo:
            raise PlazoCancelacionVencido("No se puede cancelar el día del torneo o después")
        self.estado = EstadoInscripcion.CANCELADA

    def declarar_ap(self, disciplina: Disciplina, valor: Decimal) -> APDeclarado:
        if disciplina not in self.disciplinas:
            raise DisciplinaNoInscripta(
                f"La disciplina {disciplina.value} no pertenece a la inscripción"
            )
        ap = APDeclarado.desde_disciplina(disciplina, valor)
        self.ap_por_disciplina[disciplina] = ap
        return ap

    def obtener_ap(self, disciplina: Disciplina) -> APDeclarado | None:
        return self.ap_por_disciplina.get(disciplina)

    def tiene_ap_completo(self) -> bool:
        return all(self.obtener_ap(disciplina) is not None for disciplina in self.disciplinas)

    def cambiar_aceptacion(self, nuevo_estado: EstadoAceptacion) -> None:
        self.estado_aceptacion = nuevo_estado

    def adjuntar_apto_medico(self, path: str) -> None:
        if not path or not path.strip():
            raise ValueError("path no puede ser vacío")
        self.apto_medico_path = path

    def adjuntar_constancia_pago(self, path: str) -> None:
        if not path or not path.strip():
            raise ValueError("path no puede ser vacío")
        self.constancia_pago_path = path


def _parse_ap_por_disciplina(raw: Any) -> dict[Disciplina, APDeclarado]:
    return {
        Disciplina(disciplina): APDeclarado(
            valor=Decimal(payload["valor"]),
            unidad=UnidadMedida(payload["unidad"]),
        )
        for disciplina, payload in json.loads(raw or "{}").items()
    }
