"""Router FastAPI del BC Competencia — endpoints de la interfaz del juez."""
from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

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


def get_event_store() -> SQLiteEventStore:
    """Dependency: instancia del Event Store según configuración de entorno."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)


EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]


@router.get("/{competencia_id}/performance/actual", response_class=JSONResponse)
async def get_performance_actual(
    competencia_id: UUID,
    event_store: EventStoreDep,
) -> PerformanceActualDTO | None:
    """Retorna la performance que el juez está evaluando en este momento.

    Returns:
        PerformanceActualDTO si hay una performance en estado Llamada o
        ResultadoRegistrado, null si no hay ninguna activa.
    """
    handler = ObtenerPerformanceActualHandler(event_store)
    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=competencia_id))
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
    event_store: EventStoreDep,
) -> list[ProximoAtletaDTO]:
    """Retorna los próximos 3 atletas a competir (en estado AnunciadaAP).

    Returns:
        Lista de hasta 3 ProximoAtletaDTO ordenados por momento de registro (SP1).
    """
    handler = ObtenerProximasPerformancesHandler(event_store)
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
    event_store: EventStoreDep,
) -> ProgresoCompetenciaDTO:
    """Retorna el progreso de ejecución de la competencia.

    Returns:
        ProgresoCompetenciaDTO con total, ejecutadas, dns_count y completadas.
    """
    handler = ObtenerProgresoHandler(event_store)
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
