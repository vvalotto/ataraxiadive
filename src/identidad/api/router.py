from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator

from identidad.api.dependencies import (
    get_password_hasher,
    get_token_service,
    get_usuario_repository,
)
from identidad.application.commands.autenticar_usuario import (
    AutenticarUsuarioCommand,
    AutenticarUsuarioHandler,
    TokenResponse,
)
from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.domain.exceptions import (
    CredencialesInvalidas,
    EmailYaRegistrado,
    PasswordDemasiadoCorto,
    UsuarioInactivo,
)
from identidad.domain.value_objects.rol import Rol

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Schemas ──────────────────────────────────────────────────────────────────


class RegistroRequest(BaseModel):
    email: str
    password: str
    rol: Rol

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("La contraseña debe tener al menos 8 caracteres")
        return v


class RegistroResponse(BaseModel):
    usuario_id: UUID


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str


# ── Endpoints ─────────────────────────────────────────────────────────────────


@router.post("/registro", status_code=201)
async def registrar_usuario(body: RegistroRequest) -> JSONResponse:
    repo = get_usuario_repository()
    password_hasher = get_password_hasher()
    handler = RegistrarUsuarioHandler(repo, password_hasher)
    cmd = RegistrarUsuarioCommand(email=body.email, password=body.password, rol=body.rol)
    try:
        usuario_id = await handler.handle(cmd)
    except PasswordDemasiadoCorto as exc:
        return JSONResponse(status_code=422, content={"detail": str(exc)})
    except EmailYaRegistrado as exc:
        return JSONResponse(status_code=409, content={"detail": str(exc)})
    return JSONResponse(status_code=201, content={"usuario_id": str(usuario_id)})


@router.post("/login", status_code=200)
async def autenticar_usuario(body: LoginRequest) -> JSONResponse:
    repo = get_usuario_repository()
    token_service = get_token_service()
    password_hasher = get_password_hasher()
    handler = AutenticarUsuarioHandler(repo, token_service, password_hasher)
    cmd = AutenticarUsuarioCommand(email=body.email, password=body.password)
    try:
        token_response: TokenResponse = await handler.handle(cmd)
    except (CredencialesInvalidas, UsuarioInactivo):
        return JSONResponse(status_code=401, content={"detail": "Credenciales inválidas"})
    return JSONResponse(
        status_code=200,
        content={
            "access_token": token_response.access_token,
            "token_type": token_response.token_type,
        },
    )
