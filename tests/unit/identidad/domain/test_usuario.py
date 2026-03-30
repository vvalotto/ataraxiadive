"""Tests unitarios — domain Usuario + exceptions (sin I/O)."""
from __future__ import annotations

import uuid

import pytest

from identidad.domain.aggregates.usuario import Usuario
from identidad.domain.exceptions import (
    CredencialesInvalidas,
    EmailYaRegistrado,
    PasswordDemasiadoCorto,
    TokenInvalido,
    UsuarioInactivo,
    UsuarioNoEncontrado,
)
from identidad.domain.value_objects.rol import Rol


# ── Rol ───────────────────────────────────────────────────────────────────────

def test_rol_valores_validos() -> None:
    assert Rol.ORGANIZADOR == "ORGANIZADOR"
    assert Rol.JUEZ == "JUEZ"
    assert Rol.ATLETA == "ATLETA"
    assert Rol.ADMIN == "ADMIN"


def test_rol_es_str_enum() -> None:
    assert isinstance(Rol.JUEZ, str)


# ── Usuario ───────────────────────────────────────────────────────────────────

def test_usuario_creacion_basica() -> None:
    uid = uuid.uuid4()
    u = Usuario(
        usuario_id=uid,
        email="test@test.com",
        password_hash="$2b$12$hash",
        rol=Rol.ORGANIZADOR,
    )
    assert u.usuario_id == uid
    assert u.email == "test@test.com"
    assert u.rol == Rol.ORGANIZADOR
    assert u.activo is True


def test_usuario_inactivo_por_defecto_es_true() -> None:
    u = Usuario(
        usuario_id=uuid.uuid4(),
        email="a@b.com",
        password_hash="hash",
        rol=Rol.ATLETA,
    )
    assert u.activo is True


def test_usuario_puede_estar_inactivo() -> None:
    u = Usuario(
        usuario_id=uuid.uuid4(),
        email="a@b.com",
        password_hash="hash",
        rol=Rol.ATLETA,
        activo=False,
    )
    assert u.activo is False


# ── Exceptions ────────────────────────────────────────────────────────────────

def test_email_ya_registrado_mensaje() -> None:
    exc = EmailYaRegistrado("dup@test.com")
    assert "dup@test.com" in str(exc)


def test_credenciales_invalidas_mensaje() -> None:
    exc = CredencialesInvalidas()
    assert "contraseña" in str(exc).lower() or "credencial" in str(exc).lower()


def test_usuario_no_encontrado_mensaje() -> None:
    exc = UsuarioNoEncontrado("abc-123")
    assert "abc-123" in str(exc)


def test_usuario_inactivo_mensaje() -> None:
    exc = UsuarioInactivo("inactivo@test.com")
    assert "inactivo@test.com" in str(exc)


def test_password_demasiado_corto_mensaje() -> None:
    exc = PasswordDemasiadoCorto()
    assert "8" in str(exc)


def test_token_invalido_mensaje() -> None:
    exc = TokenInvalido()
    assert "token" in str(exc).lower() or "jwt" in str(exc).lower()
