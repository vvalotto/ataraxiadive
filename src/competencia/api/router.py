"""Router FastAPI del BC Competencia — endpoints de la interfaz del juez."""

from __future__ import annotations

import os
from datetime import datetime
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse, Response
from pydantic import BaseModel

from competencia.application.commands.asignar_tarjeta import (
    AsignarTarjetaCommand,
    AsignarTarjetaHandler,
    PerformanceNoEncontrada as PerformanceNoEncontradaAsignarTarjeta,
)
from competencia.application.commands.ajustar_grilla import (
    AjustarGrillaCommand,
    AjustarGrillaHandler,
)
from competencia.application.commands.confirmar_grilla import (
    ConfirmarGrillaCommand,
    ConfirmarGrillaHandler,
)
from competencia.application.commands.corregir_resultado_tras_dns import (
    CorregirResultadoTrasDNSCommand,
    CorregirResultadoTrasDNSHandler,
    PerformanceNoEncontrada as PerformanceNoEncontradaCorregirTrasDns,
)
from competencia.application.commands.configurar_intervalo_ot import (
    ConfigurarIntervaloOTCommand,
    ConfigurarIntervaloOTHandler,
)
from competencia.application.commands.generar_grilla import (
    GenerarGrillaCommand,
    GenerarGrillaHandler,
)
from competencia.application.commands.llamar_atleta import (
    AndarivelesConflicto,
    CompetenciaNoEnEjecucion,
    LlamarAtletaCommand,
    LlamarAtletaHandler,
    PerformanceNoEncontrada as PerformanceNoEncontradaLlamar,
)
from competencia.application.commands.registrar_resultado import (
    RegistrarResultadoCommand,
    RegistrarResultadoHandler,
    PerformanceNoEncontrada as PerformanceNoEncontradaRegistrarResultado,
    UnidadIncompatible,
)
from competencia.application.commands.registrar_dns import (
    RegistrarDNSCommand,
    RegistrarDNSHandler,
    PerformanceNoEncontrada as PerformanceNoEncontradaRegistrarDns,
)
from competencia.application.commands.resolver_revision import (
    ResolverRevisionCommand,
    ResolverRevisionHandler,
    PerformanceNoEncontrada as PerformanceNoEncontradaResolverRevision,
)
from competencia.application.queries.obtener_competencias_por_torneo import (
    ObtenerCompetenciasPorTorneoHandler,
    ObtenerCompetenciasPorTorneoQuery,
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
from competencia.application.queries.obtener_audit_log import (
    ObtenerAuditLogHandler,
    ObtenerAuditLogQuery,
    PerformanceNoEncontrada as PerformanceNoEncontradaAuditLog,
)
from competencia.application.queries.obtener_progreso import (
    ObtenerProgresoHandler,
    ObtenerProgresoQuery,
    ProgresoCompetenciaDTO,
)
from competencia.domain.value_objects.cambio_grilla import CambioGrilla
from competencia.domain.value_objects.disciplina import Disciplina
from competencia.domain.value_objects.motivo_dq import MotivoDQ
from competencia.domain.value_objects.penalizacion_tecnica import PenalizacionTecnica
from competencia.domain.value_objects.tipo_penalizacion import TipoPenalizacion
from competencia.domain.value_objects.tipo_tarjeta import TipoTarjeta
from competencia.domain.value_objects.unidad_medida import UnidadMedida
from competencia.domain.ports.competencias_por_torneo_port import CompetenciasPorTorneoPort
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.competencia_estado_adapter import (
    CompetenciaEstadoAdapter,
)
from competencia.infrastructure.repositories.andariveles_activos_adapter import (
    AndarivelesActivosAdapter,
)
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_estado_adapter import (
    PerformancesEstadoAdapter,
)
from competencia.infrastructure.repositories.performances_ap_adapter import PerformancesAPAdapter
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from competencia.infrastructure.repositories.atleta_nombre_adapter import AtletaNombreAdapter
from competencia.domain.exceptions import DomainError
from shared.api.dependencies import JuezDep, OrganizadorDep

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


class GenerarGrillaBody(BaseModel):
    """Body del endpoint POST /generar-grilla."""

    disciplina: Disciplina
    ot_inicio: datetime
    andariveles: int = 1


class ConfigurarOTBody(BaseModel):
    """Body del endpoint POST /competencia — crea y configura una competencia."""

    competencia_id: UUID
    disciplina: Disciplina
    intervalo_minutos: int
    configurado_por: str
    torneo_id: UUID | None = None


class LlamarAtletaBody(BaseModel):
    """Body del endpoint POST /competencia/{id}/llamar."""

    participante_id: UUID
    disciplina: Disciplina
    ot_programado: datetime
    posicion_grilla: int
    andarivel: int = 1


class RegistrarResultadoBody(BaseModel):
    """Body del endpoint POST /competencia/{id}/registrar-resultado."""

    participante_id: UUID
    disciplina: Disciplina
    valor_rp: Decimal
    unidad: UnidadMedida


class RegistrarDNSBody(BaseModel):
    """Body del endpoint POST /competencia/{id}/registrar-dns."""

    participante_id: UUID
    disciplina: Disciplina


class CorregirResultadoTrasDNSBody(BaseModel):
    """Body del endpoint para corregir un DNS registrado por error."""

    participante_id: UUID | None = None
    atleta_id: UUID | None = None
    disciplina: Disciplina
    valor_rp: Decimal
    unidad: UnidadMedida
    registrado_por: str | None = None
    motivo_correccion: str

    def resolve_participante_id(self) -> UUID:
        """Compatibilidad: acepta participante_id o atleta_id."""
        if self.participante_id is not None:
            return self.participante_id
        if self.atleta_id is not None:
            return self.atleta_id
        raise ValueError("participante_id o atleta_id es obligatorio")


class PenalizacionTecnicaBody(BaseModel):
    """Payload de una penalización técnica individual."""

    tipo: TipoPenalizacion
    deduccion: Decimal


class AsignarTarjetaBody(BaseModel):
    """Body del endpoint POST /competencia/{id}/asignar-tarjeta."""

    participante_id: UUID
    disciplina: Disciplina
    tipo: TipoTarjeta | None = None
    tarjeta: TipoTarjeta | None = None
    motivo_dq: MotivoDQ | None = None
    motivo_texto: str | None = None
    distancia_blackout: Decimal | None = None
    penalizaciones: list[PenalizacionTecnicaBody] = []

    def resolve_tipo(self) -> TipoTarjeta:
        """Compatibilidad con spec: acepta `tipo` o `tarjeta`."""
        return self.tipo or self.tarjeta or TipoTarjeta.Blanca


class ResolverRevisionBody(BaseModel):
    """Body del endpoint POST /competencia/{id}/resolver-revision."""

    participante_id: UUID
    disciplina: Disciplina
    tipo: TipoTarjeta | None = None
    resolucion: TipoTarjeta | None = None
    motivo_dq: MotivoDQ | None = None
    penalizaciones: list[PenalizacionTecnicaBody] = []

    def resolve_tipo(self) -> TipoTarjeta:
        """Compatibilidad con spec: acepta `tipo` o `resolucion`."""
        return self.tipo or self.resolucion or TipoTarjeta.Blanca


# ── Dependency providers ──────────────────────────────────────────────────────


def get_event_store() -> EventStorePort:
    """Dependency: instancia del Event Store según configuración de entorno."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)


def get_disciplina_descriptor() -> DisciplinaDescriptorAdapter:
    """Dependency: adapter del descriptor de disciplina (sin I/O)."""
    return DisciplinaDescriptorAdapter()


def get_competencias_por_torneo_projection() -> CompetenciasPorTorneoPort:
    """Dependency: proyeccion materializada de competencias por torneo."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteCompetenciasPorTorneo(db_path)


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


def get_obtener_audit_log_handler(
    event_store: EventStoreDep,
) -> ObtenerAuditLogHandler:
    """Dependency: handler de consulta de audit log."""
    return ObtenerAuditLogHandler(event_store, AtletaNombreAdapter())


def get_llamar_atleta_handler(
    event_store: EventStoreDep,
) -> LlamarAtletaHandler:
    """Dependency: handler para llamar al atleta."""
    return LlamarAtletaHandler(
        event_store,
        CompetenciaEstadoAdapter(event_store),
        AndarivelesActivosAdapter(event_store),
    )


def get_registrar_resultado_handler(
    event_store: EventStoreDep,
    disciplina_descriptor: DisciplinaDescriptorDep,
) -> RegistrarResultadoHandler:
    """Dependency: handler para registrar resultado."""
    return RegistrarResultadoHandler(event_store, disciplina_descriptor)


def get_asignar_tarjeta_handler(
    event_store: EventStoreDep,
    performances_estado: PerformancesEstadoAdapterDep,
) -> AsignarTarjetaHandler:
    """Dependency: handler para asignar tarjeta."""
    return AsignarTarjetaHandler(event_store, performances_estado)


def get_registrar_dns_handler(
    event_store: EventStoreDep,
    performances_estado: PerformancesEstadoAdapterDep,
) -> RegistrarDNSHandler:
    """Dependency: handler para registrar DNS."""
    return RegistrarDNSHandler(event_store, performances_estado)


def get_corregir_resultado_tras_dns_handler(
    event_store: EventStoreDep,
) -> CorregirResultadoTrasDNSHandler:
    """Dependency: handler para corregir resultado tras DNS."""
    return CorregirResultadoTrasDNSHandler(event_store)


def get_resolver_revision_handler(
    event_store: EventStoreDep,
    performances_estado: PerformancesEstadoAdapterDep,
) -> ResolverRevisionHandler:
    """Dependency: handler para resolver una revision pendiente."""
    return ResolverRevisionHandler(event_store, performances_estado)


EventStoreDep = Annotated[EventStorePort, Depends(get_event_store)]
DisciplinaDescriptorDep = Annotated[DisciplinaDescriptorAdapter, Depends(get_disciplina_descriptor)]
CompetenciasPorTorneoProjectionDep = Annotated[
    CompetenciasPorTorneoPort, Depends(get_competencias_por_torneo_projection)
]
ObtenerAndarivelesActivosHandlerDep = Annotated[
    ObtenerAndarivelesActivosHandler, Depends(get_obtener_andariveles_activos_handler)
]
ObtenerAuditLogHandlerDep = Annotated[
    ObtenerAuditLogHandler, Depends(get_obtener_audit_log_handler)
]
PerformancesEstadoAdapterDep = Annotated[
    PerformancesEstadoAdapter, Depends(get_performances_estado_adapter)
]
LlamarAtletaHandlerDep = Annotated[LlamarAtletaHandler, Depends(get_llamar_atleta_handler)]
RegistrarResultadoHandlerDep = Annotated[
    RegistrarResultadoHandler, Depends(get_registrar_resultado_handler)
]
AsignarTarjetaHandlerDep = Annotated[AsignarTarjetaHandler, Depends(get_asignar_tarjeta_handler)]
RegistrarDNSHandlerDep = Annotated[RegistrarDNSHandler, Depends(get_registrar_dns_handler)]
CorregirResultadoTrasDNSHandlerDep = Annotated[
    CorregirResultadoTrasDNSHandler,
    Depends(get_corregir_resultado_tras_dns_handler),
]
ResolverRevisionHandlerDep = Annotated[
    ResolverRevisionHandler, Depends(get_resolver_revision_handler)
]


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
    proyeccion: CompetenciasPorTorneoProjectionDep,
) -> ConfigurarIntervaloOTHandler:
    """Dependency: handler para configurar intervalo OT."""
    return ConfigurarIntervaloOTHandler(event_store, proyeccion)


def get_obtener_competencias_por_torneo_handler(
    proyeccion: CompetenciasPorTorneoProjectionDep,
) -> ObtenerCompetenciasPorTorneoHandler:
    """Dependency: handler para listar competencias por torneo."""
    return ObtenerCompetenciasPorTorneoHandler(proyeccion)


ObtenerEventosHandlerDep = Annotated[ObtenerEventosHandler, Depends(get_obtener_eventos_handler)]
ObtenerPerformanceActualHandlerDep = Annotated[
    ObtenerPerformanceActualHandler, Depends(get_obtener_performance_actual_handler)
]
ObtenerProximasPerformancesHandlerDep = Annotated[
    ObtenerProximasPerformancesHandler, Depends(get_obtener_proximas_performances_handler)
]
ObtenerProgresoHandlerDep = Annotated[ObtenerProgresoHandler, Depends(get_obtener_progreso_handler)]
ConfigurarIntervaloOTHandlerDep = Annotated[
    ConfigurarIntervaloOTHandler, Depends(get_configurar_intervalo_ot_handler)
]
ObtenerCompetenciasPorTorneoHandlerDep = Annotated[
    ObtenerCompetenciasPorTorneoHandler, Depends(get_obtener_competencias_por_torneo_handler)
]


def get_ajustar_grilla_handler(event_store: EventStoreDep) -> AjustarGrillaHandler:
    """Dependency: handler para ajustar la grilla."""
    return AjustarGrillaHandler(event_store)


def get_confirmar_grilla_handler(event_store: EventStoreDep) -> ConfirmarGrillaHandler:
    """Dependency: handler para confirmar la grilla."""
    return ConfirmarGrillaHandler(event_store)


def get_generar_grilla_handler(
    event_store: EventStoreDep,
    disciplina_descriptor: DisciplinaDescriptorDep,
) -> GenerarGrillaHandler:
    """Dependency: handler para generar la grilla."""
    return GenerarGrillaHandler(
        event_store,
        PerformancesAPAdapter(event_store),
        disciplina_descriptor,
    )


def get_iniciar_competencia_handler(event_store: EventStoreDep) -> IniciarCompetenciaHandler:
    """Dependency: handler para iniciar la competencia."""
    return IniciarCompetenciaHandler(event_store)


def get_obtener_grilla_handler(event_store: EventStoreDep) -> ObtenerGrillaHandler:
    """Dependency: handler de consulta de la grilla."""
    return ObtenerGrillaHandler(event_store, AtletaNombreAdapter())


def get_obtener_estado_competencia_handler(
    event_store: EventStoreDep,
) -> ObtenerEstadoCompetenciaHandler:
    """Dependency: handler de consulta de estado de competencia."""
    return ObtenerEstadoCompetenciaHandler(event_store)


AjustarGrillaHandlerDep = Annotated[AjustarGrillaHandler, Depends(get_ajustar_grilla_handler)]
ConfirmarGrillaHandlerDep = Annotated[ConfirmarGrillaHandler, Depends(get_confirmar_grilla_handler)]
GenerarGrillaHandlerDep = Annotated[GenerarGrillaHandler, Depends(get_generar_grilla_handler)]
IniciarCompetenciaHandlerDep = Annotated[
    IniciarCompetenciaHandler, Depends(get_iniciar_competencia_handler)
]
ObtenerGrillaHandlerDep = Annotated[ObtenerGrillaHandler, Depends(get_obtener_grilla_handler)]
ObtenerEstadoCompetenciaHandlerDep = Annotated[
    ObtenerEstadoCompetenciaHandler, Depends(get_obtener_estado_competencia_handler)
]


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("", response_class=JSONResponse)
async def post_configurar_competencia(
    body: ConfigurarOTBody,
    handler: ConfigurarIntervaloOTHandlerDep,
    _: OrganizadorDep,
) -> JSONResponse:
    """Crea y configura una competencia (primer comando de dominio — US-3.3.1).

    Si se provee torneo_id, la competencia queda asociada al torneo (INV-CT-02).
    Si no se provee, la competencia es standalone (INV-CT-01).

    Returns:
        201 con competencia_id.
    """
    await handler.handle(
        ConfigurarIntervaloOTCommand(
            competencia_id=body.competencia_id,
            disciplina=body.disciplina,
            intervalo_minutos=body.intervalo_minutos,
            configurado_por=body.configurado_por,
            torneo_id=body.torneo_id,
        )
    )
    return JSONResponse(
        content={"competencia_id": str(body.competencia_id)},
        status_code=201,
    )


@router.get("", response_class=JSONResponse)
async def get_competencias_por_torneo(
    torneo_id: UUID,
    handler: ObtenerCompetenciasPorTorneoHandlerDep,
) -> JSONResponse:
    """Lista las competencias asociadas a un torneo (US-3.3.1).

    Returns:
        200 con lista de competencias del torneo.
    """
    competencias = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=torneo_id))
    return JSONResponse(
        content=[
            {
                "competencia_id": str(c.competencia_id),
                "disciplina": c.disciplina,
                "torneo_id": str(c.torneo_id),
            }
            for c in competencias
        ],
        status_code=200,
    )


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


@router.get("/{competencia_id}/performances/{atleta_id}/audit-log", response_class=JSONResponse)
async def get_audit_log(
    competencia_id: UUID,
    atleta_id: UUID,
    handler: ObtenerAuditLogHandlerDep,
    _: OrganizadorDep,
) -> JSONResponse:
    """Retorna el audit log de una performance puntual para auditoria."""
    try:
        audit_log = await handler.handle(
            ObtenerAuditLogQuery(competencia_id=competencia_id, atleta_id=atleta_id)
        )
    except PerformanceNoEncontradaAuditLog as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    return JSONResponse(
        content={
            "competencia_id": audit_log.competencia_id,
            "atleta_id": audit_log.atleta_id,
            "atleta_nombre": audit_log.atleta_nombre,
            "disciplina": audit_log.disciplina,
            "eventos": [
                {
                    "sequence": evento.sequence,
                    "tipo": evento.tipo,
                    "timestamp": evento.timestamp,
                    "datos": evento.datos,
                }
                for evento in audit_log.eventos
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
    result = await handler.handle(ObtenerPerformanceActualQuery(competencia_id=competencia_id))
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
    _: OrganizadorDep,
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
    return Response(status_code=204)


@router.post("/{competencia_id}/generar-grilla", response_class=JSONResponse)
async def post_generar_grilla(
    competencia_id: UUID,
    body: GenerarGrillaBody,
    handler: GenerarGrillaHandlerDep,
    _: OrganizadorDep,
) -> JSONResponse:
    """Genera la Grilla de Salida desde el primer OT definido por organizador."""
    await handler.handle(
        GenerarGrillaCommand(
            competencia_id=competencia_id,
            disciplina=body.disciplina,
            ot_inicio=body.ot_inicio,
            andariveles=body.andariveles,
        )
    )
    return Response(status_code=204)


@router.post("/{competencia_id}/llamar", response_class=JSONResponse)
async def post_llamar_atleta(
    competencia_id: UUID,
    body: LlamarAtletaBody,
    handler: LlamarAtletaHandlerDep,
    user: JuezDep,
) -> JSONResponse:
    """Llama al atleta seleccionado para iniciar el flujo de performance."""
    try:
        await handler.handle(
            LlamarAtletaCommand(
                competencia_id=competencia_id,
                participante_id=body.participante_id,
                disciplina=body.disciplina,
                ot_programado=body.ot_programado,
                posicion_grilla=body.posicion_grilla,
                andarivel=body.andarivel,
            )
        )
    except (
        CompetenciaNoEnEjecucion,
        AndarivelesConflicto,
    ) as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc), "actor": user["email"]})
    except PerformanceNoEncontradaLlamar as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DomainError as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return Response(status_code=204)


@router.post("/{competencia_id}/registrar-resultado", response_class=JSONResponse)
async def post_registrar_resultado(
    competencia_id: UUID,
    body: RegistrarResultadoBody,
    handler: RegistrarResultadoHandlerDep,
    user: JuezDep,
) -> JSONResponse:
    """Registra el RP de la performance activa."""
    try:
        await handler.handle(
            RegistrarResultadoCommand(
                competencia_id=competencia_id,
                participante_id=body.participante_id,
                disciplina=body.disciplina,
                valor_rp=body.valor_rp,
                unidad=body.unidad,
                registrado_por=user["email"],
            )
        )
    except UnidadIncompatible as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except PerformanceNoEncontradaRegistrarResultado as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DomainError as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return Response(status_code=204)


@router.post("/{competencia_id}/registrar-dns", response_class=JSONResponse)
async def post_registrar_dns(
    competencia_id: UUID,
    body: RegistrarDNSBody,
    handler: RegistrarDNSHandlerDep,
    user: JuezDep,
) -> JSONResponse:
    """Registra que el atleta no se presentó."""
    try:
        await handler.handle(
            RegistrarDNSCommand(
                competencia_id=competencia_id,
                participante_id=body.participante_id,
                disciplina=body.disciplina,
                registrado_por=user["email"],
            )
        )
    except PerformanceNoEncontradaRegistrarDns as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DomainError as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return Response(status_code=204)


@router.post(
    "/{competencia_id}/performances/{performance_id}/corregir-resultado-tras-dns",
    response_class=JSONResponse,
)
async def post_corregir_resultado_tras_dns(
    competencia_id: UUID,
    performance_id: UUID,
    body: CorregirResultadoTrasDNSBody,
    handler: CorregirResultadoTrasDNSHandlerDep,
    user: JuezDep,
) -> JSONResponse:
    """Corrige un DNS registrado por error y deja la performance lista para tarjeta."""
    del performance_id
    try:
        await handler.handle(
            CorregirResultadoTrasDNSCommand(
                competencia_id=competencia_id,
                participante_id=body.resolve_participante_id(),
                disciplina=body.disciplina,
                valor_rp=body.valor_rp,
                unidad=body.unidad,
                registrado_por=body.registrado_por or user["email"],
                motivo_correccion=body.motivo_correccion,
            )
        )
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except PerformanceNoEncontradaCorregirTrasDns as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DomainError as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return Response(status_code=204)


@router.post("/{competencia_id}/asignar-tarjeta", response_class=JSONResponse)
async def post_asignar_tarjeta(
    competencia_id: UUID,
    body: AsignarTarjetaBody,
    handler: AsignarTarjetaHandlerDep,
    user: JuezDep,
) -> JSONResponse:
    """Asigna la tarjeta final de la performance."""
    try:
        await handler.handle(
            AsignarTarjetaCommand(
                competencia_id=competencia_id,
                participante_id=body.participante_id,
                disciplina=body.disciplina,
                tipo=body.resolve_tipo(),
                asignada_por=user["email"],
                motivo_dq=body.motivo_dq,
                motivo_texto=body.motivo_texto,
                distancia_blackout=body.distancia_blackout,
                penalizaciones=tuple(
                    PenalizacionTecnica(tipo=p.tipo, deduccion=p.deduccion)
                    for p in body.penalizaciones
                ),
            )
        )
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except PerformanceNoEncontradaAsignarTarjeta as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DomainError as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return Response(status_code=204)


@router.post("/{competencia_id}/resolver-revision", response_class=JSONResponse)
async def post_resolver_revision(
    competencia_id: UUID,
    body: ResolverRevisionBody,
    handler: ResolverRevisionHandlerDep,
    user: JuezDep,
) -> JSONResponse:
    """Resuelve la tarjeta definitiva de una performance en revisión."""
    try:
        await handler.handle(
            ResolverRevisionCommand(
                competencia_id=competencia_id,
                participante_id=body.participante_id,
                disciplina=body.disciplina,
                tipo=body.resolve_tipo(),
                resuelta_por=user["email"],
                motivo_dq=body.motivo_dq,
                penalizaciones=tuple(
                    PenalizacionTecnica(tipo=p.tipo, deduccion=p.deduccion)
                    for p in body.penalizaciones
                ),
            )
        )
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except PerformanceNoEncontradaResolverRevision as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DomainError as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return Response(status_code=204)


@router.post("/{competencia_id}/confirmar-grilla", response_class=JSONResponse)
async def post_confirmar_grilla(
    competencia_id: UUID,
    body: ConfirmarGrillaBody,
    handler: ConfirmarGrillaHandlerDep,
    _: OrganizadorDep,
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
    return Response(status_code=204)


@router.post("/{competencia_id}/iniciar", response_class=JSONResponse)
async def post_iniciar_competencia(
    competencia_id: UUID,
    body: IniciarCompetenciaBody,
    handler: IniciarCompetenciaHandlerDep,
    _: OrganizadorDep,
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
    return Response(status_code=204)


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
                "nombre_atleta": e.nombre_atleta,
                "posicion": e.posicion,
                "andarivel": e.andarivel,
                "ot_programado": e.ot_programado,
                "ap_declarado": e.ap_declarado,
                "unidad": e.unidad,
                "estado": e.estado,
                "tarjeta_asignada": e.tarjeta_asignada,
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
            "torneo_id": str(dto.torneo_id) if dto.torneo_id else None,
            "hash_sha256": dto.hash_sha256,
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
