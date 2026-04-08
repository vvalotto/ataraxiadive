from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.exceptions import (
    AsignacionNoPermitida,
    DisciplinaObsoleta,
    DisciplinaNoEnTorneo,
    TorneoCerrado,
    TransicionEstadoInvalida,
)
from torneo.domain.value_objects.disciplina_torneo import DisciplinaTorneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.sede import Sede

_TRANSICIONES_VALIDAS: dict[EstadoTorneo, set[EstadoTorneo]] = {
    EstadoTorneo.CREADO: {EstadoTorneo.INSCRIPCION_ABIERTA},
    EstadoTorneo.INSCRIPCION_ABIERTA: {EstadoTorneo.PREPARACION},
    EstadoTorneo.PREPARACION: {EstadoTorneo.EJECUCION},
    EstadoTorneo.EJECUCION: {EstadoTorneo.PREPARACION, EstadoTorneo.PREMIACION},
    EstadoTorneo.PREMIACION: {EstadoTorneo.CERRADO},
    EstadoTorneo.CERRADO: set(),
    EstadoTorneo.CANCELADO: set(),
}

_ESTADOS_TERMINALES = {EstadoTorneo.CERRADO, EstadoTorneo.CANCELADO}


_ESTADOS_ASIGNACION_VALIDOS = {
    EstadoTorneo.CREADO,
    EstadoTorneo.INSCRIPCION_ABIERTA,
    EstadoTorneo.PREPARACION,
}

@dataclass
class Torneo:
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede: Sede
    entidad_organizadora: EntidadOrganizadora
    torneo_id: UUID = field(default_factory=uuid4)
    estado: EstadoTorneo = EstadoTorneo.CREADO
    disciplinas_torneo: list[DisciplinaTorneo] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del torneo no puede estar vacío")
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor o igual a fecha_inicio")

    def _transicionar(self, nuevo_estado: EstadoTorneo) -> None:
        if self.estado == EstadoTorneo.CERRADO:
            raise TorneoCerrado(f"El torneo está cerrado y no puede transicionar a {nuevo_estado}")
        if nuevo_estado not in _TRANSICIONES_VALIDAS[self.estado]:
            raise TransicionEstadoInvalida(f"Transición inválida: {self.estado} → {nuevo_estado}")
        self.estado = nuevo_estado

    def abrir_inscripcion(self) -> None:
        self._transicionar(EstadoTorneo.INSCRIPCION_ABIERTA)

    def cerrar_inscripcion(self) -> None:
        self._transicionar(EstadoTorneo.PREPARACION)

    def iniciar_ejecucion(self) -> None:
        self._transicionar(EstadoTorneo.EJECUCION)

    def volver_a_preparacion(self) -> None:
        self._transicionar(EstadoTorneo.PREPARACION)

    def iniciar_premiacion(self) -> None:
        self._transicionar(EstadoTorneo.PREMIACION)

    def cerrar(self) -> None:
        self._transicionar(EstadoTorneo.CERRADO)

    def cancelar(self) -> None:
        if self.estado == EstadoTorneo.CERRADO:
            raise TorneoCerrado("Un torneo cerrado no puede cancelarse")
        if self.estado == EstadoTorneo.CANCELADO:
            raise TransicionEstadoInvalida("El torneo ya está cancelado")
        self.estado = EstadoTorneo.CANCELADO

    def asignar_disciplinas(self, disciplinas: frozenset[Disciplina]) -> None:
        """Configura las disciplinas disponibles. Solo en estados CREADO, INSCRIPCION_ABIERTA o PREPARACION."""
        if self.estado not in _ESTADOS_ASIGNACION_VALIDOS:
            raise AsignacionNoPermitida(
                f"No se pueden asignar disciplinas con el torneo en estado {self.estado}"
            )
        if Disciplina.SPE in disciplinas:
            raise DisciplinaObsoleta(
                "Disciplina.SPE es legacy y no puede configurarse en torneos nuevos"
            )
        self.disciplinas_torneo = [DisciplinaTorneo(disciplina=d) for d in sorted(disciplinas)]

    def asignar_juez(self, disciplina: Disciplina, juez_id: UUID) -> None:
        """Asigna juez a una disciplina del torneo. Permite reasignación."""
        if self.estado not in _ESTADOS_ASIGNACION_VALIDOS:
            raise AsignacionNoPermitida(
                f"No se puede asignar juez con el torneo en estado {self.estado}"
            )
        for i, dt in enumerate(self.disciplinas_torneo):
            if dt.disciplina == disciplina:
                self.disciplinas_torneo[i] = dt.con_juez(juez_id)
                return
        raise DisciplinaNoEnTorneo(f"La disciplina {disciplina} no está configurada en este torneo")

    def obtener_disciplinas_de_juez(self, juez_id: UUID) -> list[Disciplina]:
        """Retorna las disciplinas asignadas al juez dado."""
        return [dt.disciplina for dt in self.disciplinas_torneo if dt.juez_id == juez_id]
