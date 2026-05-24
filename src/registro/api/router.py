from __future__ import annotations

from collections.abc import Awaitable, Callable
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel, field_validator

from identidad.api.dependencies import get_current_user
from registro.application.commands.cambiar_aceptacion_inscripcion import (
    CambiarAceptacionInscripcionCommand,
    CambiarAceptacionInscripcionHandler,
)
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
from registro.application.commands.actualizar_atleta import (
    ActualizarAtletaCommand,
    ActualizarAtletaHandler,
)
from registro.application.commands.actualizar_juez import (
    ActualizarJuezCommand,
    ActualizarJuezHandler,
)
from registro.application.commands.actualizar_organizador import (
    ActualizarOrganizadorCommand,
    ActualizarOrganizadorHandler,
)
from registro.application.commands.registrar_atleta import (
    RegistrarAtletaCommand,
    RegistrarAtletaHandler,
)
from registro.application.commands.registrar_juez import (
    RegistrarJuezCommand,
    RegistrarJuezHandler,
)
from registro.application.commands.registrar_organizador import (
    RegistrarOrganizadorCommand,
    RegistrarOrganizadorHandler,
)
from registro.application.queries.listar_inscriptos import ListarInscriptosHandler
from registro.application.queries.obtener_atleta import ObtenerAtletaHandler
from registro.application.queries.obtener_juez import ObtenerJuezHandler
from registro.application.queries.obtener_organizador import (
    ObtenerOrganizadorHandler as ObtenerOrganizadorQueryHandler,
)
from registro.application.queries.verificar_completitud_ap import (
    VerificarCompletitudAPHandler,
)
from registro.domain.aggregates.inscripcion import Inscripcion
from registro.domain.exceptions import (
    APIncompletoParaPreparacion,
    AtletaNoEncontrado,
    AtletaYaInscripto,
    AtletaYaRegistrado,
    DisciplinaNoDisponible,
    DisciplinaNoInscripta,
    InscripcionNoEncontrada,
    JuezNoEncontrado,
    JuezYaRegistrado,
    OrganizadorNoEncontrado,
    OrganizadorYaRegistrado,
    PlazoCancelacionVencido,
    TorneoNoDisponible,
)
from registro.domain.ports.adjunto_storage_port import AdjuntoStoragePort
from registro.domain.value_objects.categoria import Categoria
from registro.domain.value_objects.estado_aceptacion import EstadoAceptacion
from registro.domain.value_objects.estado_inscripcion import EstadoInscripcion
from registro.infrastructure.acl.sqlite_torneo_consulta import SQLiteTorneoConsulta
from registro.infrastructure.adjuntos.local_adjunto_storage import LocalAdjuntoStorage
from registro.infrastructure.repositories.sqlite_atleta_repository import SQLiteAtletaRepository
from registro.infrastructure.repositories.sqlite_inscripcion_repository import (
    SQLiteInscripcionRepository,
)
from registro.infrastructure.repositories.sqlite_juez_repository import SQLiteJuezRepository
from registro.infrastructure.repositories.sqlite_organizador_repository import (
    SQLiteOrganizadorRepository,
)
from shared.api.dependencies import AtletaDep, JuezDep, OrganizadorDep
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
    nombre: str
    apellido: str
    email: str
    fecha_nacimiento: date
    categoria: Categoria | None = None
    club: str | None = None
    brevet: str | None = None
    dni: str | None = None
    telefono: str | None = None

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
    fecha_nacimiento: date | None = None
    categoria: Categoria | None
    club: str | None
    brevet: str | None
    dni: str | None
    telefono: str | None


class ActualizarAtletaMeRequest(BaseModel):
    nombre: str | None = None
    apellido: str | None = None
    categoria: Categoria | None = None
    club: str | None = None
    fecha_nacimiento: date | None = None
    brevet: str | None = None
    dni: str | None = None
    telefono: str | None = None


# ── Schemas — Juez ───────────────────────────────────────────────────────────


class RegistrarJuezRequest(BaseModel):
    numero_licencia: str | None = None
    federacion: str | None = None


class JuezResponse(BaseModel):
    juez_id: UUID
    email: str
    numero_licencia: str | None
    federacion: str | None


class ActualizarJuezMeRequest(BaseModel):
    numero_licencia: str | None = None
    federacion: str | None = None


# ── Schemas — Organizador ────────────────────────────────────────────────────


class RegistrarOrganizadorRequest(BaseModel):
    nombre_organizacion: str | None = None


class OrganizadorResponse(BaseModel):
    organizador_id: UUID
    email: str
    nombre_organizacion: str | None


class ActualizarOrganizadorMeRequest(BaseModel):
    nombre_organizacion: str | None = None


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
    estado_aceptacion: EstadoAceptacion
    fecha_inscripcion: datetime
    nombre: str
    apellido: str
    categoria: Categoria | None
    club: str | None
    disciplinas: list[EstadoAPDisciplinaResponse]


class DeclararAPInscripcionRequest(BaseModel):
    disciplina: Disciplina
    valor_ap: Decimal


class CambiarAceptacionRequest(BaseModel):
    estado: EstadoAceptacion


class InscripcionDetalleResponse(BaseModel):
    inscripcion_id: UUID
    atleta_id: UUID
    torneo_id: UUID
    estado: EstadoInscripcion
    estado_aceptacion: EstadoAceptacion
    fecha_inscripcion: datetime
    nombre: str
    apellido: str
    categoria: Categoria | None
    club: str | None
    brevet: str | None
    dni: str | None
    telefono: str | None
    apto_medico_url: str | None
    constancia_pago_url: str | None


# ── Helpers de dependencias ───────────────────────────────────────────────────


def _repo() -> SQLiteAtletaRepository:
    return SQLiteAtletaRepository()


def _juez_repo() -> SQLiteJuezRepository:
    return SQLiteJuezRepository()


def _organizador_repo() -> SQLiteOrganizadorRepository:
    return SQLiteOrganizadorRepository()


def _inscripcion_repo() -> SQLiteInscripcionRepository:
    return SQLiteInscripcionRepository()


def _torneo_consulta() -> SQLiteTorneoConsulta:
    return SQLiteTorneoConsulta()


def _adjunto_storage() -> AdjuntoStoragePort:
    return LocalAdjuntoStorage()


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
    storage: AdjuntoStoragePort | None = None,
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

    ruta = (storage or _adjunto_storage()).guardar(
        inscripcion_id=inscripcion_id,
        nombre_archivo=nombre_archivo,
        filename_original=archivo.filename,
        contenido=contenido,
    )

    getattr(inscripcion, metodo_adjunto)(ruta)
    await _inscripcion_repo().save(inscripcion)

    return JSONResponse(status_code=200, content={"path": ruta})


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
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        fecha_nacimiento=body.fecha_nacimiento,
        categoria=body.categoria,
        club=body.club,
        brevet=body.brevet,
        dni=body.dni,
        telefono=body.telefono,
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
            dni=atleta.dni,
            telefono=atleta.telefono,
        ).model_dump(mode="json"),
    )


@router.patch("/atletas/me", status_code=200)
async def actualizar_atleta_me(
    body: ActualizarAtletaMeRequest, current_user: AtletaDep
) -> JSONResponse:
    email: str = current_user["email"]
    try:
        atleta = await ActualizarAtletaHandler(_repo()).handle(
            ActualizarAtletaCommand(
                email=email,
                nombre=body.nombre,
                apellido=body.apellido,
                categoria=body.categoria,
                club=body.club,
                fecha_nacimiento=body.fecha_nacimiento,
                brevet=body.brevet,
                dni=body.dni,
                telefono=body.telefono,
            )
        )
    except AtletaNoEncontrado as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
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
            dni=atleta.dni,
            telefono=atleta.telefono,
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
            dni=atleta.dni,
            telefono=atleta.telefono,
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


@router.get("/torneos/{torneo_id}/inscriptos-info", status_code=200)
async def listar_inscriptos_info_publico(torneo_id: UUID) -> JSONResponse:
    """Información pública de inscriptos: atleta_id, nombre completo y club. Sin auth."""
    inscripciones = await _inscripcion_repo().find_active_by_torneo(torneo_id)
    atletas_repo = _repo()
    seen: set[str] = set()
    content = []
    for inscripcion in inscripciones:
        key = str(inscripcion.atleta_id)
        if key in seen:
            continue
        seen.add(key)
        atleta = await atletas_repo.find_by_id(inscripcion.atleta_id)
        if atleta is None:
            continue
        content.append(
            {
                "atleta_id": key,
                "nombre": f"{atleta.nombre} {atleta.apellido}".strip(),
                "club": atleta.club or "",
            }
        )
    return JSONResponse(status_code=200, content=content)


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
                estado_aceptacion=inscripcion.estado_aceptacion,
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


@router.get("/inscripciones/{inscripcion_id}/adjuntos/{tipo}", status_code=200)
async def descargar_adjunto_inscripcion(
    inscripcion_id: UUID,
    tipo: str,
    _: OrganizadorDep,
) -> FileResponse:
    if tipo not in ("apto_medico", "constancia_pago"):
        return JSONResponse(status_code=400, content={"detail": "Tipo de adjunto inválido"})
    inscripcion = await _inscripcion_repo().find_by_id(inscripcion_id)
    if inscripcion is None:
        return JSONResponse(status_code=404, content={"detail": "Inscripción no encontrada"})
    ruta = (
        inscripcion.apto_medico_path if tipo == "apto_medico" else inscripcion.constancia_pago_path
    )
    if not ruta:
        return JSONResponse(status_code=404, content={"detail": "Adjunto no disponible"})
    path = Path(ruta)
    if not path.exists():
        return JSONResponse(
            status_code=404, content={"detail": "Archivo no encontrado en el servidor"}
        )
    filename = f"{tipo}_{inscripcion_id}{path.suffix}"
    return FileResponse(path=path, filename=filename, media_type="application/octet-stream")


@router.patch("/inscripciones/{inscripcion_id}/aceptacion", status_code=200)
async def cambiar_aceptacion_inscripcion(
    inscripcion_id: UUID,
    body: CambiarAceptacionRequest,
    _: OrganizadorDep,
) -> JSONResponse:
    handler = CambiarAceptacionInscripcionHandler(_inscripcion_repo())
    try:
        await handler.handle(
            CambiarAceptacionInscripcionCommand(
                inscripcion_id=inscripcion_id,
                nuevo_estado=body.estado,
            )
        )
    except InscripcionNoEncontrada as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    return JSONResponse(status_code=200, content={"ok": True, "estado": body.estado.value})


@router.get("/inscripciones/{inscripcion_id}/detalle", status_code=200)
async def obtener_inscripcion_detalle(
    inscripcion_id: UUID,
    _: OrganizadorDep,
) -> JSONResponse:
    inscripcion = await _inscripcion_repo().find_by_id(inscripcion_id)
    if inscripcion is None:
        return JSONResponse(status_code=404, content={"detail": "Inscripción no encontrada"})
    atleta = await _repo().find_by_id(inscripcion.atleta_id)
    if atleta is None:
        return JSONResponse(status_code=404, content={"detail": "Atleta no encontrado"})
    return JSONResponse(
        status_code=200,
        content=InscripcionDetalleResponse(
            inscripcion_id=inscripcion.inscripcion_id,
            atleta_id=inscripcion.atleta_id,
            torneo_id=inscripcion.torneo_id,
            estado=inscripcion.estado,
            estado_aceptacion=inscripcion.estado_aceptacion,
            fecha_inscripcion=inscripcion.fecha_inscripcion,
            nombre=atleta.nombre,
            apellido=atleta.apellido,
            categoria=atleta.categoria,
            club=atleta.club,
            brevet=atleta.brevet,
            dni=atleta.dni,
            telefono=atleta.telefono,
            apto_medico_url=inscripcion.apto_medico_path,
            constancia_pago_url=inscripcion.constancia_pago_path,
        ).model_dump(mode="json"),
    )


# ── Endpoints — Juez ──────────────────────────────────────────────────────────


@router.post("/jueces", status_code=201)
async def registrar_juez(body: RegistrarJuezRequest, current_user: JuezDep) -> JSONResponse:
    repo = _juez_repo()
    handler = RegistrarJuezHandler(repo)
    try:
        juez_id = await handler.handle(
            RegistrarJuezCommand(
                email=current_user["email"],
                numero_licencia=body.numero_licencia,
                federacion=body.federacion,
            )
        )
    except JuezYaRegistrado:
        return JSONResponse(status_code=409, content={"detail": "Perfil de juez ya registrado"})
    juez = await repo.find_by_id(juez_id)
    return JSONResponse(
        status_code=201,
        content=JuezResponse(
            juez_id=juez.juez_id,  # type: ignore[union-attr]
            email=juez.email,  # type: ignore[union-attr]
            numero_licencia=juez.numero_licencia,  # type: ignore[union-attr]
            federacion=juez.federacion,  # type: ignore[union-attr]
        ).model_dump(mode="json"),
    )


@router.get("/jueces/me", status_code=200)
async def obtener_juez_me(current_user: JuezDep) -> JSONResponse:
    try:
        juez = await ObtenerJuezHandler(_juez_repo()).handle(current_user["email"])
    except JuezNoEncontrado:
        return JSONResponse(status_code=404, content={"detail": "Juez no encontrado"})
    return JSONResponse(
        content=JuezResponse(
            juez_id=juez.juez_id,
            email=juez.email,
            numero_licencia=juez.numero_licencia,
            federacion=juez.federacion,
        ).model_dump(mode="json")
    )


@router.patch("/jueces/me", status_code=200)
async def actualizar_juez_me(body: ActualizarJuezMeRequest, current_user: JuezDep) -> JSONResponse:
    try:
        juez = await ActualizarJuezHandler(_juez_repo()).handle(
            ActualizarJuezCommand(
                email=current_user["email"],
                numero_licencia=body.numero_licencia,
                federacion=body.federacion,
            )
        )
    except JuezNoEncontrado:
        return JSONResponse(status_code=404, content={"detail": "Juez no encontrado"})
    return JSONResponse(
        content=JuezResponse(
            juez_id=juez.juez_id,
            email=juez.email,
            numero_licencia=juez.numero_licencia,
            federacion=juez.federacion,
        ).model_dump(mode="json")
    )


# ── Endpoints — Organizador ───────────────────────────────────────────────────


@router.post("/organizadores", status_code=201)
async def registrar_organizador(
    body: RegistrarOrganizadorRequest, current_user: OrganizadorDep
) -> JSONResponse:
    repo = _organizador_repo()
    try:
        organizador_id = await RegistrarOrganizadorHandler(repo).handle(
            RegistrarOrganizadorCommand(
                email=current_user["email"],
                nombre_organizacion=body.nombre_organizacion,
            )
        )
    except OrganizadorYaRegistrado:
        return JSONResponse(
            status_code=409, content={"detail": "Perfil de organizador ya registrado"}
        )
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    organizador = await repo.find_by_id(organizador_id)
    return JSONResponse(
        status_code=201,
        content=OrganizadorResponse(
            organizador_id=organizador.organizador_id,  # type: ignore[union-attr]
            email=organizador.email,  # type: ignore[union-attr]
            nombre_organizacion=organizador.nombre_organizacion,  # type: ignore[union-attr]
        ).model_dump(mode="json"),
    )


@router.get("/organizadores/me", status_code=200)
async def obtener_organizador_me(current_user: OrganizadorDep) -> JSONResponse:
    try:
        organizador = await ObtenerOrganizadorQueryHandler(_organizador_repo()).handle(
            current_user["email"]
        )
    except OrganizadorNoEncontrado:
        return JSONResponse(status_code=404, content={"detail": "Organizador no encontrado"})
    return JSONResponse(
        content=OrganizadorResponse(
            organizador_id=organizador.organizador_id,
            email=organizador.email,
            nombre_organizacion=organizador.nombre_organizacion,
        ).model_dump(mode="json")
    )


@router.patch("/organizadores/me", status_code=200)
async def actualizar_organizador_me(
    body: ActualizarOrganizadorMeRequest, current_user: OrganizadorDep
) -> JSONResponse:
    email: str = current_user["email"]
    # Patch parcial: si el campo no fue enviado en el JSON, preservar valor actual.
    # Si fue enviado (incluso null), actualizar al valor recibido.
    if "nombre_organizacion" not in body.model_fields_set:
        organizador_actual = await _organizador_repo().find_by_email(email)
        if organizador_actual is None:
            return JSONResponse(status_code=404, content={"detail": "Organizador no encontrado"})
        nombre_final = organizador_actual.nombre_organizacion
    else:
        nombre_final = body.nombre_organizacion

    try:
        organizador = await ActualizarOrganizadorHandler(_organizador_repo()).handle(
            ActualizarOrganizadorCommand(
                email=email,
                nombre_organizacion=nombre_final,
            )
        )
    except OrganizadorNoEncontrado:
        return JSONResponse(status_code=404, content={"detail": "Organizador no encontrado"})
    except ValueError as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    return JSONResponse(
        content=OrganizadorResponse(
            organizador_id=organizador.organizador_id,
            email=organizador.email,
            nombre_organizacion=organizador.nombre_organizacion,
        ).model_dump(mode="json")
    )
