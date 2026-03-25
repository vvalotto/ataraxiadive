"""Aggregate Competencia — ciclo de vida de una disciplina en un torneo."""
from __future__ import annotations

import json
from typing import Any
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.events.intervalo_ot_configurado import IntervaloOTConfigurado
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_competencia import EstadoCompetencia
from competencia.domain.value_objects.intervalo_disciplina import IntervaloDisciplina


class GrillaYaConfirmada(Exception):
    """La grilla fue confirmada — no se puede reconfigurar el intervalo OT."""


class Competencia(AggregateRoot):
    """Aggregate raíz que modela el ciclo de vida de una disciplina en un torneo.

    Stream ID: "competencia-{competencia_id}"

    Estados:
        Preparacion → Confirmada → EnEjecucion → Finalizada

    Invariantes:
        INV-C-01: intervaloDisciplina debe estar configurado antes de GenerarGrilla.
    """

    def __init__(
        self,
        competencia_id: UUID,
        disciplina: Disciplina,
    ) -> None:
        super().__init__()
        self._competencia_id = competencia_id
        self._disciplina = disciplina
        self._estado: EstadoCompetencia = EstadoCompetencia.Preparacion
        self._intervalo: IntervaloDisciplina | None = None
        self._grilla_confirmada: bool = False

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def competencia_id(self) -> UUID:
        """Identificador único de la Competencia."""
        return self._competencia_id

    @property
    def disciplina(self) -> Disciplina:
        """Disciplina asociada a esta Competencia."""
        return self._disciplina

    @property
    def estado(self) -> EstadoCompetencia:
        """Estado actual de la Competencia."""
        return self._estado

    @property
    def intervalo(self) -> IntervaloDisciplina | None:
        """Intervalo entre OTs configurado, o None si aún no fue configurado."""
        return self._intervalo

    # ── Comandos de dominio ───────────────────────────────────────────────────

    def configurar_intervalo_ot(
        self, intervalo_minutos: int, configurado_por: str
    ) -> None:
        """Configura (o reconfigura) el intervalo de tiempo entre OTs consecutivos.

        La operación es repetible. Si ya existe un IntervaloOTConfigurado previo,
        se emite uno nuevo con el valor actualizado (P-03: OTs desactualizados
        hasta regenerar grilla).

        Si la grilla ya fue confirmada (GrillaConfirmada emitido), la operación
        no está permitida — la grilla está congelada.

        Args:
            intervalo_minutos: Tiempo en minutos entre OTs. Debe ser > 0.
            configurado_por: Identificador del organizador o juez.

        Raises:
            IntervaloInvalido: Si intervalo_minutos <= 0.
            GrillaYaConfirmada: Si la grilla ya fue confirmada para esta competencia.
        """
        if self._grilla_confirmada:
            raise GrillaYaConfirmada(
                f"Competencia {self._competencia_id}: grilla confirmada — "
                "no se puede reconfigurar el intervalo OT"
            )

        intervalo = IntervaloDisciplina(minutos=intervalo_minutos)  # valida > 0

        event = IntervaloOTConfigurado(
            event_type="IntervaloOTConfigurado",
            aggregate_id=str(self._competencia_id),
            occurred_at=IntervaloOTConfigurado.now(),
            competencia_id=str(self._competencia_id),
            disciplina=self._disciplina.value,
            intervalo_minutos=intervalo.minutos,
            configurado_por=configurado_por,
        )
        self._intervalo = intervalo
        self._record(event)

    # ── Reconstitución desde eventos ──────────────────────────────────────────

    @classmethod
    def reconstitute(
        cls, competencia_id: UUID, disciplina: Disciplina, events: list[dict[str, Any]]
    ) -> "Competencia":
        """Reconstruye el aggregate desde los eventos del Event Store.

        Args:
            competencia_id: Identificador de la competencia.
            disciplina: Disciplina asociada.
            events: Lista de registros del Event Store (con event_type, payload).

        Returns:
            Competencia con el estado proyectado desde los eventos.
        """
        competencia = cls(competencia_id=competencia_id, disciplina=disciplina)
        for event in events:
            competencia._apply_stored(event)
        return competencia

    def _apply_stored(self, event: dict[str, Any]) -> None:
        """Aplica un evento almacenado al estado interno del aggregate."""
        event_type = event["event_type"]
        payload = self._parse_payload(event["payload"])

        _handlers: dict[str, Any] = {
            "IntervaloOTConfigurado": self._apply_intervalo_ot_configurado,
            "GrillaConfirmada": self._apply_grilla_confirmada,
        }

        handler = _handlers.get(event_type)
        if handler is not None:
            handler(payload)

    def _apply_intervalo_ot_configurado(self, payload: dict[str, Any]) -> None:
        self._intervalo = IntervaloDisciplina(minutos=payload["intervalo_minutos"])

    def _apply_grilla_confirmada(self, payload: dict[str, Any]) -> None:  # noqa: ARG002
        self._grilla_confirmada = True

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        """Parsea el payload del Event Store (puede ser str JSON o dict)."""
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]
