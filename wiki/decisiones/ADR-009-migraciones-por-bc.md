---
title: "ADR-009: Migraciones de schema por Bounded Context"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-009-migraciones-por-bc.md
estado: Aceptada
fecha: 2026-03-20
bcs_afectados: [todos]
---

# ADR-009: Migraciones de schema por Bounded Context

## Decisión

Un entorno Alembic independiente por BC, con su propio `env.py` y `alembic.ini`, apuntando a su propio SQLite.

## Estructura vigente

```
src/<bc>/infrastructure/migrations/
├── env.py
└── versions/
```

## Por qué no migraciones globales

Un único historial de migraciones para todos los BCs viola la aislación de [[ADR-007-sqlite-persistencia-bc]]: el schema de un BC podría afectar inadvertidamente a otro.

## Consecuencias vigentes

- El schema de cada BC evoluciona de forma **completamente independiente**.
- Para correr todas las migraciones hay que iterar sobre cada BC — se mitiga con un script `migrate_all.sh`.
- Mayor configuración inicial: un `alembic.ini` y `env.py` por BC.

## ADRs relacionados

- [[ADR-006-estructura-bc-first]] — la estructura `src/<bc>/` tiene su correspondencia en `data/<bc>.db` y en las migraciones
- [[ADR-007-sqlite-persistencia-bc]] — cada BC tiene su propio archivo SQLite
