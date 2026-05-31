---
title: "RNF-07 — Mantenibilidad: configuración sin desarrollador"
type: trazabilidad-rnf
rnf_id: RNF-07
atributo: Mantenibilidad
last_updated: "2026-05-31"
adr_refs:
  - ADR-004-reglas-como-datos
  - ADR-006-estructura-bc-first
  - ADR-009-migraciones-por-bc
bcs_afectados:
  - todos
---

# RNF-07 — Mantenibilidad

**Driver:** configuración de reglas sin desarrollador; frecuencia de cambio de reglamentos muy esporádica (~cada 2 años).

| Atributo | Valor |
|---|---|
| Configuración de reglas sin desarrollador | Requerida |
| Frecuencia de cambio de reglamentos | ~cada 2 años |
| Actualización sin interrumpir torneo en curso | No requerida |

## Decisiones arquitectónicas derivadas

- [[decisiones/ADR-004-reglas-como-datos]] — reglas editables sin despliegue
- [[decisiones/ADR-006-estructura-bc-first]] — organización por BC: cada BC es independiente y modificable en aislamiento
- [[decisiones/ADR-009-migraciones-por-bc]] — Alembic por BC: migraciones aisladas sin afectar otros BCs

## Relación con el dominio

→ [[conceptos/atributos-calidad]]
