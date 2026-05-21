---
title: "US-3.4.2 — Auth por rol en APIs escribibles con JWT middleware"
type: trazabilidad-us
sp: SP3
inc: INC-3.4
bc: identidad, shared
estado: completado
fecha_cierre: "2026-04-01"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §9
---

# US-3.4.2 — Auth por rol en APIs escribibles con JWT middleware

## Descripción

Protege todos los endpoints de escritura (POST/PUT/PATCH/DELETE) con validación JWT y guard de rol, asegurando que solo usuarios autorizados puedan ejecutar cada operación.

## RFs cubiertos

| RF | Descripción |
|----|-------------|
| RF-US-02 | Un usuario puede tener múltiples roles |
| RF-US-03 | Autenticación mail + contraseña |
| RF-US-04 | Juez asignado a disciplina específica |

## Contenido implementado

- Middleware JWT en FastAPI via `Depends(require_role(...))`
- Guards específicos por endpoint: `require_role("ORGANIZADOR")`, `require_role("JUEZ")`, etc.
- Integración con `shared/api/dependencies.py` ([[US-ADJ-3.4]])

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/identidad/api | ✅ |
| features/US-3.4.2-auth-jwt-middleware | ✅ |
| **Total** | **15 tests** |

## Estado

✅ Completado — 2026-04-01
