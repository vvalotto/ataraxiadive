"""Stubs compartidos para tests BDD del BC Competencia."""

from __future__ import annotations

from decimal import Decimal
from uuid import UUID

from competencia.domain.ports.performances_ap_port import PerformancesAPData, PerformancesAPPort
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore


class StubPerformancesAPPort(PerformancesAPPort):
    """Lee APRegistrado desde el event store para tests BDD."""

    def __init__(self, store: SQLiteEventStore) -> None:
        self._store = store

    async def get_performances_con_ap(self, competencia_id: UUID) -> list[PerformancesAPData]:
        streams = await self._store.load_all_streams_with_prefix(f"performance-{competencia_id}-")
        result = []
        for stream in streams:
            for event in stream:
                if event["event_type"] == "APRegistrado":
                    p = event["payload"]
                    result.append(
                        PerformancesAPData(
                            performance_id=UUID(p["performance_id"]),
                            atleta_id=UUID(p["participante_id"]),
                            valor_ap=Decimal(p["valor_ap"]),
                            unidad=UnidadMedida(p["unidad"]),
                        )
                    )
                    break
        return result
