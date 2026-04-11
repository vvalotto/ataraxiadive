"""
Seed de usuarios de prueba para INC-4.2.
Uso: uv run python scripts/seed_test_users.py

Requiere IDENTIDAD_JWT_SECRET en el entorno (solo para que JWTService no falle al importar).
Alternativa: IDENTIDAD_JWT_SECRET=dev uv run python scripts/seed_test_users.py
"""
import asyncio
import os
import sys

sys.path.insert(0, "src")

os.environ.setdefault("IDENTIDAD_JWT_SECRET", "dev-seed-secret")

from identidad.application.commands.registrar_usuario import (
    RegistrarUsuarioCommand,
    RegistrarUsuarioHandler,
)
from identidad.domain.exceptions import EmailYaRegistrado
from identidad.domain.value_objects.rol import Rol
from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
from identidad.infrastructure.repositories.sqlite_usuario_repository import SQLiteUsuarioRepository

USUARIOS_PRUEBA = [
    {"email": "juez@ataraxia.com", "password": "juez1234", "rol": Rol.JUEZ},
    {"email": "org@ataraxia.com",  "password": "org12345", "rol": Rol.ORGANIZADOR},
]


async def seed() -> None:
    repo = SQLiteUsuarioRepository()
    hasher = BcryptPasswordHasher()
    handler = RegistrarUsuarioHandler(repo, hasher)

    for u in USUARIOS_PRUEBA:
        cmd = RegistrarUsuarioCommand(email=u["email"], password=u["password"], rol=u["rol"])
        try:
            uid = await handler.handle(cmd)
            print(f"  ✓ {u['email']} ({u['rol'].value}) — id={uid}")
        except EmailYaRegistrado:
            print(f"  ~ {u['email']} ya existe, se omite")


if __name__ == "__main__":
    print("Creando usuarios de prueba...")
    asyncio.run(seed())
    print()
    print("Credenciales:")
    for u in USUARIOS_PRUEBA:
        print(f"  {u['email']}  /  {u['password']}  ({u['rol'].value})")
