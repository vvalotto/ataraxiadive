"""Router FastAPI del BC Competencia — endpoints de la interfaz del juez."""
from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTHandler,
)
from competencia.application.queries.obtener_eventos import (
    ObtenerEventosHandler,
    ObtenerEventosQuery,
)
from competencia.application.queries.obtener_performance_actual import (
    ObtenerPerformanceActualHandler,
    ObtenerPerformanceActualQuery,
    PerformanceActualDTO,
)
from competencia.application.queries.obtener_proximas_performances import (
    ObtenerProximasPerformancesHandler,
    ObtenerProximasPerformancesQuery,
    ProximoAtletaDTO,
)
from competencia.application.queries.obtener_progreso import (
    ObtenerProgresoHandler,
    ObtenerProgresoQuery,
    ProgresoCompetenciaDTO,
)
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

router = APIRouter(prefix="/competencia", tags=["competencia"])


# ── Dependency providers ──────────────────────────────────────────────────────


def get_event_store() -> SQLiteEventStore:
    """Dependency: instancia del Event Store según configuración de entorno."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)


EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]


def get_obtener_eventos_handler(
    event_store: EventStoreDep,
) -> ObtenerEventosHandler:
    """Dependency: handler de consulta de eventos."""
    return ObtenerEventosHandler(event_store)


def get_obtener_performance_actual_handler(
    event_store: EventStoreDep,
) -> ObtenerPerformanceActualHandler:
    """Dependency: handler de performance actual."""
    return ObtenerPerformanceActualHandler(event_store)


def get_obtener_proximas_performances_handler(
    event_store: EventStoreDep,
) -> ObtenerProximasPerformancesHandler:
    """Dependency: handler de próximas performances."""
    return ObtenerProximasPerformancesHandler(event_store)


def get_obtener_progreso_handler(
    event_store: EventStoreDep,
) -> ObtenerProgresoHandler:
    """Dependency: handler de progreso de competencia."""
    return ObtenerProgresoHandler(event_store)


def get_configurar_intervalo_ot_handler(
    event_store: EventStoreDep,
) -> ConfigurarIntervaloOTHandler:
    """Dependency: handler para configurar intervalo OT."""
    return ConfigurarIntervaloOTHandler(event_store)


ObtenerEventosHandlerDep = Annotated[
    ObtenerEventosHandler, Depends(get_obtener_eventos_handler)
]
ObtenerPerformanceActualHandlerDep = Annotated[
    ObtenerPerformanceActualHandler, Depends(get_obtener_performance_actual_handler)
]
ObtenerProximasPerformancesHandlerDep = Annotated[
    ObtenerProximasPerformancesHandler, Depends(get_obtener_proximas_performances_handler)
]
ObtenerProgresoHandlerDep = Annotated[
    ObtenerProgresoHandler, Depends(get_obtener_progreso_handler)
]
ConfigurarIntervaloOTHandlerDep = Annotated[
    ConfigurarIntervaloOTHandler, Depends(get_configurar_intervalo_ot_handler)
]


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.get("/{competencia_id}/events", response_class=JSONResponse)
async def get_eventos(
    competencia_id: UUID,
    handler: ObtenerEventosHandlerDep,
) -> JSONResponse:
    """Retorna todos los eventos del Event Store para una competencia en orden de inserción.

    Expone el Event Store como audit log de solo lectura. Útil para verificar
    la traza completa de eventos y la consistencia del sistema (US-1.4.2).

    Returns:
        JSON con competencia_id, total_events y lista de eventos con
        sequence, event_type, performance_id, occurred_at y data.
    """
    eventos = await handler.handle(ObtenerEventosQuery(competencia_id=competencia_id))
    return JSONResponse(
        content={
            "competencia_id": str(competencia_id),
            "total_events": len(eventos),
            "events": [
                {
                    "sequence": dto.sequence,
                    "event_type": dto.event_type,
                    "performance_id": dto.performance_id,
                    "occurred_at": dto.occurred_at,
                    "data": dto.data,
                }
                for dto in eventos
            ],
        },
        status_code=200,
    )


@router.get("/{competencia_id}/performance/actual", response_class=JSONResponse)
async def get_performance_actual(
    competencia_id: UUID,
    handler: ObtenerPerformanceActualHandlerDep,
) -> PerformanceActualDTO | None:
    """Retorna la performance que el juez está evaluando en este momento.

    Returns:
        PerformanceActualDTO si hay una performance en estado Llamada o
        ResultadoRegistrado, null si no hay ninguna activa.
    """
    result = await handler.handle(
        ObtenerPerformanceActualQuery(competencia_id=competencia_id)
    )
    if result is None:
        return JSONResponse(content=None, status_code=200)
    return JSONResponse(
        content={
            "performance_id": result.performance_id,
            "nombre_atleta": result.nombre_atleta,
            "ap_declarado": result.ap_declarado,
            "unidad": result.unidad,
            "andarivel": result.andarivel,
            "estado": result.estado,
        },
        status_code=200,
    )


@router.get("/{competencia_id}/performance/proximas", response_class=JSONResponse)
async def get_proximas_performances(
    competencia_id: UUID,
    handler: ObtenerProximasPerformancesHandlerDep,
) -> list[ProximoAtletaDTO]:
    """Retorna los próximos 3 atletas a competir (en estado AnunciadaAP).

    Returns:
        Lista de hasta 3 ProximoAtletaDTO ordenados por momento de registro (SP1).
    """
    result = await handler.handle(
        ObtenerProximasPerformancesQuery(competencia_id=competencia_id)
    )
    return JSONResponse(
        content=[
            {
                "nombre_atleta": dto.nombre_atleta,
                "ap_declarado": dto.ap_declarado,
                "unidad": dto.unidad,
                "posicion": dto.posicion,
            }
            for dto in result
        ],
        status_code=200,
    )


@router.get("/{competencia_id}/progreso", response_class=JSONResponse)
async def get_progreso(
    competencia_id: UUID,
    handler: ObtenerProgresoHandlerDep,
) -> ProgresoCompetenciaDTO:
    """Retorna el progreso de ejecución de la competencia.

    Returns:
        ProgresoCompetenciaDTO con total, ejecutadas, dns_count y completadas.
    """
    result = await handler.handle(ObtenerProgresoQuery(competencia_id=competencia_id))
    return JSONResponse(
        content={
            "total": result.total,
            "ejecutadas": result.ejecutadas,
            "dns_count": result.dns_count,
            "completadas": result.completadas,
        },
        status_code=200,
    )
