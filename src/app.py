"""AtaraxiaDive — FastAPI application entry point (composition root)."""

import logging
import os
from decimal import Decimal
from typing import Awaitable, Callable
from uuid import UUID

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from competencia.api.exception_handlers import register_exception_handlers
from competencia.api.router import (
    configure_ap_registrado_callback,
    configure_competencia_cross_bc_dependencies,
    configure_on_finalizada_callback,
)
from competencia.api.router import (
    router as competencia_router,
)
from competencia.application.commands.iniciar_competencia import (
    IniciarCompetenciaCommand,
    IniciarCompetenciaHandler,
)
from competencia.application.queries.obtener_competencias_por_torneo import (
    ObtenerCompetenciasPorTorneoHandler,
    ObtenerCompetenciasPorTorneoQuery,
)
from competencia.domain.aggregates.competencia import Competencia
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
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
from notificaciones.application.policies.politica_p11 import (
    PodioPublicado,
    PoliticaP11Handler,
    ResultadoPublicadoAtleta,
    ResultadosPublicados,
)
from notificaciones.infrastructure.email.logging_email_adapter import LoggingEmailAdapter
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
    build_cierre_inscripcion_precondition,
    configure_inscripcion_notificaciones,
)
from registro.api.router import (
    router as registro_router,
)
from registro.application.commands.declarar_ap_inscripcion import (
    DeclararAPInscripcionCommand,
    DeclararAPInscripcionHandler,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from resultados.api.router import (
    configure_resultados_cross_bc_dependencies,
)
from resultados.api.router import (
    router as resultados_router,
)
from resultados.application.commands.calcular_overall import (
    CalcularOverallCommand,
    CalcularOverallHandler,
)
from resultados.application.commands.calcular_ranking import (
    CalcularRankingCommand,
    CalcularRankingHandler,
)
from resultados.domain.services.algoritmo_faas import AlgoritmoPuntajeFAAS
from resultados.application.queries.obtener_ranking import (
    ObtenerRankingHandler,
    ObtenerRankingQuery,
)
from resultados.infrastructure.repositories.atleta_categoria_adapter import (
    AtletaCategoriaAdapter,
)
from resultados.infrastructure.repositories.disciplina_descriptor_adapter import (
    DisciplinaDescriptorAdapter,
)
from resultados.infrastructure.repositories.resultados_competencia_adapter import (
    ResultadosCompetenciaAdapter,
)
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore
from torneo.api.exception_handlers import register_torneo_exception_handlers
from torneo.api.router import (
    configure_cierre_inscripcion_precondition,
    configure_ejecucion_post_action,
    configure_ejecucion_precondition,
    configure_premiacion_precondition,
)
from torneo.api.router import (
    router as torneo_router,
)
from torneo.domain.exceptions import EjecucionNoPermitida, PremiacionNoPermitida
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

app = FastAPI(title="AtaraxiaDive", version="0.1.0")
logger = logging.getLogger(__name__)

if os.getenv("IDENTIDAD_JWT_SECRET"):
    configure_identity_dependencies(
        token_service=JWTService(),
        password_hasher=BcryptPasswordHasher(),
        email_sender=ResendEmailAdapter() if os.getenv("RESEND_API_KEY") else LoggingEmailAdapter(),
    )

configure_competencia_cross_bc_dependencies(
    inscripcion_repository_factory=lambda: SQLiteInscripcionRepository(
        os.getenv("REGISTRO_DB_PATH", "data/registro.db")
    )
)
configure_resultados_cross_bc_dependencies(
    competencias_por_torneo_factory=lambda: SQLiteCompetenciasPorTorneo(
        os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    ),
    torneo_repository_factory=SQLiteTorneoRepository,
)

app.include_router(identidad_router)
app.include_router(registro_router)
app.include_router(competencia_router)
app.include_router(resultados_router)
app.include_router(torneo_router)
register_exception_handlers(app)
register_torneo_exception_handlers(app)


def build_p10_handler() -> PoliticaP10Handler:
    """Construye la política P-10.

    Usa ResendEmailAdapter si RESEND_API_KEY está configurado,
    LoggingEmailAdapter como fallback para desarrollo/smoke-test.
    """
    store = SQLiteNotificacionEventStore()
    repository = SQLiteNotificacionRepository(store)
    email_adapter = ResendEmailAdapter() if os.getenv("RESEND_API_KEY") else LoggingEmailAdapter()
    return PoliticaP10Handler(
        repository=repository,
        solicitar_envio_handler=SolicitarEnvioHandler(repository),
        enviar_notificacion_handler=EnviarNotificacionHandler(
            repository,
            email_adapter,
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
configure_cierre_inscripcion_precondition(build_cierre_inscripcion_precondition())


def build_p11_handler() -> PoliticaP11Handler:
    """Construye la política P-11 con adaptadores reales de Notificaciones."""
    store = SQLiteNotificacionEventStore()
    repository = SQLiteNotificacionRepository(store)
    email_adapter = ResendEmailAdapter() if os.getenv("RESEND_API_KEY") else LoggingEmailAdapter()
    return PoliticaP11Handler(
        repository=repository,
        solicitar_envio_handler=SolicitarEnvioHandler(repository),
        enviar_notificacion_handler=EnviarNotificacionHandler(
            repository,
            email_adapter,
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
    registro_db_path = os.getenv("REGISTRO_DB_PATH", "data/registro.db")
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
        try:
            await _notificar_resultados_p11(
                ranking_store=ranking_store,
                competencia_id=competencia_id,
                disciplina=disciplina,
                torneo_id=torneo_id,
                registro_db_path=registro_db_path,
                torneo_db_path=torneo_db_path,
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("P-11 no pudo notificar resultados: %s", exc)

    return _on_finalizada


async def _notificar_resultados_p11(
    *,
    ranking_store: SQLiteEventStore,
    competencia_id: UUID,
    disciplina: Disciplina,
    torneo_id: UUID | None,
    registro_db_path: str,
    torneo_db_path: str,
    p11_handler: PoliticaP11Handler | None = None,
    atleta_repo: SQLiteAtletaRepository | None = None,
    torneo_repo: SQLiteTorneoRepository | None = None,
) -> None:
    """Ejecuta P-11: notificar resultados publicados al finalizar disciplina."""
    categorias = await ObtenerRankingHandler(ranking_store).handle(
        ObtenerRankingQuery(competencia_id=competencia_id, disciplina=disciplina)
    )
    entradas = [entrada for categoria in categorias for entrada in categoria.entradas]
    if not entradas:
        return

    atletas = atleta_repo or SQLiteAtletaRepository(registro_db_path)
    torneo_nombre = await _obtener_nombre_torneo(torneo_id, torneo_db_path, torneo_repo)

    resultados: list[ResultadoPublicadoAtleta] = []
    podio: list[PodioPublicado] = []
    for entrada in entradas:
        atleta_nombre, atleta_email = await _obtener_datos_atleta_p11(atletas, entrada.atleta_id)
        rp = _rp_publicado(entrada.rp)
        resultados.append(
            ResultadoPublicadoAtleta(
                atleta_id=entrada.atleta_id,
                atleta_email=atleta_email,
                atleta_nombre=atleta_nombre,
                posicion=entrada.posicion,
                rp=rp,
                tarjeta=entrada.tarjeta,
                estado="DNS" if entrada.es_dns else "Clasificado",
            )
        )
        if entrada.en_podio:
            podio.append(_crear_podio_publicado(entrada.posicion, atleta_nombre, rp))

    evento = ResultadosPublicados(
        id=str(competencia_id),
        torneo_id=str(torneo_id) if torneo_id else None,
        torneo_nombre=torneo_nombre,
        disciplina=disciplina.value,
        resultados=tuple(resultados),
        podio=tuple(podio),
    )
    await (p11_handler or build_p11_handler()).handle(evento)


async def _obtener_datos_atleta_p11(
    atletas: SQLiteAtletaRepository,
    atleta_id: str,
) -> tuple[str, str | None]:
    """Obtiene nombre/email para P-11; si Registro falla, permite registrar fallo sin email."""
    try:
        atleta = await atletas.find_by_id(UUID(atleta_id))
    except Exception:  # noqa: BLE001
        atleta = None
    if atleta is None:
        return atleta_id, None
    return f"{atleta.nombre} {atleta.apellido}".strip(), atleta.email


def _rp_publicado(rp: str | None) -> str:
    """Normaliza RP para el email de resultados."""
    return rp if rp is not None else "DNS"


def _crear_podio_publicado(
    posicion: int,
    atleta_nombre: str,
    rp: str,
) -> PodioPublicado:
    """Crea una entrada de podio para P-11."""
    return PodioPublicado(posicion=posicion, atleta_nombre=atleta_nombre, rp=rp)


async def _obtener_nombre_torneo(
    torneo_id: UUID | None,
    torneo_db_path: str,
    torneo_repo: SQLiteTorneoRepository | None = None,
) -> str:
    """Obtiene nombre de torneo para P-11 con fallback estable."""
    if torneo_id is None:
        return "Torneo sin nombre"
    torneos = torneo_repo or SQLiteTorneoRepository(torneo_db_path)
    torneo = await torneos.find_by_id(torneo_id)
    return torneo.nombre if torneo is not None else f"Torneo {torneo_id}"


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
        algoritmo=AlgoritmoPuntajeFAAS(),
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

    if await _obtener_disciplinas_pendientes_premiacion(
        torneo_id,
        competencia_event_store,
        torneo_db_path,
    ):
        return

    disciplinas = await _obtener_disciplinas_torneo(torneo_id, torneo_db_path)
    if not disciplinas:
        return

    competencias_por_torneo = SQLiteCompetenciasPorTorneo()
    overall_handler = CalcularOverallHandler(ranking_store, competencias_por_torneo)
    await overall_handler.handle(
        CalcularOverallCommand(
            torneo_id=torneo_id,
            disciplinas=disciplinas,
        )
    )


def build_premiacion_precondition(
    competencia_event_store: SQLiteEventStore | None = None,
    torneo_db_path: str | None = None,
) -> Callable[[UUID], Awaitable[None]]:
    """Construye la precondicion para pasar un torneo a premiacion."""
    event_store = competencia_event_store or SQLiteEventStore(
        os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    )
    torneos_path = torneo_db_path or os.getenv("TORNEO_DB_PATH", "data/torneo.db")

    async def _precondition(torneo_id: UUID) -> None:
        pendientes = await _obtener_disciplinas_pendientes_premiacion(
            torneo_id,
            event_store,
            torneos_path,
        )
        if pendientes:
            detalle = ", ".join(pendientes)
            cantidad = len(pendientes)
            etiqueta = "disciplina" if cantidad == 1 else "disciplinas"
            raise PremiacionNoPermitida(
                f"No se puede pasar a premiacion: falta cerrar {cantidad} {etiqueta}: " f"{detalle}"
            )

    return _precondition


def build_ejecucion_precondition(
    competencia_event_store: SQLiteEventStore | None = None,
    torneo_db_path: str | None = None,
    competencia_db_path: str | None = None,
) -> Callable[[UUID], Awaitable[None]]:
    """Construye la precondición para pasar un torneo a ejecución."""
    event_store = competencia_event_store or SQLiteEventStore(
        os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    )
    torneos_path = torneo_db_path or os.getenv("TORNEO_DB_PATH", "data/torneo.db")
    competencias_path = competencia_db_path or os.getenv(
        "COMPETENCIA_DB_PATH", "data/competencia.db"
    )

    async def _precondition(torneo_id: UUID) -> None:
        pendientes = await _obtener_disciplinas_pendientes_ejecucion(
            torneo_id,
            event_store,
            torneos_path,
            competencias_path,
        )
        if pendientes:
            raise EjecucionNoPermitida("No se puede pasar a ejecucion: " + "; ".join(pendientes))

    return _precondition


def build_ejecucion_post_action(
    competencia_event_store: SQLiteEventStore | None = None,
    torneo_db_path: str | None = None,
    competencia_db_path: str | None = None,
) -> Callable[[UUID], Awaitable[None]]:
    """Inicia las competencias listas cuando el torneo entra en ejecución."""
    event_store = competencia_event_store or SQLiteEventStore(
        os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
    )
    torneos_path = torneo_db_path or os.getenv("TORNEO_DB_PATH", "data/torneo.db")
    competencias_path = competencia_db_path or os.getenv(
        "COMPETENCIA_DB_PATH", "data/competencia.db"
    )

    async def _post_action(torneo_id: UUID) -> None:
        disciplinas = await _obtener_disciplinas_torneo(torneo_id, torneos_path)
        if not disciplinas:
            return

        competencias = await ObtenerCompetenciasPorTorneoHandler(
            SQLiteCompetenciasPorTorneo(competencias_path)
        ).handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=torneo_id))
        competencias_por_disciplina = {
            competencia.disciplina: competencia.competencia_id for competencia in competencias
        }
        iniciar_handler = IniciarCompetenciaHandler(event_store)

        for disciplina in disciplinas:
            competencia_id = competencias_por_disciplina.get(disciplina.value)
            if competencia_id is None:
                continue

            events = await event_store.load(f"competencia-{competencia_id}")
            if not events:
                continue

            competencia = Competencia.reconstitute(
                competencia_id=competencia_id,
                disciplina=disciplina,
                events=events,
            )
            if competencia.estado.value != "Confirmada":
                continue

            juez_referencia = next(
                (entrada.juez_id for entrada in competencia.grilla if entrada.juez_id),
                None,
            )
            if juez_referencia is None:
                continue

            await iniciar_handler.handle(
                IniciarCompetenciaCommand(
                    competencia_id=competencia_id,
                    disciplina=disciplina,
                    juez_id=juez_referencia,
                )
            )

    return _post_action


async def _obtener_disciplinas_pendientes_premiacion(
    torneo_id: UUID,
    competencia_event_store: SQLiteEventStore,
    torneo_db_path: str,
) -> list[str]:
    """Retorna disciplinas configuradas que aun no tienen competencia finalizada."""
    disciplinas = await _obtener_disciplinas_torneo(torneo_id, torneo_db_path)
    if not disciplinas:
        return []

    competencias = await ObtenerCompetenciasPorTorneoHandler(SQLiteCompetenciasPorTorneo()).handle(
        ObtenerCompetenciasPorTorneoQuery(torneo_id=torneo_id)
    )
    competencias_por_disciplina = {
        competencia.disciplina: competencia.competencia_id for competencia in competencias
    }

    pendientes: list[str] = []
    for disciplina in disciplinas:
        competencia_id = competencias_por_disciplina.get(disciplina.value)
        if competencia_id is None:
            pendientes.append(disciplina.value)
            continue

        events = await competencia_event_store.load(f"competencia-{competencia_id}")
        if not any(event["event_type"] == "CompetenciaFinalizada" for event in events):
            pendientes.append(disciplina.value)

    return pendientes


async def _obtener_disciplinas_pendientes_ejecucion(
    torneo_id: UUID,
    competencia_event_store: SQLiteEventStore,
    torneo_db_path: str,
    competencia_db_path: str,
) -> list[str]:
    disciplinas = await _obtener_disciplinas_torneo(torneo_id, torneo_db_path)
    if not disciplinas:
        return []

    competencias = await ObtenerCompetenciasPorTorneoHandler(
        SQLiteCompetenciasPorTorneo(competencia_db_path)
    ).handle(ObtenerCompetenciasPorTorneoQuery(torneo_id=torneo_id))
    competencias_por_disciplina = {
        competencia.disciplina: competencia.competencia_id for competencia in competencias
    }

    pendientes: list[str] = []
    for disciplina in disciplinas:
        competencia_id = competencias_por_disciplina.get(disciplina.value)
        if competencia_id is None:
            pendientes.append(f"{disciplina.value}: falta crear la competencia")
            continue

        events = await competencia_event_store.load(f"competencia-{competencia_id}")
        if not events:
            pendientes.append(f"{disciplina.value}: competencia sin configuracion operativa")
            continue

        competencia = Competencia.reconstitute(
            competencia_id=competencia_id,
            disciplina=disciplina,
            events=events,
        )
        if not competencia.grilla_confirmada:
            pendientes.append(f"{disciplina.value}: falta confirmar la grilla")
            continue

        sin_juez = sum(1 for entrada in competencia.grilla if not entrada.juez_id)
        if sin_juez > 0:
            etiqueta = "performance" if sin_juez == 1 else "performances"
            pendientes.append(
                f"{disciplina.value}: faltan jueces en {sin_juez} {etiqueta} de la grilla"
            )

    return pendientes


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


configure_premiacion_precondition(build_premiacion_precondition())
configure_ejecucion_precondition(build_ejecucion_precondition())
configure_ejecucion_post_action(build_ejecucion_post_action())
configure_on_finalizada_callback(
    build_on_finalizada_callback(
        SQLiteEventStore(os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db"))
    )
)


def build_on_ap_registrado_callback(
    *,
    competencias_repo: SQLiteCompetenciasPorTorneo | None = None,
    inscripcion_repo: SQLiteInscripcionRepository | None = None,
) -> Callable[[UUID, UUID, Disciplina, Decimal], Awaitable[None]]:
    async def _callback(
        competencia_id: UUID,
        atleta_id: UUID,
        disciplina: Disciplina,
        valor_ap: Decimal,
    ) -> None:
        competencias = competencias_repo or SQLiteCompetenciasPorTorneo()
        inscripciones = inscripcion_repo or SQLiteInscripcionRepository()
        handler = DeclararAPInscripcionHandler(inscripciones)
        record = await competencias.obtener_por_competencia_id(competencia_id)
        if record is None:
            return
        inscripcion = await inscripciones.find_by_atleta_y_torneo(atleta_id, record.torneo_id)
        if inscripcion is None:
            return
        await handler.handle(
            DeclararAPInscripcionCommand(
                inscripcion_id=inscripcion.inscripcion_id,
                disciplina=disciplina,
                valor_ap=valor_ap,
            )
        )

    return _callback


configure_ap_registrado_callback(build_on_ap_registrado_callback())


@app.get("/health", response_class=JSONResponse)
async def health_check() -> dict[str, str]:
    """Health-check endpoint — verifica que la aplicación está activa."""
    return {"status": "ok"}
