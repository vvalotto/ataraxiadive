"""AtaraxiaDive — FastAPI application entry point (composition root)."""

import os
from typing import Awaitable, Callable
from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from competencia.application.queries.obtener_competencias_por_torneo import (
    ObtenerCompetenciasPorTorneoHandler,
    ObtenerCompetenciasPorTorneoQuery,
)
from competencia.api.exception_handlers import register_exception_handlers
from competencia.api.router import router as competencia_router
from resultados.api.router import router as resultados_router
from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from identidad.api.dependencies import configure_identity_dependencies
from identidad.api.router import router as identidad_router
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.jwt_service import JWTService
from notificaciones.application.commands.enviar_notificacion import (
    EnviarNotificacionHandler,
)
from notificaciones.application.commands.solicitar_envio import SolicitarEnvioHandler
from notificaciones.application.policies.politica_p10 import (
    InscripcionConfirmada,
    PoliticaP10Handler,
)
from notificaciones.application.policies.politica_p11 import PoliticaP11Handler
from notificaciones.infrastructure.email.resend_email_adapter import ResendEmailAdapter
from notificaciones.infrastructure.event_store.sqlite_notificacion_event_store import (
    SQLiteNotificacionEventStore,
)
from notificaciones.infrastructure.repositories.sqlite_notificacion_repository import (
    SQLiteNotificacionRepository,
)
from notificaciones.infrastructure.templates.inscripcion_confirmada_template import (
    InscripcionConfirmadaTemplate,
)
from notificaciones.infrastructure.templates.resultados_publicados_template import (
    ResultadosPublicadosTemplate,
)
from registro.api.router import (
    configure_inscripcion_notificaciones,
    router as registro_router,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import router as torneo_router
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.atleta_categoria_adapter import (
    AtletaCategoriaAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

app = FastAPI(title="AtaraxiaDive", version="0.1.0")

if os.getenv("IDENTIDAD_JWT_SECRET"):
    configure_identity_dependencies(
        token_service=JWTService(),
        password_hasher=BcryptPasswordHasher(),
    )

app.include_router(identidad_router)
app.include_router(registro_router)
app.include_router(competencia_router)
app.include_router(resultados_router)
app.include_router(torneo_router)
register_exception_handlers(app)
register_torneo_exception_handlers(app)


def build_p10_handler() -> PoliticaP10Handler:
    """Construye la política P-10 con adaptadores reales de Notificaciones."""
    store = SQLiteNotificacionEventStore()
    repository = SQLiteNotificacionRepository(store)
    return PoliticaP10Handler(
        repository=repository,
        solicitar_envio_handler=SolicitarEnvioHandler(repository),
        enviar_notificacion_handler=EnviarNotificacionHandler(
            repository,
            ResendEmailAdapter(),
        ),
        template=InscripcionConfirmadaTemplate(),
    )


def build_on_inscripcion_confirmada_callback(
    p10_handler: PoliticaP10Handler | None = None,
    atleta_repo: SQLiteAtletaRepository | None = None,
    torneo_repo: SQLiteTorneoRepository | None = None,
) -> Callable[[Inscripcion], Awaitable[None]]:
    """Construye el callback que traduce Registro -> Notificaciones P-10."""
    p10 = p10_handler or build_p10_handler()
    atletas = atleta_repo or SQLiteAtletaRepository()
    torneos = torneo_repo or SQLiteTorneoRepository()

    async def _callback(inscripcion: Inscripcion) -> None:
        atleta = await atletas.find_by_id(inscripcion.atleta_id)
        torneo = await torneos.find_by_id(inscripcion.torneo_id)
        if atleta is None or torneo is None:
            return

        evento = InscripcionConfirmada(
            id=str(inscripcion.inscripcion_id),
            atleta_id=str(inscripcion.atleta_id),
            atleta_email=atleta.email,
            atleta_nombre=f"{atleta.nombre} {atleta.apellido}".strip(),
            torneo_nombre=torneo.nombre,
            torneo_fecha=torneo.fecha_inicio,
            torneo_sede=torneo.sede.nombre,
            disciplinas=tuple(disciplina.value for disciplina in sorted(inscripcion.disciplinas)),
        )
        await p10.handle(evento)

    return _callback


configure_inscripcion_notificaciones(build_on_inscripcion_confirmada_callback())


def build_p11_handler() -> PoliticaP11Handler:
    """Construye la política P-11 con adaptadores reales de Notificaciones."""
    store = SQLiteNotificacionEventStore()
    repository = SQLiteNotificacionRepository(store)
    return PoliticaP11Handler(
        repository=repository,
        solicitar_envio_handler=SolicitarEnvioHandler(repository),
        enviar_notificacion_handler=EnviarNotificacionHandler(
            repository,
            ResendEmailAdapter(),
        ),
        template=ResultadosPublicadosTemplate(),
    )


# ── Política P-08: CompetenciaFinalizada → CalcularRanking ────────────────────
# El callback se construye aquí (composition root) y se inyectará a los handlers
# de competencia que lo necesiten (AsignarTarjetaHandler, RegistrarDNSHandler)
# cuando se agreguen los endpoints HTTP de performance en SP3+.


def build_on_finalizada_callback(
    competencia_event_store: SQLiteEventStore,
) -> Callable[[UUID, Disciplina, UUID | None], Awaitable[None]]:
    """Construye el callback P-08 + P-09.

    Args:
        competencia_event_store: Event Store del BC Competencia para que el ACL
            pueda leer las performances al calcular el ranking.

    Returns:
        Callable async (competencia_id, disciplina, torneo_id) → None.
    """
    ranking_db_path = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")
    torneo_db_path = os.getenv("TORNEO_DB_PATH", "data/torneo.db")

    async def _on_finalizada(
        competencia_id: UUID,
        disciplina: Disciplina,
        torneo_id: UUID | None = None,
    ) -> None:
        ranking_store = SQLiteEventStore(ranking_db_path)
        await _calcular_ranking_por_finalizacion(
            competencia_event_store,
            ranking_store,
            competencia_id,
            disciplina,
        )
        await _calcular_overall_si_corresponde(
            competencia_event_store,
            ranking_store,
            torneo_db_path,
            torneo_id,
        )

    return _on_finalizada


async def _calcular_ranking_por_finalizacion(
    competencia_event_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    competencia_id: UUID,
    disciplina: Disciplina,
) -> None:
    """Ejecuta P-08: calcular ranking por disciplina al finalizar competencia."""
    acl = ResultadosCompetenciaAdapter(competencia_event_store)
    atleta_categoria_acl = AtletaCategoriaAdapter()
    descriptor = DisciplinaDescriptorAdapter()
    ranking_handler = CalcularRankingHandler(
        ranking_store,
        acl,
        atleta_categoria_acl,
        descriptor,
    )
    await ranking_handler.handle(
        CalcularRankingCommand(
            competencia_id=competencia_id,
            disciplina=disciplina,
        )
    )


async def _calcular_overall_si_corresponde(
    competencia_event_store: SQLiteEventStore,
    ranking_store: SQLiteEventStore,
    torneo_db_path: str,
    torneo_id: UUID | None,
) -> None:
    """Ejecuta P-09 solo cuando el torneo existe y todas sus disciplinas finalizaron."""
    if torneo_id is None:
        return

    if not await _verificar_todas_disciplinas_finalizadas(torneo_id, competencia_event_store):
        return

    disciplinas = await _obtener_disciplinas_torneo(torneo_id, torneo_db_path)
    if not disciplinas:
        return

    overall_handler = CalcularOverallHandler(ranking_store, competencia_event_store)
    await overall_handler.handle(
        CalcularOverallCommand(
            torneo_id=torneo_id,
            disciplinas=disciplinas,
        )
    )


async def _verificar_todas_disciplinas_finalizadas(
    torneo_id: UUID,
    competencia_event_store: SQLiteEventStore,
) -> bool:
    """Helper de P-09: verifica si todas las competencias del torneo finalizaron."""
    handler = ObtenerCompetenciasPorTorneoHandler(SQLiteCompetenciasPorTorneo())
    competencias = await handler.handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=torneo_id))
    if not competencias:
        return False

    for competencia in competencias:
        events = await competencia_event_store.load(f"competencia-{competencia.competencia_id}")
        if not any(event["event_type"] == "CompetenciaFinalizada" for event in events):
            return False
    return True


async def _obtener_disciplinas_torneo(
    torneo_id: UUID,
    torneo_db_path: str,
) -> list[Disciplina]:
    """Helper de P-09: obtiene las disciplinas registradas para el torneo."""
    torneo_repo = SQLiteTorneoRepository(torneo_db_path)
    torneo = await torneo_repo.find_by_id(torneo_id)
    if torneo is None:
        return []
    return [Disciplina(disciplina.disciplina) for disciplina in torneo.disciplinas_torneo]


@app.get("/health", response_class=JSONResponse)
async def health_check() -> dict[str, str]:
    """Health-check endpoint — verifica que la aplicación está activa."""
    return {"status": "ok"}
