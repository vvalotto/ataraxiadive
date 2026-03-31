from __future__ import annotations

from datetime import date
from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.application.queries.obtener_atleta import ObtenerAtletaHandler
from registro.domain.exceptions import AtletaNoEncontrado, AtletaYaRegistrado
from registro.domain.value_objects.categoria import Categoria
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository

router = APIRouter(prefix="/registro", tags=["registro"])


# ── Schemas ───────────────────────────────────────────────────────────────────


class RegistrarAtletaRequest(BaseModel):
    atleta_id: UUID
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria
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
    brevet: str | None


# ── Helpers de dependencias ───────────────────────────────────────────────────


def _repo() -> SQLiteAtletaRepository:
    return SQLiteAtletaRepository()


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/atletas", status_code=201)
async def registrar_atleta(body: RegistrarAtletaRequest) -> JSONResponse:
    repo = _repo()
    handler = RegistrarAtletaHandler(repo)
    cmd = RegistrarAtletaCommand(
        atleta_id=body.atleta_id,
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        fecha_nacimiento=body.fecha_nacimiento,
        categoria=body.categoria,
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
            brevet=atleta.brevet,
        ).model_dump(mode="json"),
    )
