from __future__ import annotations

import os
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from identidad.api.dependencies import (
    OrganizadorDep,
    get_current_user,
    get_email_sender,
    get_password_hasher,
    get_perfil_registro,
    get_token_service,
    get_usuario_repository,
)
from identidad.application.commands.agregar_rol_usuario import (
    AgregarRolUsuarioCommand,
    AgregarRolUsuarioHandler,
)
from identidad.application.commands.autenticar_usuario import (
    AutenticarUsuarioCommand,
    AutenticarUsuarioHandler,
    RoleSelectionRequired,
    TokenResponse,
)
from identidad.application.commands.cambiar_password import (
    CambiarPasswordCommand,
    CambiarPasswordHandler,
)
from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.application.commands.reset_password import (
    ResetPasswordCommand,
    ResetPasswordHandler,
)
from identidad.application.commands.solicitar_reset_password import (
    SolicitarResetPasswordCommand,
    SolicitarResetPasswordHandler,
)
from identidad.domain.exceptions import (
    CampoRequerido,
    CredencialesInvalidas,
    PasswordActualIncorrecto,
    PasswordDemasiadoCorto,
    RolNoEncontrado,
    RolNoPermitido,
    RolNoRemovible,
    RolYaAsignado,
    TokenResetInvalido,
    UltimoRolNoRemovible,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)
from identidad.domain.ports.password_hashing_port import PasswordHashingPort
from identidad.domain.ports.perfil_registro_port import PerfilRegistroPort
from identidad.domain.ports.token_service_port import TokenServicePort
from identidad.domain.ports.usuario_repository_port import UsuarioRepositoryPort
from identidad.domain.value_objects.rol import Rol
from notificaciones.domain.ports.email_port import EmailPort

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Schemas ──────────────────────────────────────────────────────────────────


class RegistroRequest(BaseModel):
    nombre: str
    apellido: str
    email: str
    password: str
    roles: list[Rol]
    numero_licencia: str | None = None
    federacion: str | None = None
    nombre_organizacion: str | None = None

    @field_validator("nombre", "apellido")
    @classmethod
    def required_trimmed(cls, v: str, info) -> str:  # type: ignore[no-untyped-def]
        normalizado = v.strip()
        if not normalizado:
            raise ValueError(f"El {info.field_name} es requerido")
        return normalizado

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v

    @field_validator("roles")
    @classmethod
    def roles_not_empty(cls, v: list[Rol]) -> list[Rol]:
        if not v:
            raise ValueError("Se debe especificar al menos un rol")
        return v


class LoginRequest(BaseModel):
    email: str
    password: str
    rol_elegido: Rol | None = None


class CambiarPasswordRequest(BaseModel):
    password_actual: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class SolicitarResetPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    password_nueva: str

    @field_validator("password_nueva")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/registro", status_code=201)
async def registrar_usuario(
    body: RegistroRequest,
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    password_hasher: Annotated[PasswordHashingPort, Depends(get_password_hasher)],
    token_service: Annotated[TokenServicePort, Depends(get_token_service)],
    email_sender: Annotated[EmailPort, Depends(get_email_sender)],
    perfil_registro: Annotated[PerfilRegistroPort | None, Depends(get_perfil_registro)],
) -> JSONResponse:
    handler = RegistrarUsuarioHandler(
        repo, password_hasher, token_service, email_sender, perfil_registro
    )
    cmd = RegistrarUsuarioCommand(
        nombre=body.nombre,
        apellido=body.apellido,
        email=body.email,
        password=body.password,
        roles=body.roles,
        numero_licencia=body.numero_licencia,
        federacion=body.federacion,
        nombre_organizacion=body.nombre_organizacion,
    )
    try:
        resultado = await handler.handle(cmd)
    except CampoRequerido as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except PasswordDemasiadoCorto as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except CredencialesInvalidas:
        return JSONResponse(status_code=401, content={"detail": "Credenciales inválidas"})
    except RolYaAsignado as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except RolNoPermitido as exc:
        return JSONResponse(status_code=403, content={"detail": str(exc)})

    status = 201 if resultado.es_usuario_nuevo else 200

    if resultado.requires_role_selection:
        return JSONResponse(
            status_code=status,
            content={
                "usuario_id": str(resultado.usuario_id),
                "requires_role_selection": True,
                "roles": [r.value for r in resultado.roles_disponibles],
            },
        )

    assert resultado.token_response is not None
    return JSONResponse(
        status_code=status,
        content={
            "usuario_id": str(resultado.usuario_id),
            "access_token": resultado.token_response.access_token,
            "token_type": resultado.token_response.token_type,
        },
    )


@router.post("/login", status_code=200)
async def autenticar_usuario(
    body: LoginRequest,
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    token_service: Annotated[TokenServicePort, Depends(get_token_service)],
    password_hasher: Annotated[PasswordHashingPort, Depends(get_password_hasher)],
) -> JSONResponse:
    handler = AutenticarUsuarioHandler(repo, token_service, password_hasher)
    cmd = AutenticarUsuarioCommand(
        email=body.email,
        password=body.password,
        rol_elegido=body.rol_elegido,
    )
    try:
        result = await handler.handle(cmd)
    except (CredencialesInvalidas, UsuarioInactivo):
        return JSONResponse(status_code=401, content={"detail": "Credenciales inválidas"})

    if isinstance(result, RoleSelectionRequired):
        return JSONResponse(
            status_code=200,
            content={
                "requires_role_selection": True,
                "roles": [r.value for r in result.roles],
            },
        )

    return JSONResponse(
        status_code=200,
        content={
            "access_token": result.access_token,
            "token_type": result.token_type,
        },
    )


@router.post("/cambiar-password", status_code=204)
async def cambiar_password(
    body: CambiarPasswordRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    password_hasher: Annotated[PasswordHashingPort, Depends(get_password_hasher)],
) -> JSONResponse:
    handler = CambiarPasswordHandler(repo, password_hasher)
    cmd = CambiarPasswordCommand(
        usuario_id=UUID(current_user["sub"]),
        password_actual=body.password_actual,
        password_nueva=body.password_nueva,
    )
    try:
        await handler.handle(cmd)
    except PasswordActualIncorrecto as exc:
        return JSONResponse(status_code=401, content={"detail": str(exc)})
    except PasswordDemasiadoCorto as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except UsuarioNoEncontrado:
        return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})
    return JSONResponse(status_code=204, content=None)


@router.post("/solicitar-reset", status_code=200)
async def solicitar_reset_password(
    body: SolicitarResetPasswordRequest,
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    token_service: Annotated[TokenServicePort, Depends(get_token_service)],
    email_sender: Annotated[EmailPort, Depends(get_email_sender)],
) -> JSONResponse:
    handler = SolicitarResetPasswordHandler(
        repo=repo,
        token_service=token_service,
        email_sender=email_sender,
        frontend_base_url=os.getenv("FRONTEND_BASE_URL", "http://localhost:5173"),
    )
    await handler.handle(SolicitarResetPasswordCommand(email=body.email))
    return JSONResponse(
        status_code=200,
        content={
            "detail": "Si el email existe, enviaremos instrucciones para restablecer la contraseña"
        },
    )


@router.post("/reset-password", status_code=204)
async def reset_password(
    body: ResetPasswordRequest,
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    token_service: Annotated[TokenServicePort, Depends(get_token_service)],
    password_hasher: Annotated[PasswordHashingPort, Depends(get_password_hasher)],
) -> JSONResponse:
    handler = ResetPasswordHandler(repo, token_service, password_hasher)
    try:
        await handler.handle(
            ResetPasswordCommand(token=body.token, password_nueva=body.password_nueva)
        )
    except TokenResetInvalido as exc:
        return JSONResponse(status_code=400, content={"detail": str(exc)})
    except PasswordDemasiadoCorto as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    return JSONResponse(status_code=204, content=None)


class AgregarRolRequest(BaseModel):
    rol: Rol


@router.post("/usuarios/me/roles", status_code=200)
async def agregar_rol(
    body: AgregarRolRequest,
    current_user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
) -> JSONResponse:
    handler = AgregarRolUsuarioHandler(repo)
    cmd = AgregarRolUsuarioCommand(
        usuario_id=UUID(current_user["sub"]),
        nuevo_rol=body.rol,
    )
    try:
        roles = await handler.handle(cmd)
    except RolYaAsignado as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except RolNoPermitido as exc:
        return JSONResponse(status_code=403, content={"detail": str(exc)})
    except UsuarioNoEncontrado:
        return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})
    return JSONResponse(status_code=200, content={"roles": [r.value for r in roles]})


@router.delete("/usuarios/me/roles/{rol}", status_code=200)
async def quitar_rol(
    rol: Rol,
    current_user: Annotated[dict, Depends(get_current_user)],
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
) -> JSONResponse:
    handler = QuitarRolUsuarioHandler(repo)
    cmd = QuitarRolUsuarioCommand(
        usuario_id=UUID(current_user["sub"]),
        rol=rol,
    )
    try:
        roles = await handler.handle(cmd)
    except RolNoEncontrado as exc:
        return JSONResponse(status_code=404, content={"detail": str(exc)})
    except (RolNoRemovible, UltimoRolNoRemovible) as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    except UsuarioNoEncontrado:
        return JSONResponse(status_code=401, content={"detail": "Token inválido o expirado"})
    return JSONResponse(status_code=200, content={"roles": [r.value for r in roles]})


@router.get("/usuarios", status_code=200)
async def listar_usuarios(
    _: OrganizadorDep,
    repo: Annotated[UsuarioRepositoryPort, Depends(get_usuario_repository)],
    rol: Rol | None = None,
) -> JSONResponse:
    usuarios = await repo.list_by_rol(rol) if rol else await repo.list_all()
    return JSONResponse(
        status_code=200,
        content=[
            {
                "usuario_id": str(usuario.usuario_id),
                "nombre": usuario.nombre,
                "apellido": usuario.apellido,
                "email": usuario.email,
                "roles": [r.value for r in usuario.roles],
                "activo": usuario.activo,
            }
            for usuario in usuarios
        ],
    )
