from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date, datetime
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pydantic import BaseModel, field_validator

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
from registro.application.queries.listar_inscriptos_detalle import ListarInscriptosDetalleHandler
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


class InscriptoDetalleResponse(BaseModel):
    inscripcion_id: UUID
    atleta_id: UUID
    nombre: str
    apellido: str
    categoria: str
    club: str
    disciplinas: list[str]
    estado: str


# ── Helpers de dependencias ───────────────────────────────────────────────────


def _repo() -> SQLiteAtletaRepository:
    return SQLiteAtletaRepository()


def _inscripcion_repo() -> SQLiteInscripcionRepository:
    return SQLiteInscripcionRepository()


def _torneo_consulta() -> SQLiteTorneoConsulta:
    return SQLiteTorneoConsulta()


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


@router.get("/torneos/{torneo_id}/inscriptos-detalle", status_code=200)
async def listar_inscriptos_detalle(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    handler = ListarInscriptosDetalleHandler(_inscripcion_repo(), _repo())
    inscriptos = await handler.handle(torneo_id)
    return JSONResponse(
        status_code=200,
        content=[
            InscriptoDetalleResponse(
                inscripcion_id=i.inscripcion_id,
                atleta_id=i.atleta_id,
                nombre=i.nombre,
                apellido=i.apellido,
                categoria=i.categoria,
                club=i.club,
                disciplinas=i.disciplinas,
                estado=i.estado,
            ).model_dump(mode="json")
            for i in inscriptos
        ],
    )


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
