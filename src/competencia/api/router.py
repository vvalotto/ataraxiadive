"""Router FastAPI del BC Competencia — endpoints de la interfaz del juez."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from competencia.api.dependencies import (
    AjustarGrillaHandlerDep,
    ConfirmarGrillaHandlerDep,
    ConfigurarIntervaloOTHandlerDep,
    IniciarCompetenciaHandlerDep,
    ObtenerAndarivelesActivosHandlerDep,
    ObtenerEstadoCompetenciaHandlerDep,
    ObtenerEventosHandlerDep,
    ObtenerGrillaHandlerDep,
    ObtenerPerformanceActualHandlerDep,
    ObtenerProgresoHandlerDep,
    ObtenerProximasPerformancesHandlerDep,
    get_event_store,  # re-exportado: tests usan dependency_overrides[get_event_store]
)
from competencia.api.schemas import AjustarGrillaBody, ConfirmarGrillaBody, IniciarCompetenciaBody
from competencia.application.commands.ajustar_grilla import AjustarGrillaCommand
from competencia.application.commands.confirmar_grilla import ConfirmarGrillaCommand
from competencia.application.commands.iniciar_competencia import IniciarCompetenciaCommand
from competencia.application.queries.obtener_andariveles_activos import (
    ObtenerAndarivelesActivosQuery,
)
from competencia.application.queries.obtener_estado_competencia import (
    ObtenerEstadoCompetenciaQuery,
)
from competencia.application.queries.obtener_eventos import ObtenerEventosQuery
from competencia.application.queries.obtener_grilla import ObtenerGrillaQuery
from competencia.application.queries.obtener_performance_actual import (
    ObtenerPerformanceActualQuery,
    PerformanceActualDTO,
)
from competencia.application.queries.obtener_progreso import (
    ObtenerProgresoQuery,
    ProgresoCompetenciaDTO,
)
from competencia.application.queries.obtener_proximas_performances import (
    ObtenerProximasPerformancesQuery,
    ProximoAtletaDTO,
)
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina

router = APIRouter(prefix="/competencia", tags=["competencia"])

__all__ = ["router", "get_event_store"]


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
            "unidad_esperada": result.unidad_esperada,
            "andarivel": result.andarivel,
            "estado": result.estado,
        },
        status_code=200,
    )


@router.get("/{competencia_id}/performance/proximas", response_class=JSONResponse)
async def get_proximas_performances(
    competencia_id: UUID,
    disciplina: Disciplina,
    handler: ObtenerProximasPerformancesHandlerDep,
) -> list[ProximoAtletaDTO]:
    """Retorna los próximos 3 atletas a competir (en estado AnunciadaAP).

    Returns:
        Lista de hasta 3 ProximoAtletaDTO ordenados por posicion_grilla (SP2).
    """
    result = await handler.handle(
        ObtenerProximasPerformancesQuery(competencia_id=competencia_id, disciplina=disciplina)
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


@router.post("/{competencia_id}/ajustar-grilla", response_class=JSONResponse)
async def post_ajustar_grilla(
    competencia_id: UUID,
    body: AjustarGrillaBody,
    handler: AjustarGrillaHandlerDep,
) -> JSONResponse:
    """Aplica ajustes manuales sobre la Grilla de Salida (US-2.1.3).

    Returns:
        204 No Content si el ajuste fue aplicado correctamente.
    """
    cambios = [
        CambioGrilla(
            performance_id=c.performance_id,
            campo=c.campo,  # type: ignore[arg-type]
            valor_nuevo=c.valor_nuevo,
        )
        for c in body.cambios
    ]
    await handler.handle(
        AjustarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=body.disciplina,
            cambios=cambios,
        )
    )
    return JSONResponse(content=None, status_code=204)


@router.post("/{competencia_id}/confirmar-grilla", response_class=JSONResponse)
async def post_confirmar_grilla(
    competencia_id: UUID,
    body: ConfirmarGrillaBody,
    handler: ConfirmarGrillaHandlerDep,
) -> JSONResponse:
    """Confirma la Grilla de Salida de forma irreversible (INV-C-02).

    Returns:
        204 No Content si la grilla fue confirmada correctamente.
    """
    await handler.handle(
        ConfirmarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=body.disciplina,
        )
    )
    return JSONResponse(content=None, status_code=204)


@router.post("/{competencia_id}/iniciar", response_class=JSONResponse)
async def post_iniciar_competencia(
    competencia_id: UUID,
    body: IniciarCompetenciaBody,
    handler: IniciarCompetenciaHandlerDep,
) -> JSONResponse:
    """Inicia la Competencia, habilitando el registro de performances (INV-C-03).

    Returns:
        204 No Content si la competencia fue iniciada correctamente.
    """
    await handler.handle(
        IniciarCompetenciaCommand(
            competencia_id=competencia_id,
            disciplina=body.disciplina,
            juez_id=body.juez_id,
        )
    )
    return JSONResponse(content=None, status_code=204)


@router.get("/{competencia_id}/grilla", response_class=JSONResponse)
async def get_grilla(
    competencia_id: UUID,
    disciplina: Disciplina,
    handler: ObtenerGrillaHandlerDep,
) -> JSONResponse:
    """Retorna la Grilla de Salida ordenada por posición.

    Returns:
        Lista de entradas de grilla con performance_id, atleta_id, posicion,
        andarivel y ot_programado.
    """
    entradas = await handler.handle(
        ObtenerGrillaQuery(competencia_id=competencia_id, disciplina=disciplina)
    )
    return JSONResponse(
        content=[
            {
                "performance_id": e.performance_id,
                "atleta_id": e.atleta_id,
                "posicion": e.posicion,
                "andarivel": e.andarivel,
                "ot_programado": e.ot_programado,
            }
            for e in entradas
        ],
        status_code=200,
    )


@router.get("/{competencia_id}/estado", response_class=JSONResponse)
async def get_estado_competencia(
    competencia_id: UUID,
    disciplina: Disciplina,
    handler: ObtenerEstadoCompetenciaHandlerDep,
) -> JSONResponse:
    """Retorna el estado actual de la competencia.

    Returns:
        JSON con estado, intervalo_minutos y grilla_confirmada.
    """
    dto = await handler.handle(
        ObtenerEstadoCompetenciaQuery(competencia_id=competencia_id, disciplina=disciplina)
    )
    return JSONResponse(
        content={
            "estado": dto.estado,
            "intervalo_minutos": dto.intervalo_minutos,
            "grilla_confirmada": dto.grilla_confirmada,
        },
        status_code=200,
    )


@router.get("/{competencia_id}/andariveles", response_class=JSONResponse)
async def get_andariveles_activos(
    competencia_id: UUID,
    disciplina: Disciplina,
    andariveles: int,
    handler: ObtenerAndarivelesActivosHandlerDep,
) -> JSONResponse:
    """Retorna el estado de cada andarivel para la competencia en ejecución.

    Permite al juez ver qué andariveles están ocupados (Performance en Llamada)
    y cuáles están libres (US-2.3.1).

    Returns:
        Lista de andariveles con numero, ocupado, atleta_id, performance_id y ot_programado.
    """
    result = await handler.handle(
        ObtenerAndarivelesActivosQuery(
            competencia_id=competencia_id,
            disciplina=disciplina,
            andariveles=andariveles,
        )
    )
    return JSONResponse(
        content=[
            {
                "numero": a.numero,
                "ocupado": a.ocupado,
                "atleta_id": str(a.atleta_id) if a.atleta_id else None,
                "performance_id": str(a.performance_id) if a.performance_id else None,
                "ot_programado": a.ot_programado.isoformat() if a.ot_programado else None,
            }
            for a in result
        ],
        status_code=200,
    )
