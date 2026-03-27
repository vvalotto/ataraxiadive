"""Router FastAPI del BC Competencia — endpoints de la interfaz del juez."""
from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from competencia.application.commands.ajustar_grilla import (
    AjustarGrillaCommand,
    AjustarGrillaHandler,
)
from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.application.queries.obtener_estado_competencia import (
    ObtenerEstadoCompetenciaHandler,
    ObtenerEstadoCompetenciaQuery,
)
from competencia.application.queries.obtener_eventos import (
    ObtenerEventosHandler,
    ObtenerEventosQuery,
)
from competencia.application.queries.obtener_grilla import (
    ObtenerGrillaHandler,
    ObtenerGrillaQuery,
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
from competencia.application.queries.obtener_andariveles_activos import (
    ObtenerAndarivelesActivosHandler,
    ObtenerAndarivelesActivosQuery,
)
from competencia.application.queries.obtener_progreso import (
    ObtenerProgresoHandler,
    ObtenerProgresoQuery,
    ProgresoCompetenciaDTO,
)
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.andariveles_activos_adapter import (
    AndarivelesActivosAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_estado_adapter import (
    PerformancesEstadoAdapter,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)

router = APIRouter(prefix="/competencia", tags=["competencia"])


# ── Request body schemas ───────────────────────────────────────────────────────


class CambioGrillaSchema(BaseModel):
    """Schema de un cambio individual sobre la Grilla de Salida."""

    performance_id: UUID
    campo: str
    valor_nuevo: int


class AjustarGrillaBody(BaseModel):
    """Body del endpoint POST /ajustar-grilla."""

    disciplina: Disciplina
    cambios: list[CambioGrillaSchema]


class ConfirmarGrillaBody(BaseModel):
    """Body del endpoint POST /confirmar-grilla."""

    disciplina: Disciplina


class IniciarCompetenciaBody(BaseModel):
    """Body del endpoint POST /iniciar."""

    disciplina: Disciplina
    juez_id: str


# ── Dependency providers ──────────────────────────────────────────────────────


def get_event_store() -> SQLiteEventStore:
    """Dependency: instancia del Event Store según configuración de entorno."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)


def get_disciplina_descriptor() -> DisciplinaDescriptorAdapter:
    """Dependency: adapter del descriptor de disciplina (sin I/O)."""
    return DisciplinaDescriptorAdapter()


def get_andariveles_activos_adapter(
    event_store: EventStoreDep,
) -> AndarivelesActivosAdapter:
    """Dependency: adapter de andariveles activos."""
    return AndarivelesActivosAdapter(event_store)


def get_performances_estado_adapter(
    event_store: EventStoreDep,
) -> PerformancesEstadoAdapter:
    """Dependency: adapter de estado de performances (P-08 — US-2.4.1)."""
    return PerformancesEstadoAdapter(event_store)


def get_obtener_andariveles_activos_handler(
    event_store: EventStoreDep,
) -> ObtenerAndarivelesActivosHandler:
    """Dependency: handler de consulta de andariveles activos."""
    return ObtenerAndarivelesActivosHandler(AndarivelesActivosAdapter(event_store))


EventStoreDep = Annotated[SQLiteEventStore, Depends(get_event_store)]
DisciplinaDescriptorDep = Annotated[DisciplinaDescriptorAdapter, Depends(get_disciplina_descriptor)]
ObtenerAndarivelesActivosHandlerDep = Annotated[
    ObtenerAndarivelesActivosHandler, Depends(get_obtener_andariveles_activos_handler)
]
PerformancesEstadoAdapterDep = Annotated[
    PerformancesEstadoAdapter, Depends(get_performances_estado_adapter)
]


def get_on_finalizada_callback(
    event_store: EventStoreDep,
    disciplina_descriptor: DisciplinaDescriptorDep,
) -> "Callable[[UUID, Disciplina], Awaitable[None]]":
    """Dependency: callback P-08 → CalcularRanking (SP2 llamada directa)."""
    from typing import Awaitable, Callable

    ranking_db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")

    async def _on_finalizada(competencia_id: UUID, disciplina: Disciplina) -> None:
        from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore as SES
        ranking_store = SES(ranking_db_path)
        acl = ResultadosCompetenciaAdapter(event_store)
        handler = CalcularRankingHandler(ranking_store, acl, disciplina_descriptor)
        await handler.handle(CalcularRankingCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
        ))

    return _on_finalizada


def get_obtener_eventos_handler(
    event_store: EventStoreDep,
) -> ObtenerEventosHandler:
    """Dependency: handler de consulta de eventos."""
    return ObtenerEventosHandler(event_store)


def get_obtener_performance_actual_handler(
    event_store: EventStoreDep,
    disciplina_descriptor: DisciplinaDescriptorDep,
) -> ObtenerPerformanceActualHandler:
    """Dependency: handler de performance actual."""
    return ObtenerPerformanceActualHandler(event_store, disciplina_descriptor)


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


def get_ajustar_grilla_handler(event_store: EventStoreDep) -> AjustarGrillaHandler:
    """Dependency: handler para ajustar la grilla."""
    return AjustarGrillaHandler(event_store)


def get_confirmar_grilla_handler(event_store: EventStoreDep) -> ConfirmarGrillaHandler:
    """Dependency: handler para confirmar la grilla."""
    return ConfirmarGrillaHandler(event_store)


def get_iniciar_competencia_handler(event_store: EventStoreDep) -> IniciarCompetenciaHandler:
    """Dependency: handler para iniciar la competencia."""
    return IniciarCompetenciaHandler(event_store)


def get_obtener_grilla_handler(event_store: EventStoreDep) -> ObtenerGrillaHandler:
    """Dependency: handler de consulta de la grilla."""
    return ObtenerGrillaHandler(event_store)


def get_obtener_estado_competencia_handler(
    event_store: EventStoreDep,
) -> ObtenerEstadoCompetenciaHandler:
    """Dependency: handler de consulta de estado de competencia."""
    return ObtenerEstadoCompetenciaHandler(event_store)


AjustarGrillaHandlerDep = Annotated[
    AjustarGrillaHandler, Depends(get_ajustar_grilla_handler)
]
ConfirmarGrillaHandlerDep = Annotated[
    ConfirmarGrillaHandler, Depends(get_confirmar_grilla_handler)
]
IniciarCompetenciaHandlerDep = Annotated[
    IniciarCompetenciaHandler, Depends(get_iniciar_competencia_handler)
]
ObtenerGrillaHandlerDep = Annotated[
    ObtenerGrillaHandler, Depends(get_obtener_grilla_handler)
]
ObtenerEstadoCompetenciaHandlerDep = Annotated[
    ObtenerEstadoCompetenciaHandler, Depends(get_obtener_estado_competencia_handler)
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
