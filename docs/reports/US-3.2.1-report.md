# Reporte de Implementación — US-3.2.1

| Campo | Valor |
|-------|-------|
| **US** | US-3.2.1 |
| **Título** | BC Identidad — Usuario + JWT mínimo |
| **Sprint** | SP3 — El Torneo |
| **Incremento** | INC-3.2 |
| **Fecha** | 2026-03-30 |
| **Tiempo total** | ~14 min |

---

## Resumen

BC Identidad implementado completo: registro de usuarios con bcrypt, autenticación JWT, repositorio SQLite, router FastAPI `/auth` y dependencia `get_current_user()` reutilizable por otros BCs en INC-3.4.

---

## Artefactos generados

### Código

| Archivo | Descripción |
|---------|-------------|
| `src/identidad/domain/value_objects/rol.py` | `Rol` StrEnum (ORGANIZADOR/JUEZ/ATLETA/ADMIN) |
| `src/identidad/domain/aggregates/usuario.py` | `@dataclass Usuario` |
| `src/identidad/domain/ports/usuario_repository_port.py` | Puerto abstracto |
| `src/identidad/domain/exceptions.py` | 6 excepciones de dominio |
| `src/identidad/application/commands/registrar_usuario.py` | Handler + Command |
| `src/identidad/application/commands/autenticar_usuario.py` | Handler + Command + `TokenResponse` |
| `src/identidad/infrastructure/jwt_service.py` | `JWTService` (generate/verify) |
| `src/identidad/infrastructure/repositories/sqlite_usuario_repository.py` | Repositorio aiosqlite |
| `src/identidad/api/router.py` | `POST /auth/registro` + `POST /auth/login` |
| `src/identidad/api/dependencies.py` | `get_current_user()` FastAPI dep |
| `src/app.py` | Router identidad incluido |

### Tests

| Suite | Tests | Resultado |
|-------|-------|-----------|
| Unit (domain) | 11 | ✅ 100% |
| Unit (application) | 12 | ✅ 100% |
| Integration (repository) | 6 | ✅ 100% |
| BDD (7 escenarios) | 7 | ✅ 100% |
| **Total US-3.2.1** | **36** | **✅ 100%** |
| **Total suite completa** | **586** | **✅ 100%** |

### Cobertura

| Módulo | Cobertura |
|--------|-----------|
| `src/identidad/` | **100%** |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| CodeGuard | ✅ 0 errores, 0 advertencias |
| Tests 100% pass | ✅ 36/36 |
| Cobertura domain/ + application/ | ✅ 100% |

---

## Invariantes verificados

| Invariante | Descripción | Test |
|------------|-------------|------|
| INV-ID-01 | Email único | `test_registrar_email_duplicado_lanza_excepcion` + BDD 409 |
| INV-ID-02 | Password ≥ 8 caracteres | `test_registrar_password_corto_lanza_excepcion` + BDD 422 |
| INV-ID-03 | Password almacenado como hash bcrypt | `test_registrar_guarda_hash_no_plain` |
| INV-ID-04 | JWT expira en 24h (configurable) | `JWTService` con env var |
| INV-ID-05 | JWT contiene sub/email/rol/exp | `test_jwt_generate_y_verify_payload` + BDD |
| INV-ID-06 | Usuario inactivo no puede autenticarse | `test_autenticar_usuario_inactivo_lanza_excepcion` |

---

## Decisiones técnicas

- `JWTService` en `infrastructure/` — depende de PyJWT, no pertenece al dominio
- `get_current_user()` en `api/dependencies.py` — los otros BCs la importarán en INC-3.4 (US-3.4.2)
- `IDENTIDAD_JWT_SECRET` obligatorio — `JWTService.__init__` lanza `ValueError` si no está seteada
- `EmailStr` descartado — requiere `email-validator`; validación de formato no es invariante de esta US
- Dependencias añadidas: `PyJWT>=2.8.0`, `bcrypt>=4.1.0`

---

## Próximo paso

INC-3.2 continúa con US-3.2.2 — BC Registro: aggregate `Atleta`.

---

*Generado: 2026-03-30 — Fase 9 US-3.2.1*
