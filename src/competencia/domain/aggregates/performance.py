"""Aggregate Performance — ciclo de vida de la actuación de un atleta."""
from __future__ import annotations

import json
from decimal import Decimal
from typing import Any
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.events.ap_registrado import APRegistrado
from competencia.domain.value_objects.ap import AP
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.estado_performance import EstadoPerformance
from competencia.domain.value_objects.unidad_medida import UnidadMedida


class Performance(AggregateRoot):
    """Aggregate raíz que modela el ciclo de vida de la actuación de un atleta.

    Stream ID: "performance-{competencia_id}-{participante_id}-{disciplina}"

    Estados:
        AnunciadaAP → Llamada → Ejecutada  (camino nominal)
        AnunciadaAP → Llamada → DNS        (atleta no se presentó)

    Invariantes (ver event-storming-competencia.md):
        INV-P-01: valorAP > 0  (validado por AP value object)
    """

    def __init__(
        self,
        performance_id: UUID,
        competencia_id: UUID,
        participante_id: UUID,
        disciplina: Disciplina,
    ) -> None:
        super().__init__()
        self._performance_id = performance_id
        self._competencia_id = competencia_id
        self._participante_id = participante_id
        self._disciplina = disciplina
        self._ap: AP | None = None
        self._estado: EstadoPerformance | None = None

    # ── Propiedades ───────────────────────────────────────────────────────────

    @property
    def performance_id(self) -> UUID:
        """Identificador único de la Performance."""
        return self._performance_id

    @property
    def estado(self) -> EstadoPerformance | None:
        """Estado actual de la Performance."""
        return self._estado

    @property
    def ap(self) -> AP | None:
        """AP registrado, o None si aún no fue declarado."""
        return self._ap

    # ── Comandos de dominio ───────────────────────────────────────────────────

    def registrarAP(self, valor: Decimal, unidad: UnidadMedida) -> None:
        """Registra el Announced Performance del atleta.

        Valida INV-P-01 a través del value object AP.
        Emite APRegistrado y transiciona al estado AnunciadaAP.

        Args:
            valor: Marca declarada. Debe ser > 0 (INV-P-01).
            unidad: Unidad de medida (Metros | Segundos).

        Raises:
            ValorAPInvalido: Si valor <= 0 (INV-P-01).
        """
        ap = AP(valor=valor, unidad=unidad)  # valida INV-P-01

        event = APRegistrado(
            event_type="APRegistrado",
            aggregate_id=str(self._performance_id),
            occurred_at=APRegistrado.now(),
            performance_id=str(self._performance_id),
            competencia_id=str(self._competencia_id),
            participante_id=str(self._participante_id),
            disciplina=self._disciplina.value,
            valor_ap=str(ap.valor),
            unidad=ap.unidad.value,
        )
        self._ap = ap
        self._estado = EstadoPerformance.AnunciadaAP
        self._record(event)

    # ── Reconstitución desde eventos ──────────────────────────────────────────

    @classmethod
    def reconstitute(cls, events: list[dict[str, Any]]) -> "Performance":
        """Reconstruye el aggregate desde los eventos del Event Store.

        Args:
            events: Lista de registros del Event Store (con event_type, payload).

        Returns:
            Performance con el estado proyectado desde los eventos.

        Raises:
            ValueError: Si la lista de eventos está vacía o el primer evento
                no es APRegistrado.
        """
        if not events:
            raise ValueError("No se puede reconstituir Performance sin eventos")

        first = events[0]
        if first["event_type"] != "APRegistrado":
            raise ValueError(
                f"El primer evento debe ser APRegistrado, recibido: {first['event_type']}"
            )

        payload = cls._parse_payload(first["payload"])
        performance = cls(
            performance_id=UUID(payload["performance_id"]),
            competencia_id=UUID(payload["competencia_id"]),
            participante_id=UUID(payload["participante_id"]),
            disciplina=Disciplina(payload["disciplina"]),
        )

        for event in events:
            performance._apply_stored(event)

        return performance

    def _apply_stored(self, event: dict[str, Any]) -> None:
        """Aplica un evento almacenado al estado interno del aggregate."""
        event_type = event["event_type"]
        payload = self._parse_payload(event["payload"])

        if event_type == "APRegistrado":
            self._ap = AP(
                valor=Decimal(payload["valor_ap"]),
                unidad=UnidadMedida(payload["unidad"]),
            )
            self._estado = EstadoPerformance.AnunciadaAP

    @staticmethod
    def _parse_payload(payload: Any) -> dict[str, Any]:
        """Parsea el payload del Event Store (puede ser str JSON o dict)."""
        if isinstance(payload, str):
            return json.loads(payload)  # type: ignore[no-any-return]
        return payload  # type: ignore[return-value]
