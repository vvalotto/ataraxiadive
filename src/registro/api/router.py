from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from identidad.api.dependencies import get_current_user
from registro.application.commands.cancelar_inscripcion import (
    CancelarInscripcionCommand,
    CancelarInscripcionHandler,
)
from registro.application.commands.declarar_ap_inscripcion import (
    DeclararAPInscripcionCommand,
    DeclararAPInscripcionHandler,
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
from registro.application.queries.verificar_completitud_ap import (
    VerificarCompletitudAPHandler,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import (
    APIncompletoParaPreparacion,
    APYaDeclarado,
    AtletaNoEncontrado,
    AtletaYaInscripto,
    AtletaYaRegistrado,
    DisciplinaNoDisponible,
    DisciplinaNoInscripta,
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
CurrentUserDep = Annotated[dict, Depends(get_current_user)]

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


class DeclararAPInscripcionRequest(BaseModel):
    disciplina: Disciplina
    valor_ap: Decimal


# ── Helpers de dependencias ───────────────────────────────────────────────────


def _repo() -> SQLiteAtletaRepository:
    return SQLiteAtletaRepository()


def _inscripcion_repo() -> SQLiteInscripcionRepository:
    return SQLiteInscripcionRepository()


def _torneo_consulta() -> SQLiteTorneoConsulta:
    return SQLiteTorneoConsulta()


def _format_decimal(value: Decimal | None) -> str | None:
    if value is None:
        return None
    normalized = value.normalize()
    return format(normalized, "f")


async def _subir_adjunto_inscripcion(
    inscripcion_id: UUID,
    archivo: UploadFile,
    nombre_archivo: str,
    metodo_adjunto: str,
) -> JSONResponse:
    max_size = 10 * 1024 * 1024
    contenido = await archivo.read()
    if len(contenido) > max_size:
        return JSONResponse(
            status_code=413,
            content={"detail": "Archivo demasiado grande (máx 10 MB)"},
        )

    inscripcion = await _inscripcion_repo().find_by_id(inscripcion_id)
    if inscripcion is None:
        return JSONResponse(status_code=404, content={"detail": "Inscripción no encontrada"})

    extension = Path(archivo.filename or "").suffix or ".bin"
    directorio = Path("data/adjuntos") / str(inscripcion_id)
    directorio.mkdir(parents=True, exist_ok=True)
    ruta = directorio / f"{nombre_archivo}{extension}"
    ruta.write_bytes(contenido)

    getattr(inscripcion, metodo_adjunto)(str(ruta))
    await _inscripcion_repo().save(inscripcion)

    return JSONResponse(status_code=200, content={"path": str(ruta)})


async def _load_ap_por_torneo(
    torneo_id: UUID,
) -> dict[tuple[UUID, str], tuple[str | None, str | None]]:
    ap_por_clave: dict[tuple[UUID, str], tuple[str | None, str | None]] = {}
    for inscripcion in await _inscripcion_repo().find_active_by_torneo(torneo_id):
        for disciplina, ap in inscripcion.ap_por_disciplina.items():
            ap_por_clave[(inscripcion.atleta_id, disciplina.value)] = (
                _format_decimal(ap.valor),
                ap.unidad.value,
            )
    return ap_por_clave


def build_cierre_inscripcion_precondition(
    inscripcion_repo: SQLiteInscripcionRepository | None = None,
    atleta_repo: SQLiteAtletaRepository | None = None,
) -> Callable[[UUID], Awaitable[None]]:
    async def _precondition(torneo_id: UUID) -> None:
        handler = VerificarCompletitudAPHandler(
            inscripcion_repo or _inscripcion_repo(),
            atleta_repo or _repo(),
        )
        faltantes = await handler.obtener_faltantes(torneo_id)
        if not faltantes:
            return
        detalle = ", ".join(
            f"{faltante.atleta_nombre} ({faltante.disciplina})" for faltante in faltantes[:5]
        )
        if len(faltantes) > 5:
            detalle = f"{detalle}, y {len(faltantes) - 5} más"
        raise APIncompletoParaPreparacion(
            f"Faltan AP por completar para cerrar inscripción: {detalle}"
        )

    return _precondition


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


@router.get("/inscripciones/{inscripcion_id}/ap", status_code=200)
async def obtener_ap_inscripcion(
    inscripcion_id: UUID,
    disciplina: Disciplina,
    _: CurrentUserDep,
) -> JSONResponse:
    inscripcion = await _inscripcion_repo().find_by_id(inscripcion_id)
    if inscripcion is None:
        return JSONResponse(status_code=404, content={"detail": "Inscripción no encontrada"})
    ap = inscripcion.obtener_ap(disciplina)
    return JSONResponse(
        status_code=200,
        content={
            "disciplina": disciplina.value,
            "ap": _format_decimal(ap.valor) if ap else None,
            "unidad": ap.unidad.value if ap else None,
        },
    )


@router.put("/inscripciones/{inscripcion_id}/ap", status_code=200)
async def declarar_ap_inscripcion(
    inscripcion_id: UUID,
    body: DeclararAPInscripcionRequest,
    _: CurrentUserDep,
) -> JSONResponse:
    handler = DeclararAPInscripcionHandler(_inscripcion_repo())
    try:
        await handler.handle(
            DeclararAPInscripcionCommand(
                inscripcion_id=inscripcion_id,
                disciplina=body.disciplina,
                valor_ap=body.valor_ap,
            )
        )
    except InscripcionNoEncontrada as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except DisciplinaNoInscripta as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except APYaDeclarado as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    inscripcion = await _inscripcion_repo().find_by_id(inscripcion_id)
    assert inscripcion is not None
    ap = inscripcion.obtener_ap(body.disciplina)
    return JSONResponse(
        status_code=200,
        content={
            "disciplina": body.disciplina.value,
            "ap": _format_decimal(ap.valor) if ap else None,
            "unidad": ap.unidad.value if ap else None,
        },
    )


@router.post("/inscripciones/{inscripcion_id}/apto-medico", status_code=200)
async def subir_apto_medico(
    inscripcion_id: UUID,
    archivo: UploadFile,
    _: AtletaDep,
) -> JSONResponse:
    return await _subir_adjunto_inscripcion(
        inscripcion_id,
        archivo,
        "apto_medico",
        "adjuntar_apto_medico",
    )


@router.post("/inscripciones/{inscripcion_id}/constancia-pago", status_code=200)
async def subir_constancia_pago(
    inscripcion_id: UUID,
    archivo: UploadFile,
    _: AtletaDep,
) -> JSONResponse:
    return await _subir_adjunto_inscripcion(
        inscripcion_id,
        archivo,
        "constancia_pago",
        "adjuntar_constancia_pago",
    )
