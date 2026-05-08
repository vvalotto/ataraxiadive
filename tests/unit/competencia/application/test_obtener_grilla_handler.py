"""Tests unitarios de ObtenerGrillaHandler."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal
from typing import Any
from uuid import UUID

import pytest

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.llamar_atleta import LlamarAtletaCommand, LlamarAtletaHandler
from competencia.application.commands.registrar_ap import RegistrarAPCommand, RegistrarAPHandler
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
)
from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
)
from competencia.application.queries.obtener_grilla import ObtenerGrillaHandler, ObtenerGrillaQuery
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.infrastructure.competencia_estado_stub import StubCompetenciaEstadoAdapter
from competencia.domain.ports.performances_ap_port import PerformancesAPData, PerformancesAPPort
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)

COMPETENCIA_ID = UUID("00000000-0000-0000-0000-000000000701")


class StubPerformancesAPPort(PerformancesAPPort):
    """Lee APRegistrado desde el event store para tests unitarios."""

    def __init__(self, store: "InMemoryEventStore") -> None:
        self._store = store

    async def get_performances_con_ap(self, competencia_id: UUID) -> list[PerformancesAPData]:
        streams = await self._store.load_all_streams_with_prefix(
            f"performance-{competencia_id}-"
        )
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
ATLETA_CON_TARJETA = UUID("00000000-0000-0000-0000-000000000711")
ATLETA_SIN_TARJETA = UUID("00000000-0000-0000-0000-000000000712")
OT_INICIO = datetime(2026, 4, 19, 10, 0, tzinfo=timezone.utc)


class InMemoryEventStore:
    """Event store minimo para tests del query handler."""

    def __init__(self) -> None:
        self._streams: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self._sequence = 0

    async def append(
        self,
        stream_id: str,
        event_type: str,
        payload: dict[str, Any],
        expected_version: int | None = None,
    ) -> None:
        del expected_version
        self._sequence += 1
        self._streams[stream_id].append(
            {
                "sequence": self._sequence,
                "stream_id": stream_id,
                "event_type": event_type,
                "payload": payload,
                "version": len(self._streams[stream_id]) + 1,
                "occurred_at": payload.get("occurred_at", OT_INICIO.isoformat()),
            }
        )

    async def load(self, stream_id: str) -> list[dict[str, Any]]:
        return list(self._streams.get(stream_id, []))

    async def load_from(self, stream_id: str, from_version: int) -> list[dict[str, Any]]:
        return [
            event for event in self._streams.get(stream_id, []) if event["version"] >= from_version
        ]

    async def load_all_streams_with_prefix(self, prefix: str) -> list[list[dict[str, Any]]]:
        return [
            list(events)
            for stream_id, events in self._streams.items()
            if stream_id.startswith(prefix)
        ]

    async def load_all_events_ordered(self, prefix: str) -> list[dict[str, Any]]:
        events = [
            event
            for stream_id, stream_events in self._streams.items()
            if stream_id.startswith(prefix)
            for event in stream_events
        ]
        return sorted(events, key=lambda event: event["sequence"])


async def _registrar_ap(store: InMemoryEventStore, atleta_id: UUID, valor: str) -> None:
    await RegistrarAPHandler(
        store,
        StubCompetenciaEstadoAdapter(),
        DisciplinaDescriptorAdapter(),
    ).handle(
        RegistrarAPCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=atleta_id,
            disciplina=Disciplina.DNF,
            valor_ap=Decimal(valor),
            unidad=UnidadMedida.Metros,
        )
    )


async def _seed_grilla(store: InMemoryEventStore) -> None:
    await ConfigurarIntervaloOTHandler(store).handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=Disciplina.DNF,
            intervalo_minutos=8,
            configurado_por="org",
        )
    )
    await _registrar_ap(store, ATLETA_CON_TARJETA, "50")
    await _registrar_ap(store, ATLETA_SIN_TARJETA, "60")
    await GenerarGrillaHandler(
        store,
        StubPerformancesAPPort(store),
        DisciplinaDescriptorAdapter(),
    ).handle(
        GenerarGrillaCommand(
            competencia_id=COMPETENCIA_ID,
            disciplina=Disciplina.DNF,
            ot_inicio=OT_INICIO,
        )
    )


async def _ejecutar_con_tarjeta(store: InMemoryEventStore) -> None:
    await LlamarAtletaHandler(store, StubCompetenciaEstadoAdapter()).handle(
        LlamarAtletaCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=ATLETA_CON_TARJETA,
            disciplina=Disciplina.DNF,
            ot_programado=OT_INICIO,
            posicion_grilla=1,
        )
    )
    await RegistrarResultadoHandler(store, DisciplinaDescriptorAdapter()).handle(
        RegistrarResultadoCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=ATLETA_CON_TARJETA,
            disciplina=Disciplina.DNF,
            valor_rp=Decimal("48"),
            unidad=UnidadMedida.Metros,
            registrado_por="juez",
        )
    )
    await AsignarTarjetaHandler(store).handle(
        AsignarTarjetaCommand(
            competencia_id=COMPETENCIA_ID,
            participante_id=ATLETA_CON_TARJETA,
            disciplina=Disciplina.DNF,
            tipo=TipoTarjeta.Blanca,
            asignada_por="juez",
        )
    )


@pytest.mark.asyncio
async def test_obtener_grilla_expone_tarjeta_asignada() -> None:
    store = InMemoryEventStore()
    await _seed_grilla(store)
    await _ejecutar_con_tarjeta(store)

    result = await ObtenerGrillaHandler(store).handle(
        ObtenerGrillaQuery(competencia_id=COMPETENCIA_ID, disciplina=Disciplina.DNF)
    )

    por_atleta = {entrada.atleta_id: entrada for entrada in result}
    assert por_atleta[str(ATLETA_CON_TARJETA)].tarjeta_asignada == "Blanca"
    assert por_atleta[str(ATLETA_SIN_TARJETA)].tarjeta_asignada is None
