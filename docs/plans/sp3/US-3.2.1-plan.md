# Plan de Implementación — US-3.2.1

| Campo | Valor |
|-------|-------|
| **US** | US-3.2.1 |
| **Título** | BC Identidad — Usuario + JWT mínimo |
| **BC** | `identidad` |
| **Estimación** | 8 puntos |

---

## Estructura a crear

```
src/identidad/
├── domain/
│   ├── value_objects/
│   │   └── rol.py                         # StrEnum: ORGANIZADOR/JUEZ/ATLETA/ADMIN
│   ├── aggregates/
│   │   └── usuario.py                     # @dataclass Usuario
│   ├── ports/
│   │   └── usuario_repository_port.py     # ABC: save/find_by_id/find_by_email
│   └── exceptions.py                      # EmailYaRegistrado/CredencialesInvalidas/...
├── application/
│   └── commands/
│       ├── registrar_usuario.py           # Command + Handler
│       └── autenticar_usuario.py          # Command + Handler + TokenResponse
├── infrastructure/
│   ├── jwt_service.py                     # JWTService: generate/verify
│   └── repositories/
│       └── sqlite_usuario_repository.py  # SQLiteUsuarioRepository
└── api/
    ├── router.py                          # /auth: POST registro + POST login
    └── dependencies.py                   # get_current_user() dep FastAPI

tests/
├── unit/identidad/
│   ├── domain/test_usuario.py             # invariantes del aggregate
│   └── application/test_handlers.py      # handlers con repo mock
├── integration/identidad/
│   └── test_sqlite_usuario_repository.py # CRUD con aiosqlite real
└── features/
    ├── US-3.2.1-bc-identidad-jwt.feature (ya creado)
    └── steps/US-3.2.1-steps.py
```

---

## Tareas

| # | Tarea | Capas |
|---|-------|-------|
| T1 | `Rol` StrEnum + `Usuario` dataclass + `UsuarioRepositoryPort` + `exceptions.py` | domain |
| T2 | `RegistrarUsuarioHandler` — bcrypt hash + INV-ID-01/02 | application |
| T3 | `AutenticarUsuarioHandler` — verificar hash + producir `TokenResponse` | application |
| T4 | `JWTService` — generate (RS sub/email/rol/exp) + verify | infrastructure |
| T5 | `SQLiteUsuarioRepository` — save/find_by_id/find_by_email, tabla `usuarios` | infrastructure |
| T6 | Router `/auth` — POST registro + POST login + exception handlers | api |
| T7 | `get_current_user()` dependency + `app.py` incluir router identidad | api |

---

## Dependencias entre tareas

```
T1 → T2, T3 (domain primero)
T4 → T3 (JWTService lo usa AutenticarHandler)
T5 → tests integración
T6 → T1, T2, T3, T4, T5
T7 → T6
```

---

## Variables de entorno necesarias

```
IDENTIDAD_JWT_SECRET=dev-secret-change-in-prod
IDENTIDAD_DB_PATH=data/identidad.db
IDENTIDAD_JWT_EXPIRY_HOURS=24
```

---

## Notas

- `JWTService` en `infrastructure/` — no en domain (depende de PyJWT)
- `get_current_user()` en `api/dependencies.py` — los otros BCs la importarán en INC-3.4
- Tabla: `usuarios (usuario_id TEXT PK, email TEXT UNIQUE, password_hash TEXT, rol TEXT, activo INTEGER DEFAULT 1)`
- `CREATE TABLE IF NOT EXISTS` en `SQLiteUsuarioRepository.__init__` (sin Alembic en SP3)
- `IDENTIDAD_JWT_SECRET` obligatorio — `JWTService.__init__` lanza `ValueError` si no está seteada

---

*Redactado: 2026-03-30 — Fase 2 US-3.2.1*
