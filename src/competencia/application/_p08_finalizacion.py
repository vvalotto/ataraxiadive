"""Helper de Política P-08: disparar CompetenciaFinalizada cuando corresponde."""
from __future__ import annotations

from typing import Any, Awaitable, Callable
from uuid import UUID

from competencia.domain.aggregates.competencia import Competencia
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.domain.ports.performances_estado_port import PerformancesEstadoPort
from competencia.domain.value_objects.disciplina import Disciplina


async def trigger_finalizacion_si_corresponde(
    event_store: EventStorePort,
    performances_estado: PerformancesEstadoPort,
    competencia_id: UUID,
    disciplina: Disciplina,
    on_finalizada: Callable[[UUID, Disciplina], Awaitable[None]] | None = None,
) -> None:
    """Verifica P-08 y emite CompetenciaFinalizada si todas las performances terminaron.

    Consulta el estado actual de performances; si todas están en Ejecutada o DNS,
    carga el aggregate Competencia, llama a finalizar() y persiste CompetenciaFinalizada.
    Si se provee `on_finalizada`, lo llama tras persistir el evento (SP2: trigger ranking).

    Args:
        event_store: Puerto de persistencia de eventos.
        performances_estado: Puerto para obtener el snapshot de performances.
        competencia_id: Identificador de la competencia.
        disciplina: Disciplina en la que se verifica el cierre.
        on_finalizada: Callback async opcional — llamado con (competencia_id, disciplina)
            tras emitir CompetenciaFinalizada. En SP4+ se reemplaza por event bus.
    """
    estado = await performances_estado.get_estado(competencia_id, disciplina)
    if not estado.todas_finalizadas:
        return

    comp_stream_id = f"competencia-{competencia_id}"
    comp_events = await event_store.load(comp_stream_id)
    competencia = Competencia.reconstitute(
        competencia_id=competencia_id,
        disciplina=disciplina,
        events=comp_events,
    )

    competencia.finalizar(
        total_performances=estado.total,
        ejecutadas=estado.ejecutadas,
        dns_count=estado.dns_count,
    )

    for event in competencia.pull_events():
        await event_store.append(
            stream_id=comp_stream_id,
            event_type=event.event_type,
            payload=event.to_payload(),
        )

    if on_finalizada is not None:
        await on_finalizada(competencia_id, disciplina)
