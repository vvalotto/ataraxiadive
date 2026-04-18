from __future__ import annotations

import os
from datetime import date
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from pydantic import BaseModel, field_validator, model_validator

from shared.api.dependencies import OrganizadorDep
from shared.domain.value_objects.disciplina import Disciplina
from torneo.application.commands.asignar_disciplinas import (
    AsignarDisciplinasCommand,
    AsignarDisciplinasHandler,
)
from torneo.application.commands.asignar_juez import AsignarJuezCommand, AsignarJuezHandler
from torneo.application.commands.crear_torneo import CrearTorneoCommand, CrearTorneoHandler
from torneo.application.commands.transicionar_torneo import (
    AbrirInscripcionHandler,
    CancelarTorneoHandler,
    CerrarInscripcionHandler,
    CerrarTorneoHandler,
    IniciarEjecucionHandler,
    IniciarPremiacionHandler,
    TransicionarTorneoCommand,
    VolverAPreparacionHandler,
)
from torneo.application.queries.obtener_disciplinas_juez import ObtenerDisciplinasDeJuezHandler
from torneo.application.queries.obtener_torneo import (
    ListarTorneosHandler,
    ListarTorneosQuery,
    ObtenerTorneoHandler,
    ObtenerTorneoQuery,
)
from torneo.domain.aggregates.torneo import Torneo
from torneo.domain.exceptions import AsignacionNoPermitida, DisciplinaNoEnTorneo, DisciplinaObsoleta
from torneo.infrastructure.repositories.sqlite_torneo_repository import SQLiteTorneoRepository

router = APIRouter(prefix="/torneos", tags=["torneos"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class SedeSchema(BaseModel):
    nombre: str
    ciudad: str
    pais: str


class EntidadOrganizadoraSchema(BaseModel):
    nombre: str
    tipo: str


class CrearTorneoRequest(BaseModel):
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede: SedeSchema
    entidad_organizadora: EntidadOrganizadoraSchema

    @field_validator("nombre")
    @classmethod
    def nombre_no_vacio(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v

    @model_validator(mode="after")
    def fechas_coherentes(self) -> CrearTorneoRequest:
        if self.fecha_fin < self.fecha_inicio:
            raise ValueError("fecha_fin debe ser mayor o igual a fecha_inicio")
        return self


class TorneoResponse(BaseModel):
    torneo_id: UUID
    nombre: str
    descripcion: str
    fecha_inicio: date
    fecha_fin: date
    sede: SedeSchema
    entidad_organizadora: EntidadOrganizadoraSchema
    estado: str

    @classmethod
    def from_torneo(cls, torneo: Torneo) -> TorneoResponse:
        return cls(
            torneo_id=torneo.torneo_id,
            nombre=torneo.nombre,
            descripcion=torneo.descripcion,
            fecha_inicio=torneo.fecha_inicio,
            fecha_fin=torneo.fecha_fin,
            sede=SedeSchema(
                nombre=torneo.sede.nombre,
                ciudad=torneo.sede.ciudad,
                pais=torneo.sede.pais,
            ),
            entidad_organizadora=EntidadOrganizadoraSchema(
                nombre=torneo.entidad_organizadora.nombre,
                tipo=torneo.entidad_organizadora.tipo,
            ),
            estado=torneo.estado.value,
        )


# ── Helpers ───────────────────────────────────────────────────────────────────


def _repo() -> SQLiteTorneoRepository:
    return SQLiteTorneoRepository(os.getenv("TORNEO_DB_PATH", "data/torneo.db"))


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("", status_code=201)
async def crear_torneo(body: CrearTorneoRequest, _: OrganizadorDep) -> JSONResponse:
    repo = _repo()
    handler = CrearTorneoHandler(repo)
    torneo_id = await handler.handle(
        CrearTorneoCommand(
            nombre=body.nombre,
            descripcion=body.descripcion,
            fecha_inicio=body.fecha_inicio,
            fecha_fin=body.fecha_fin,
            sede_nombre=body.sede.nombre,
            sede_ciudad=body.sede.ciudad,
            sede_pais=body.sede.pais,
            entidad_nombre=body.entidad_organizadora.nombre,
            entidad_tipo=body.entidad_organizadora.tipo,
        )
    )
    return JSONResponse(status_code=201, content={"torneo_id": str(torneo_id)})


@router.get("", response_model=list[TorneoResponse])
async def listar_torneos() -> list[TorneoResponse]:
    handler = ListarTorneosHandler(_repo())
    torneos = await handler.handle(ListarTorneosQuery())
    return [TorneoResponse.from_torneo(t) for t in torneos]


@router.get("/{torneo_id}", response_model=TorneoResponse)
async def obtener_torneo(torneo_id: UUID) -> TorneoResponse:
    handler = ObtenerTorneoHandler(_repo())
    torneo = await handler.handle(ObtenerTorneoQuery(torneo_id=torneo_id))
    return TorneoResponse.from_torneo(torneo)


@router.put("/{torneo_id}/abrir-inscripcion", status_code=200)
async def abrir_inscripcion(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await AbrirInscripcionHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/cerrar-inscripcion", status_code=200)
async def cerrar_inscripcion(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await CerrarInscripcionHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/iniciar-ejecucion", status_code=200)
async def iniciar_ejecucion(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await IniciarEjecucionHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/volver-preparacion", status_code=200)
async def volver_preparacion(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await VolverAPreparacionHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/iniciar-premiacion", status_code=200)
async def iniciar_premiacion(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await IniciarPremiacionHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/cerrar", status_code=200)
async def cerrar_torneo(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await CerrarTorneoHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/cancelar", status_code=200)
async def cancelar_torneo(torneo_id: UUID, _: OrganizadorDep) -> JSONResponse:
    await CancelarTorneoHandler(_repo()).handle(TransicionarTorneoCommand(torneo_id))
    return JSONResponse(status_code=200, content={"ok": True})


# ── Disciplinas + Jueces ──────────────────────────────────────────────────────


class AsignarDisciplinasRequest(BaseModel):
    disciplinas: list[str]


class AsignarJuezRequest(BaseModel):
    juez_id: UUID


@router.put("/{torneo_id}/disciplinas", status_code=200)
async def asignar_disciplinas(
    torneo_id: UUID, body: AsignarDisciplinasRequest, _: OrganizadorDep
) -> JSONResponse:
    try:
        disciplinas = frozenset(Disciplina(d) for d in body.disciplinas)
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    try:
        await AsignarDisciplinasHandler(_repo()).handle(
            AsignarDisciplinasCommand(torneo_id=torneo_id, disciplinas=disciplinas)
        )
    except AsignacionNoPermitida as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except DisciplinaObsoleta as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return JSONResponse(status_code=200, content={"ok": True})


@router.put("/{torneo_id}/disciplinas/{disciplina}/juez", status_code=200)
async def asignar_juez(
    torneo_id: UUID, disciplina: str, body: AsignarJuezRequest, _: OrganizadorDep
) -> JSONResponse:
    try:
        disc = Disciplina(disciplina)
    except ValueError:
        return JSONResponse(
            status_code=422, content={"detail": f"Disciplina inválida: {disciplina}"}
        )
    try:
        await AsignarJuezHandler(_repo()).handle(
            AsignarJuezCommand(torneo_id=torneo_id, disciplina=disc, juez_id=body.juez_id)
        )
    except DisciplinaNoEnTorneo as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except AsignacionNoPermitida as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return JSONResponse(status_code=200, content={"juez_id": str(body.juez_id)})


@router.get("/{torneo_id}/disciplinas", status_code=200)
async def listar_disciplinas(torneo_id: UUID) -> JSONResponse:
    handler = ObtenerTorneoHandler(_repo())
    torneo = await handler.handle(ObtenerTorneoQuery(torneo_id=torneo_id))
    data = [
        {"disciplina": dt.disciplina.value, "juez_id": str(dt.juez_id) if dt.juez_id else None}
        for dt in torneo.disciplinas_torneo
    ]
    return JSONResponse(status_code=200, content=data)


@router.get("/{torneo_id}/jueces/{juez_id}/disciplinas", status_code=200)
async def disciplinas_de_juez(torneo_id: UUID, juez_id: UUID) -> JSONResponse:
    disciplinas = await ObtenerDisciplinasDeJuezHandler(_repo()).handle(torneo_id, juez_id)
    return JSONResponse(status_code=200, content=[d.value for d in disciplinas])
