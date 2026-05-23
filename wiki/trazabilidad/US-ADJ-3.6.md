---
title: "US-ADJ-3.6 — TokenServicePort + PasswordHashingPort (DIP en Identidad)"
type: trazabilidad-us
sp: SP-ADJ-03
inc: SP-ADJ-03
bc: identidad
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §10
us_id: US-ADJ-3.6
tests_count: null
---

# US-ADJ-3.6 — TokenServicePort + PasswordHashingPort (DIP en Identidad)

## Descripción

Introduce puertos abstractos para los servicios de token JWT y hashing de contraseñas en el BC Identidad, aplicando DIP para desacoplar el dominio de las implementaciones concretas.

## Capas afectadas

`identidad/domain/ports/`, `identidad/application/`

## Issues resueltos

| Issue | Cambio |
|-------|--------|
| SOLID-02 | `TokenServicePort` — puerto abstracto para generación y validación de JWT |
| SOLID-03 | `PasswordHashingPort` — puerto abstracto para hashing y verificación de contraseñas |

## Principios aplicados

- **DIP**: los handlers de Identidad dependen de puertos abstractos; los adaptadores concretos (PyJWT, bcrypt) se inyectan desde el composition root

## Tests

BDD waiver — refactoring arquitectónico. Tests de identidad existentes pasan sin modificación.

## Estado

✅ Completado — 2026-04-03
