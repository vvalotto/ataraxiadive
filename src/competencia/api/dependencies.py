"""Dependency providers de FastAPI para el BC Competencia."""
from __future__ import annotations

import os
from typing import Annotated

from fastapi import Depends

from competencia.application.commands.ajustar_grilla import AjustarGrillaHandler
from competencia.application.commands.confirmar_grilla import ConfirmarGrillaHandler
from competencia.application.commands.configurar_intervalo_ot import ConfigurarIntervaloOTHandler
from competencia.application.commands.iniciar_competencia import IniciarCompetenciaHandler
from competencia.application.queries.obtener_andariveles_activos import (
    ObtenerAndarivelesActivosHandler,
)
from competencia.application.queries.obtener_audit_log import ObtenerAuditLogHandler
from competencia.application.queries.obtener_estado_competencia import (
    ObtenerEstadoCompetenciaHandler,
)
from competencia.application.queries.obtener_eventos import ObtenerEventosHandler
from competencia.application.queries.obtener_grilla import ObtenerGrillaHandler
from competencia.application.queries.obtener_performance_actual import (
    ObtenerPerformanceActualHandler,
)
from competencia.application.queries.obtener_progreso import ObtenerProgresoHandler
from competencia.application.queries.obtener_proximas_performances import (
    ObtenerProximasPerformancesHandler,
)
from competencia.domain.ports.event_store_port import EventStorePort
from competencia.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from competencia.infrastructure.repositories.andariveles_activos_adapter import (
    AndarivelesActivosAdapter,
)
from competencia.infrastructure.repositories.atleta_nombre_adapter import AtletaNombreAdapter
from competencia.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from competencia.infrastructure.repositories.performances_estado_adapter import (
    PerformancesEstadoAdapter,
)


def get_event_store() -> EventStorePort:
    """Dependency: instancia del Event Store según configuración de entorno."""
    db_path = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    return SQLiteEventStore(db_path)


def get_disciplina_descriptor() -> DisciplinaDescriptorAdapter:
    """Dependency: adapter del descriptor de disciplina (sin I/O)."""
    return DisciplinaDescriptorAdapter()


EventStoreDep = Annotated[EventStorePort, Depends(get_event_store)]
DisciplinaDescriptorDep = Annotated[DisciplinaDescriptorAdapter, Depends(get_disciplina_descriptor)]


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


ObtenerAndarivelesActivosHandlerDep = Annotated[
    ObtenerAndarivelesActivosHandler, Depends(get_obtener_andariveles_activos_handler)
]
ObtenerAuditLogHandlerDep = Annotated[
    ObtenerAuditLogHandler, Depends(get_obtener_audit_log_handler)
]
PerformancesEstadoAdapterDep = Annotated[
    PerformancesEstadoAdapter, Depends(get_performances_estado_adapter)
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
