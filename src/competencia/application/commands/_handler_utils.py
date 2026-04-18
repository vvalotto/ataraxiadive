"""Helpers internos para reducir orquestacion repetida en handlers."""

from __future__ import annotations

from collections.abc import Callable
from typing import TypeVar
from uuid import UUID

from shared.domain.base.aggregate_root import AggregateRoot
from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.aggregates.performance import Performance
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.value_objects.disciplina import Disciplina

AggregateT = TypeVar("AggregateT", bound=AggregateRoot)


async def cargar_o_fallar(
    *,
    event_store: EventStorePort,
    stream_id: str,
    exception_factory: Callable[[], Exception],
) -> list[dict]:
    """Carga eventos desde un stream y falla si no existe."""
    events = await event_store.load(stream_id)
    if not events:
        raise exception_factory()
    return events


def reconstruir_performance(events: list[dict]) -> Performance:
    """Reconstituye una performance desde su stream."""
    return Performance.reconstitute(events)


def reconstruir_competencia(
    *,
    competencia_id: UUID,
    disciplina: Disciplina,
    events: list[dict],
) -> Competencia:
    """Reconstituye una competencia desde su stream."""
    return Competencia.reconstitute(
        competencia_id=competencia_id,
        disciplina=disciplina,
        events=events,
    )


async def persistir_eventos_pendientes(
    *,
    event_store: EventStorePort,
    stream_id: str,
    aggregate: AggregateT,
) -> None:
    """Persiste todos los eventos pendientes del aggregate."""
    for event in aggregate.pull_events():
        await event_store.append(
            stream_id=stream_id,
            event_type=event.event_type,
            payload=event.to_payload(),
        )


def build_performance_stream_id(
    competencia_id: UUID,
    participante_id: UUID,
    disciplina: Disciplina,
) -> str:
    """Construye el stream ID canónico para Performance."""
    return f"performance-{competencia_id}-{participante_id}-{disciplina.value}"


def build_competencia_stream_id(competencia_id: UUID) -> str:
    """Construye el stream ID canónico para Competencia."""
    return f"competencia-{competencia_id}"
