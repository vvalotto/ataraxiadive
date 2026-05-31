---
title: "RNF-06 — Escalabilidad: volumen modesto y predecible"
type: trazabilidad-rnf
rnf_id: RNF-06
atributo: Escalabilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-002-fastapi-backend
  - ADR-007-sqlite-persistencia-bc
  - ADR-021-fly-io
bcs_afectados:
  - todos
---

# RNF-06 — Escalabilidad

**Driver:** el volumen es modesto y predecible. Las decisiones de hoy no deben sobre-diseñar para escala que no existe.

| Atributo | Valor |
|---|---|
| Torneos por año (inicial) | 4 |
| Usuarios concurrentes por torneo | 50 |
| Atletas máximos por torneo | 100 |
| Horizonte temporal | 5 años |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-002-fastapi-backend]] — monolito FastAPI suficiente para el volumen actual
- [[decisiones/ADR-007-sqlite-persistencia-bc]] — SQLite por BC: simple y eficiente para este volumen
- [[decisiones/ADR-021-fly-io]] — Fly.io como PaaS: escalado bajo demanda sin over-engineering

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
