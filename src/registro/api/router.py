from __future__ import annotations

import os
from collections.abc import Awaitable, Callable
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from competencia.domain.aggregates.performance import Performance
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import (
    SQLiteCompetenciasPorTorneo,
)
from registro.application.commands.cancelar_inscripcion import (
    CancelarInscripcionCommand,
    CancelarInscripcionHandler,
)
from registro.application.commands.inscribir_atleta import (
    InscribirAtletaCommand,
    InscribirAtletaHandler,
)
from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.application.queries.listar_inscriptos import ListarInscriptosHandler
from registro.application.queries.obtener_atleta import ObtenerAtletaHandler
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import (
    AtletaNoEncontrado,
    AtletaYaInscripto,
    AtletaYaRegistrado,
    DisciplinaNoDisponible,
    InscripcionNoEncontrada,
    PlazoCancelacionVencido,
    TorneoNoDisponible,
)
from registro.domain.value_objects.categoria import Categoria
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from registro.infrastructure.acl.sqlite_torneo_consulta import SQLiteTorneoConsulta
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from shared.api.dependencies import AtletaDep, OrganizadorDep
from shared.domain.value_objects.disciplina import Disciplina
from shared.infrastructure.event_store.sqlite_event_store import SQLiteEventStore

router = APIRouter(prefix="/registro", tags=["registro"])

_on_inscripcion_confirmada_callback: Callable[[Inscripcion], Awaitable[None]] | None = None


def configure_inscripcion_notificaciones(
    callback: Callable[[Inscripcion], Awaitable[None]] | None,
) -> None:
    global _on_inscripcion_confirmada_callback
    _on_inscripcion_confirmada_callback = callback


# ── Schemas ───────────────────────────────────────────────────────────────────


class RegistrarAtletaRequest(BaseModel):
    atleta_id: UUID
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
    club: str
    brevet: str | None = None

    @field_validator("nombre", "apellido")
    @classmethod
    def no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("no puede ser vacío")
        return v


class AtletaResponse(BaseModel):
    atleta_id: UUID
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
    club: str
    brevet: str | None


# ── Schemas — Inscripcion ─────────────────────────────────────────────────────


class InscribirAtletaRequest(BaseModel):
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: list[Disciplina]


class InscripcionResponse(BaseModel):
    inscripcion_id: UUID
    atleta_id: UUID
    torneo_id: UUID
    disciplinas: list[str]
    estado: EstadoInscripcion
    fecha_inscripcion: datetime


class EstadoAPDisciplinaResponse(BaseModel):
    disciplina: str
    ap: str | None
    unidad: str | None


class InscriptoDetalleResponse(BaseModel):
    inscripcion_id: UUID
    atleta_id: UUID
    torneo_id: UUID
    estado: EstadoInscripcion
    fecha_inscripcion: datetime
    nombre: str
    apellido: str
    categoria: Categoria
    club: str
    disciplinas: list[EstadoAPDisciplinaResponse]


# ── Helpers de dependencias ───────────────────────────────────────────────────


def _repo() -> SQLiteAtletaRepository:
    return SQLiteAtletaRepository()


def _inscripcion_repo() -> SQLiteInscripcionRepository:
    return SQLiteInscripcionRepository()


def _torneo_consulta() -> SQLiteTorneoConsulta:
    return SQLiteTorneoConsulta()


def _competencias_por_torneo_repo() -> SQLiteCompetenciasPorTorneo:
    return SQLiteCompetenciasPorTorneo()


def _competencia_event_store() -> SQLiteEventStore:
    return SQLiteEventStore(os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db"))


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return format(normalized, "f")


async def _load_ap_por_torneo(
    torneo_id: UUID,
) -> dict[tuple[UUID, str], tuple[str | None, str | None]]:
    competencias = await _competencias_por_torneo_repo().listar_por_torneo(torneo_id)
    event_store = _competencia_event_store()
    ap_por_clave: dict[tuple[UUID, str], tuple[str | None, str | None]] = {}

    for competencia in competencias:
        prefix = f"performance-{competencia.competencia_id}-"
        for stream_events in await event_store.load_all_streams_with_prefix(prefix):
            if not stream_events:
                continue
            performance = Performance.reconstitute(stream_events)
            ap = performance.ap
            ap_por_clave[(performance.participante_id, competencia.disciplina)] = (
                _format_decimal(ap.valor) if ap else None,
                ap.unidad.value if ap else None,
            )

    return ap_por_clave


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/atletas", status_code=201)
async def registrar_atleta(body: RegistrarAtletaRequest, _: AtletaDep) -> JSONResponse:
    repo = _repo()
    handler = RegistrarAtletaHandler(repo)
    cmd = RegistrarAtletaCommand(
        atleta_id=body.atleta_id,
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        fecha_nacimiento=body.fecha_nacimiento,
        categoria=body.categoria,
        club=body.club,
        brevet=body.brevet,
    )
    try:
        atleta_id = await handler.handle(cmd)
    except AtletaYaRegistrado as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    return JSONResponse(status_code=201, content={"atleta_id": str(atleta_id)})


@router.get("/atletas/me", status_code=200)
async def obtener_atleta_me(current_user: AtletaDep) -> JSONResponse:
    email: str = current_user["email"]
    repo = _repo()
    atleta = await repo.find_by_email(email)
    if atleta is None:
        return JSONResponse(status_code=404, content={"detail": "Atleta no encontrado"})
    return JSONResponse(
        status_code=200,
        content=AtletaResponse(
            atleta_id=atleta.atleta_id,
            nombre=atleta.nombre,
            apellido=atleta.apellido,
            email=atleta.email,
            fecha_nacimiento=atleta.fecha_nacimiento,
            categoria=atleta.categoria,
            club=atleta.club,
            brevet=atleta.brevet,
        ).model_dump(mode="json"),
    )


@router.get("/atletas/{atleta_id}", status_code=200)
async def obtener_atleta(atleta_id: UUID) -> JSONResponse:
    repo = _repo()
    handler = ObtenerAtletaHandler(repo)
    try:
        atleta = await handler.handle(atleta_id)
    except AtletaNoEncontrado as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    return JSONResponse(
        status_code=200,
        content=AtletaResponse(
            atleta_id=atleta.atleta_id,
            nombre=atleta.nombre,
            apellido=atleta.apellido,
            email=atleta.email,
            fecha_nacimiento=atleta.fecha_nacimiento,
            categoria=atleta.categoria,
            club=atleta.club,
            brevet=atleta.brevet,
        ).model_dump(mode="json"),
    )


# ── Endpoints — Inscripcion ───────────────────────────────────────────────────


@router.post("/inscripciones", status_code=201)
async def inscribir_atleta(body: InscribirAtletaRequest, _: AtletaDep) -> JSONResponse:
    handler = InscribirAtletaHandler(
        _inscripcion_repo(),
        _torneo_consulta(),
        on_inscripcion_confirmada=_on_inscripcion_confirmada_callback,
    )
    cmd = InscribirAtletaCommand(
        atleta_id=body.atleta_id,
        torneo_id=body.torneo_id,
        disciplinas=frozenset(body.disciplinas),
    )
    try:
        inscripcion_id = await handler.handle(cmd)
    except TorneoNoDisponible as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except DisciplinaNoDisponible as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except AtletaYaInscripto as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    return JSONResponse(status_code=201, content={"inscripcion_id": str(inscripcion_id)})


@router.delete("/inscripciones/{inscripcion_id}", status_code=200)
async def cancelar_inscripcion(inscripcion_id: UUID, _: AtletaDep) -> JSONResponse:
    handler = CancelarInscripcionHandler(_inscripcion_repo(), _torneo_consulta())
    cmd = CancelarInscripcionCommand(
        inscripcion_id=inscripcion_id,
        fecha_actual=date.today(),
    )
    try:
        await handler.handle(cmd)
    except InscripcionNoEncontrada as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except PlazoCancelacionVencido as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return JSONResponse(status_code=200, content={"ok": True})


@router.get("/torneos/{torneo_id}/inscriptos", status_code=200)
async def listar_inscriptos(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    handler = ListarInscriptosHandler(_inscripcion_repo())
    inscripciones = await handler.handle(torneo_id)
    return JSONResponse(
        status_code=200,
        content=[
            InscripcionResponse(
                inscripcion_id=i.inscripcion_id,
                atleta_id=i.atleta_id,
                torneo_id=i.torneo_id,
                disciplinas=[d.value for d in i.disciplinas],
                estado=i.estado,
                fecha_inscripcion=i.fecha_inscripcion,
            ).model_dump(mode="json")
            for i in inscripciones
        ],
    )


@router.get("/atletas/{atleta_id}/inscripciones", status_code=200)
async def listar_inscripciones_de_atleta(atleta_id: UUID, _: AtletaDep) -> JSONResponse:
    inscripciones = await _inscripcion_repo().find_by_atleta(atleta_id)
    return JSONResponse(
        status_code=200,
        content=[
            InscripcionResponse(
                inscripcion_id=i.inscripcion_id,
                atleta_id=i.atleta_id,
                torneo_id=i.torneo_id,
                disciplinas=[d.value for d in i.disciplinas],
                estado=i.estado,
                fecha_inscripcion=i.fecha_inscripcion,
            ).model_dump(mode="json")
            for i in inscripciones
        ],
    )


@router.get("/torneos/{torneo_id}/inscriptos-detalle", status_code=200)
async def listar_inscriptos_detalle(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    inscripciones = await _inscripcion_repo().find_active_by_torneo(torneo_id)
    atletas_repo = _repo()
    ap_por_clave = await _load_ap_por_torneo(torneo_id)

    content = []
    for inscripcion in inscripciones:
        atleta = await atletas_repo.find_by_id(inscripcion.atleta_id)
        if atleta is None:
            continue

        disciplinas = []
        for disciplina in sorted(inscripcion.disciplinas, key=lambda item: item.value):
            ap, unidad = ap_por_clave.get((inscripcion.atleta_id, disciplina.value), (None, None))
            disciplinas.append(
                EstadoAPDisciplinaResponse(
                    disciplina=disciplina.value,
                    ap=ap,
                    unidad=unidad,
                )
            )

        content.append(
            InscriptoDetalleResponse(
                inscripcion_id=inscripcion.inscripcion_id,
                atleta_id=inscripcion.atleta_id,
                torneo_id=inscripcion.torneo_id,
                estado=inscripcion.estado,
                fecha_inscripcion=inscripcion.fecha_inscripcion,
                nombre=atleta.nombre,
                apellido=atleta.apellido,
                categoria=atleta.categoria,
                club=atleta.club,
                disciplinas=disciplinas,
            ).model_dump(mode="json")
        )

    return JSONResponse(status_code=200, content=content)
