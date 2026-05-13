"""
Seed-A UAT SP6 — Usuarios Buenos Aires 2025

Crea: 1 organizador + 3 jueces + 31 atletas con credenciales ba2025.uat
No crea torneo ni inscripciones — eso lo hace Seed-B con el torneo_id de F-02.

Limpia datos de corridas anteriores antes de crear.

Uso:  uv run python tests/uat/sp6/seed_ba2025_usuarios.py
"""

from __future__ import annotations

import asyncio
import base64
import json
import os
import re
import sqlite3
import sys
import unicodedata
import uuid
from pathlib import Path

import httpx

sys.path.insert(0, "src")

BASE = "http://localhost:8000"
PASSWORD = "Ba2025uat!"
EMAIL_DOMAIN = "@ba2025.uat"
DATASET_PATH = Path("data/datasets/buenos_aires_2025/athlete_index.json")
IDS_PATH = Path("quality/reports/uat/SP6/uat_ba2025_usuarios_ids.json")

IDENTIDAD_DB = os.getenv("IDENTIDAD_DB_PATH", "data/identidad.db")
REGISTRO_DB = os.getenv("REGISTRO_DB_PATH", "data/registro.db")
TORNEO_DB = os.getenv("TORNEO_DB_PATH", "data/torneo.db")
COMPETENCIA_DB = os.getenv("COMPETENCIA_DB_PATH", "data/competencia.db")
RESULTADOS_DB = os.getenv("RESULTADOS_DB_PATH", "data/resultados.db")

# Roles operativos
ROLES_FIJOS = [
    ("organizador", "Organizador", "BA2025", "ORGANIZADOR"),
    ("juez1", "Juez", "Uno", "JUEZ"),
    ("juez2", "Juez", "Dos", "JUEZ"),
    ("juez3", "Juez", "Tres", "JUEZ"),
]

# Sexo manual para atletas sin resultados en ninguna disciplina
SEX_OVERRIDE: dict[str, str] = {
    "Ezequiel Cuchiarelli": "MASCULINO",
}

# Fecha de nacimiento representativa por grupo etario (no afecta la categoría, que se declara)
FECHA_NAC = {
    "JUNIOR": "2007-06-15",
    "SENIOR": "1992-06-15",
    "MASTER": "1975-06-15",
}


def normalizar_email(nombre_completo: str) -> str:
    nfkd = unicodedata.normalize("NFKD", nombre_completo.lower())
    sin_tildes = "".join(c for c in nfkd if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", ".", sin_tildes).strip(".")


def cargar_atletas_dataset() -> list[dict]:
    """Extrae atletas únicos del dataset con nombre, categoria, sex y club."""
    data = json.loads(DATASET_PATH.read_text())

    atletas: dict[str, dict] = {}
    for entry in data:
        if entry["discipline"] == "OVERALL":
            continue
        name = entry["name"]
        sex = None
        for r in entry.get("results", []):
            sex = r.get("sex")
            break

        if name not in atletas:
            atletas[name] = {
                "nombre_completo": name,
                "category": entry["category"],
                "sex": sex,
                "club": entry["club"],
            }
        elif sex and atletas[name]["sex"] is None:
            atletas[name]["sex"] = sex

    # Aplicar overrides manuales para atletas sin resultados en ninguna disciplina
    for name, sex in SEX_OVERRIDE.items():
        if name in atletas and atletas[name]["sex"] is None:
            atletas[name]["sex"] = sex

    return list(atletas.values())


def limpiar_entorno_uat() -> None:
    # Torneos y todo lo derivado
    with sqlite3.connect(TORNEO_DB) as con:
        n = con.execute("SELECT COUNT(*) FROM torneos").fetchone()[0]
        con.execute("DELETE FROM torneos")
        log(f"torneos eliminados: {n}")

    with sqlite3.connect(COMPETENCIA_DB) as con:
        n_e = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        n_c = con.execute("SELECT COUNT(*) FROM competencias_por_torneo").fetchone()[0]
        con.execute("DELETE FROM events")
        con.execute("DELETE FROM competencias_por_torneo")
        log(f"competencias eliminadas: {n_c}  events: {n_e}")

    with sqlite3.connect(RESULTADOS_DB) as con:
        n = con.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        con.execute("DELETE FROM events")
        log(f"resultados events eliminados: {n}")

    # Registro: inscripciones primero (FK), luego atletas
    with sqlite3.connect(REGISTRO_DB) as con:
        n_i = con.execute("SELECT COUNT(*) FROM inscripciones").fetchone()[0]
        n_a = con.execute("SELECT COUNT(*) FROM atletas").fetchone()[0]
        con.execute("DELETE FROM inscripciones")
        con.execute("DELETE FROM atletas")
        log(f"inscripciones eliminadas: {n_i}  atletas eliminados: {n_a}")

    # Identidad: eliminar todos los usuarios no-admin de dominios de prueba
    with sqlite3.connect(IDENTIDAD_DB) as con:
        rows = con.execute("SELECT email FROM usuarios WHERE rol != 'ADMIN'").fetchall()
        if rows:
            emails = [r[0] for r in rows]
            placeholders = ",".join("?" * len(emails))
            con.execute(f"DELETE FROM usuarios WHERE email IN ({placeholders})", emails)
        # Eliminar también admins de dominios de prueba anteriores (no ba2025.uat)
        con.execute(
            f"DELETE FROM usuarios WHERE rol = 'ADMIN' AND email NOT LIKE ?",
            (f"%{EMAIL_DOMAIN}",),
        )
        log(f"usuarios no-ba2025 eliminados: {len(rows)}")

    # Eliminar usuarios ba2025.uat existentes (el seed los recrea frescos)
    with sqlite3.connect(IDENTIDAD_DB) as con:
        n = con.execute(
            "SELECT COUNT(*) FROM usuarios WHERE email LIKE ?", (f"%{EMAIL_DOMAIN}",)
        ).fetchone()[0]
        con.execute("DELETE FROM usuarios WHERE email LIKE ?", (f"%{EMAIL_DOMAIN}",))
        log(f"usuarios ba2025 anteriores eliminados: {n}")


def log(msg: str) -> None:
    print(f"  {msg}")


def assert_ok(resp: httpx.Response, context: str) -> dict:
    if resp.status_code not in (200, 201, 204):
        print(f"\n✗ ERROR en {context}: {resp.status_code}")
        print(resp.text[:500])
        sys.exit(1)
    return resp.json() if resp.content else {}


def crear_usuario(client: httpx.Client, email: str, nombre: str, apellido: str, rol: str) -> str:
    resp = client.post(
        "/auth/registro",
        json={
            "email": email,
            "password": PASSWORD,
            "rol": rol,
            "nombre": nombre,
            "apellido": apellido,
        },
    )
    assert_ok(resp, f"registro {email}")
    resp = client.post("/auth/login", json={"email": email, "password": PASSWORD})
    log(f"✓ {rol:<15} {email}")
    return assert_ok(resp, f"login {email}")["access_token"]


def decode_sub(token: str) -> str:
    payload = token.split(".")[1]
    payload += "==" * ((4 - len(payload) % 4) % 4)
    return json.loads(base64.b64decode(payload))["sub"]


async def crear_admin() -> None:
    from identidad.domain.aggregates.usuario import Usuario
    from identidad.domain.value_objects.rol import Rol
    from identidad.infrastructure.bcrypt_password_hasher import BcryptPasswordHasher
    from identidad.infrastructure.repositories.sqlite_usuario_repository import (
        SQLiteUsuarioRepository,
    )

    repo = SQLiteUsuarioRepository()
    admin_email = f"admin{EMAIL_DOMAIN}"
    existente = await repo.find_by_email(admin_email)
    if existente is not None:
        log(f"admin existente: {admin_email}")
        return
    hasher = BcryptPasswordHasher()
    usuario = Usuario(
        usuario_id=uuid.uuid4(),
        nombre="Admin",
        apellido="BA2025",
        email=admin_email,
        password_hash=hasher.hash(PASSWORD),
        rol=Rol.ADMIN,
    )
    await repo.save(usuario)
    log(f"✓ ADMIN          {admin_email}")


def main() -> None:
    print("\n=== Seed-A UAT SP6 — Usuarios BA2025 ===\n")

    atletas_dataset = cargar_atletas_dataset()
    log(f"Dataset cargado: {len(atletas_dataset)} atletas únicos")
    print()

    print("▸ Limpieza de entorno UAT (todas las BDs)")
    limpiar_entorno_uat()
    print()

    print("▸ Admin (application layer)")
    asyncio.run(crear_admin())
    print()

    ids: dict = {
        "password_universal": PASSWORD,
        "roles_fijos": {},
        "atletas": {},
    }

    with httpx.Client(base_url=BASE, timeout=15) as client:

        # ── Roles operativos ──────────────────────────────────────────────────
        print("▸ Roles operativos")
        admin_email = f"admin{EMAIL_DOMAIN}"
        admin_resp = client.post("/auth/login", json={"email": admin_email, "password": PASSWORD})
        assert_ok(admin_resp, "login admin")
        admin_token = admin_resp.json()["access_token"]
        admin_h = {"Authorization": f"Bearer {admin_token}"}

        for alias, nombre, apellido, rol in ROLES_FIJOS:
            email = f"{alias}{EMAIL_DOMAIN}"
            token = crear_usuario(client, email, nombre, apellido, rol)
            user_id = decode_sub(token)
            ids["roles_fijos"][alias] = {"email": email, "user_id": user_id}

        print()

        # ── Atletas: auth user + registro BC ──────────────────────────────────
        print("▸ Atletas")
        print(f"  Creando {len(atletas_dataset)} atletas...")

        for atleta in atletas_dataset:
            nombre_completo = atleta["nombre_completo"]
            partes = nombre_completo.split(" ", 1)
            nombre = partes[0]
            apellido = partes[1] if len(partes) > 1 else nombre

            sex = atleta["sex"]
            if sex is None:
                print(f"\n✗ Sin sexo determinado para {nombre_completo}")
                sys.exit(1)

            categoria = f"{atleta['category']}_{sex}"
            email_local = normalizar_email(nombre_completo)
            email = f"{email_local}{EMAIL_DOMAIN}"
            atleta_id = str(uuid.uuid4())
            fecha_nac = FECHA_NAC[atleta["category"]]

            # Auth user
            crear_usuario(client, email, nombre, apellido, "ATLETA")

            # Registro BC
            assert_ok(
                client.post(
                    "/registro/atletas",
                    json={
                        "atleta_id": atleta_id,
                        "nombre": nombre,
                        "apellido": apellido,
                        "email": email,
                        "fecha_nacimiento": fecha_nac,
                        "categoria": categoria,
                        "club": atleta["club"],
                    },
                    headers=admin_h,
                ),
                f"registro atleta {nombre_completo}",
            )

            ids["atletas"][nombre_completo] = {
                "atleta_id": atleta_id,
                "email": email,
                "categoria": categoria,
                "club": atleta["club"],
            }

    # ── Guardar IDs ───────────────────────────────────────────────────────────
    IDS_PATH.write_text(json.dumps(ids, indent=2))
    print()
    print(f"✓ IDs guardados en {IDS_PATH}")

    print("\n" + "=" * 60)
    print("RESUMEN")
    print(f"  Organizador:  organizador{EMAIL_DOMAIN}  /  {PASSWORD}")
    print(f"  Juez 1:       juez1{EMAIL_DOMAIN}  /  {PASSWORD}")
    print(f"  Juez 2:       juez2{EMAIL_DOMAIN}  /  {PASSWORD}")
    print(f"  Juez 3:       juez3{EMAIL_DOMAIN}  /  {PASSWORD}")
    print(f"  Víctor Valotto: victor.valotto{EMAIL_DOMAIN}  /  {PASSWORD}")
    print(f"  Guadalupe Fardi: guadalupe.fardi{EMAIL_DOMAIN}  /  {PASSWORD}")
    print(f"\n  Total atletas creados: {len(atletas_dataset)}")
    print("\n=== Seed-A completado ===\n")


if __name__ == "__main__":
    main()
