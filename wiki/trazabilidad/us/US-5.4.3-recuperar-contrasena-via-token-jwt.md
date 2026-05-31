---
title: "US-5.4.3 — Recuperar contraseña vía token JWT"
type: trazabilidad-us
sp: SP5
inc: INC-5.4
bc: identidad
estado: cerrada
fecha_cierre: "2026-04-24"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §24
  - docs/plans/sp5/US-5.4.3-plan.md
us_id: US-5.4.3
tests_count: null
rf: []
software_items:
  - src/identidad/application/commands/solicitar_reset_password.py
  - src/identidad/application/commands/reset_password.py
test_units:
  - tests/features/US-5.4.3-recuperar-password.feature
origen_tipo: plataforma
componentes_wiki:
  - arquitectura/identidad/command-handlers-identidad
---

# US-5.4.3 — Recuperar contraseña vía token JWT

## Descripción

Flujo completo de recuperación de contraseña olvidada: el usuario solicita un enlace que llega por email (Resend), el enlace incluye un JWT firmado con expiración de 1 hora, y el usuario completa el cambio en una página dedicada.

## Contenido implementado

- `TokenServicePort` — abstracción para generación y validación de tokens de reset
- JWT firmado con `exp=1h` para el enlace de reset
- `POST /auth/forgot-password` — solicitud de enlace
- `POST /auth/reset-password` — aplicación del reset con token
- Email via Resend adapter
- Páginas frontend: `/recuperar-password` y `/reset-password`

## Estado

✅ Completado — 2026-04-24 · PR #114
