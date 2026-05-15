from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from uuid import UUID, uuid4

from shared.domain.value_objects.disciplina import Disciplina
from torneo.domain.exceptions import (
    AsignacionNoPermitida,
    DisciplinaObsoleta,
    DisciplinaNoEnTorneo,
    EdicionNoPermitida,
    TorneoCerrado,
    TransicionEstadoInvalida,
)
from torneo.domain.value_objects.disciplina_torneo import DisciplinaTorneo
from torneo.domain.value_objects.entidad_organizadora import EntidadOrganizadora
from torneo.domain.value_objects.estado_torneo import EstadoTorneo
from torneo.domain.value_objects.grupo_etario import GrupoEtario
from torneo.domain.value_objects.sede import Sede
from torneo.domain.value_objects.tipo_reglamento import TipoReglamento

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

_ESTADOS_EDICION_VALIDOS = {
    EstadoTorneo.CREADO,
    EstadoTorneo.INSCRIPCION_ABIERTA,
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
    tipo_reglamento: TipoReglamento = TipoReglamento.FAAS
    grupos_etarios: frozenset[GrupoEtario] = field(
        default_factory=lambda: frozenset({GrupoEtario.SENIOR})
    )

    def __post_init__(self) -> None:
        self._validar_nombre()
        self._validar_fechas()
        self._validar_grupos_etarios()

    def _transicionar(self, nuevo_estado: EstadoTorneo) -> None:
        self._validar_transicion(nuevo_estado)
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
        self._validar_cancelacion()
        self.estado = EstadoTorneo.CANCELADO

    def actualizar(
        self,
        nombre: str,
        descripcion: str,
        fecha_inicio: date,
        fecha_fin: date,
        sede: Sede,
        grupos_etarios: frozenset[GrupoEtario],
    ) -> None:
        if self.estado not in _ESTADOS_EDICION_VALIDOS:
            raise EdicionNoPermitida(f"No se puede editar un torneo en estado {self.estado.value}")
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.sede = sede
        self.grupos_etarios = grupos_etarios
        self._validar_nombre()
        self._validar_fechas()
        self._validar_grupos_etarios()

    def asignar_disciplinas(self, disciplinas: frozenset[Disciplina]) -> None:
        """Configura las disciplinas disponibles.

        Solo en estados CREADO, INSCRIPCION_ABIERTA o PREPARACION.
        """
        self._validar_estado_asignacion()
        self._validar_disciplinas(disciplinas)
        self.disciplinas_torneo = [DisciplinaTorneo(disciplina=d) for d in sorted(disciplinas)]

    def asignar_juez(self, disciplina: Disciplina, juez_id: UUID) -> None:
        """Asigna juez a una disciplina del torneo. Permite reasignación."""
        self._validar_estado_asignacion("juez")
        for i, dt in enumerate(self.disciplinas_torneo):
            if dt.disciplina == disciplina:
                self.disciplinas_torneo[i] = dt.con_juez(juez_id)
                return
        raise DisciplinaNoEnTorneo(f"La disciplina {disciplina} no está configurada en este torneo")

    def obtener_disciplinas_de_juez(self, juez_id: UUID) -> list[Disciplina]:
        """Retorna las disciplinas asignadas al juez dado."""
        return [dt.disciplina for dt in self.disciplinas_torneo if dt.juez_id == juez_id]

    def _validar_nombre(self) -> None:
        if not self.nombre or not self.nombre.strip():
            raise ValueError("El nombre del torneo no puede estar vacío")

    def _validar_fechas(self) -> None:
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor o igual a fecha_inicio")

    def _validar_transicion(self, nuevo_estado: EstadoTorneo) -> None:
        if self.estado == EstadoTorneo.CERRADO:
            raise TorneoCerrado(f"El torneo está cerrado y no puede transicionar a {nuevo_estado}")
        if nuevo_estado not in _TRANSICIONES_VALIDAS[self.estado]:
            raise TransicionEstadoInvalida(f"Transición inválida: {self.estado} → {nuevo_estado}")

    def _validar_cancelacion(self) -> None:
        if self.estado == EstadoTorneo.CERRADO:
            raise TorneoCerrado("Un torneo cerrado no puede cancelarse")
        if self.estado == EstadoTorneo.CANCELADO:
            raise TransicionEstadoInvalida("El torneo ya está cancelado")

    def _validar_estado_asignacion(self, contexto: str = "disciplinas") -> None:
        if self.estado not in _ESTADOS_ASIGNACION_VALIDOS:
            raise AsignacionNoPermitida(
                f"No se puede asignar {contexto} con el torneo en estado {self.estado}"
            )

    @staticmethod
    def _validar_disciplinas(disciplinas: frozenset[Disciplina]) -> None:
        if Disciplina.SPE in disciplinas:
            raise DisciplinaObsoleta(
                "Disciplina.SPE es legacy y no puede configurarse en torneos nuevos"
            )

    def _validar_grupos_etarios(self) -> None:
        if not self.grupos_etarios:
            raise ValueError("Debe seleccionar al menos un grupo etario")
