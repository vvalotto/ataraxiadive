"""Command y Handler para RegistrarAP — US-1.2.1."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID, uuid4

from competencia.application.commands.registrar_resultado import UnidadIncompatible
from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.competencia_estado_port import CompetenciaEstadoPort
from competencia.domain.ports.disciplina_descriptor_port import DisciplinaDescriptorPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.unidad_medida import UnidadMedida

# ── Re-export para uso externo ─────────────────────────────────────────────────

__all__ = ["UnidadIncompatible", "APYaRegistrado", "PlazoAPVencidoError", "GrillaYaConfirmadaError"]


# ── Excepciones de aplicación ─────────────────────────────────────────────────


class APYaRegistrado(Exception):
    """INV-P-02: ya existe un AP activo para (atleta, disciplina, competencia)."""


class PlazoAPVencidoError(Exception):
    """INV-P-03: el plazo de registro de AP ya venció para esta competencia."""


class GrillaYaConfirmadaError(Exception):
    """INV-P-04: la grilla fue confirmada — no se permiten nuevos APs."""


# ── Command ───────────────────────────────────────────────────────────────────


@dataclass(frozen=True)
class RegistrarAPCommand:
    """Comando para registrar el AP de un atleta.

    Attributes:
        competencia_id: Competencia en la que se declara el AP.
        participante_id: Participante que declara el AP.
        disciplina: Disciplina en la que compite.
        valor_ap: Marca declarada (debe ser > 0).
        unidad: Unidad de medida (Metros | Segundos).
    """

    competencia_id: UUID
    participante_id: UUID
    disciplina: Disciplina
    valor_ap: Decimal
    unidad: UnidadMedida


# ── Handler ───────────────────────────────────────────────────────────────────


class RegistrarAPHandler:
    """Handler del comando RegistrarAP.

    Orquesta la verificación de precondiciones (INV-P-02, P-03, P-04),
    la creación del aggregate Performance y la persistencia del evento
    APRegistrado en el Event Store.

    Args:
        event_store: Puerto de persistencia de eventos.
        competencia_estado: Puerto para verificar estado de Competencia.
    """

    def __init__(
        self,
        event_store: EventStorePort,
        competencia_estado: CompetenciaEstadoPort,
        disciplina_descriptor: DisciplinaDescriptorPort,
    ) -> None:
        self._event_store = event_store
        self._competencia_estado = competencia_estado
        self._disciplina_descriptor = disciplina_descriptor

    async def handle(self, command: RegistrarAPCommand) -> UUID:
        """Ejecuta el comando RegistrarAP.

        Args:
            command: Datos del AP a registrar.

        Returns:
            UUID del PerformanceId recién creado.

        Raises:
            UnidadIncompatible: la unidad no coincide con la disciplina.
            PlazoAPVencidoError: INV-P-03 — plazo cerrado.
            GrillaYaConfirmadaError: INV-P-04 — grilla congelada.
            APYaRegistrado: INV-P-02 — AP duplicado.
            ValorAPInvalido: INV-P-01 — valor <= 0 (lanzado por AP value object).
        """
        descriptor = self._disciplina_descriptor.describe(command.disciplina)
        if command.unidad != descriptor.unidad_esperada:
            raise UnidadIncompatible(
                f"{command.disciplina.value} requiere {descriptor.unidad_esperada.value}, "
                f"recibido {command.unidad.value}"
            )

        # INV-P-03: plazo de AP vencido?
        if await self._competencia_estado.is_plazo_vencido(
            command.competencia_id, command.disciplina
        ):
            raise PlazoAPVencidoError(
                f"INV-P-03: plazo de AP vencido para competencia={command.competencia_id} "
                f"disciplina={command.disciplina.value}"
            )

        # INV-P-04: grilla confirmada?
        if await self._competencia_estado.is_grilla_confirmada(
            command.competencia_id, command.disciplina
        ):
            raise GrillaYaConfirmadaError(
                f"INV-P-04: grilla confirmada para competencia={command.competencia_id}"
            )

        # INV-P-02: ya existe un AP para esta combinación?
        stream_id = _build_stream_id(
            command.competencia_id, command.participante_id, command.disciplina
        )
        existing_events = await self._event_store.load(stream_id)
        if existing_events:
            raise APYaRegistrado(
                f"INV-P-02: ya existe un AP para participante={command.participante_id} "
                f"disciplina={command.disciplina.value} "
                f"competencia={command.competencia_id}"
            )

        # Crear Performance y registrar AP (INV-P-01 validado por AP value object)
        performance_id = uuid4()
        performance = Performance(
            performance_id=performance_id,
            competencia_id=command.competencia_id,
            participante_id=command.participante_id,
            disciplina=command.disciplina,
        )
        performance.registrarAP(command.valor_ap, command.unidad)

        # Persistir eventos pendientes
        for event in performance.pull_events():
            await self._event_store.append(
                stream_id=stream_id,
                event_type=event.event_type,
                payload=event.to_payload(),
            )

        return performance_id


# ── Helpers ───────────────────────────────────────────────────────────────────


def _build_stream_id(competencia_id: UUID, participante_id: UUID, disciplina: Disciplina) -> str:
    """Construye el stream ID canónico para una Performance.

    El stream ID encoda el natural key de la Performance.
    Stream vacío → Performance no existe → INV-P-02 satisfecho.

    Format: "performance-{competencia_id}-{participante_id}-{disciplina}"
    """
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"
