---
title: "US-3.2.1 — BC Identidad: Usuario + JWT mínimo + /auth"
type: trazabilidad-us
sp: SP3
inc: INC-3.2
bc: identidad
estado: cerrada
fecha_cierre: "2026-03-30"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
us_id: US-3.2.1
tests_count: null
rf:
  - RF-US-01
  - RF-US-02
  - RF-US-03
  - RF-US-04
  - RF-US-05
software_items:
  - src/identidad/domain/aggregates/usuario.py
  - src/identidad/application/commands/autenticar_usuario.py
  - src/identidad/infrastructure/jwt_service.py
  - src/identidad/infrastructure/repositories/sqlite_usuario_repository.py
test_units:
  - tests/features/US-3.2.1-bc-identidad-jwt.feature
  - tests/integration/identidad/test_sqlite_usuario_repository.py
origen_tipo: rf
---

# US-3.2.1 — BC Identidad: Usuario + JWT mínimo + /auth

## Descripción

Introduce el BC Identidad con la entidad `Usuario`, autenticación JWT mínima y el endpoint `/auth/login`.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| [[RF-US-01]] | Un organizador por torneo |
| [[RF-US-02]] | Un usuario puede tener múltiples roles |
| [[RF-US-03]] | Autenticación mail + contraseña |
| [[RF-US-04]] | Juez asignado a disciplina específica |
| [[RF-US-05]] | Atletas solo ven resultados finales |

## Contenido implementado

- Entidad `Usuario` con campo `rol` (ADMIN, ORGANIZADOR, JUEZ, ATLETA)
- `POST /auth/login` — retorna JWT firmado con `rol` en payload
- `SQLiteUsuarioRepository`
- Hashing de contraseña con `PasswordHashingPort`

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/identidad/domain | ✅ |
| unit/identidad/application | ✅ |
| integration/identidad | ✅ |
| features/US-3.2.1 | ✅ |
| **Total** | **36 tests (100%)** |

## Estado

✅ Completado — 2026-03-30
