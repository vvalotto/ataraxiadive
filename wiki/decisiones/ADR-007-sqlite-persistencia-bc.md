---
title: "ADR-007: SQLite — un archivo por Bounded Context"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-007-sqlite-persistencia-bc.md
estado: Aceptada
fecha: 2026-03-20
bcs_afectados: [todos]
---

# ADR-007: SQLite — un archivo por Bounded Context

## Decisión

SQLite como motor de persistencia. Un archivo `.db` por BC. Reemplaza la propuesta original de PostgreSQL.

## Mapa de archivos

```
data/
├── competencia.db     ← event store + read models (Core Domain)
├── torneo.db          ← ciclo de vida, disciplinas, categorías, sede
├── registro.db        ← atletas, inscripciones, anuncios
├── resultados.db      ← rankings, publicaciones
├── identidad.db       ← usuarios, roles, tokens
└── notificaciones.db  ← notification events, outbox
```

## Por qué no PostgreSQL

- **Escala real:** 4 torneos/año, ~100 atletas, ~500 performances/torneo, 50 usuarios concurrentes.
- El pico de escritura está **naturalmente particionado**: cada juez opera en su andarivel propio, contención mínima.
- Modo WAL de SQLite (`PRAGMA journal_mode=WAL`) permite lecturas concurrentes durante escrituras.
- Cero infraestructura de servidor — `git clone` + `uv sync` es suficiente para levantar.

## Consecuencias vigentes

- Cada BC accede **únicamente a su propio archivo**. No hay JOINs entre BCs.
- Sin JSONB con índices — reemplazado por columnas explícitas o JSON sin índice.
- El `RepositorioPuerto` abstrae completamente el motor — migrar a PostgreSQL afecta solo `infrastructure/repositories/`.
- Tests de integración con SQLite en memoria (`:memory:`) — rápidos y sin infraestructura.
- Backup en producción: Fly.io con volumen persistente (ver [[ADR-021-fly-io]]).

## Condición de escape documentada

Migrar a PostgreSQL si se cumple cualquiera:
- Más de 200 escrituras simultáneas sostenidas
- Necesidad de full-text search avanzado
- Requerimiento de replicación multi-servidor

## ADRs relacionados

- [[ADR-008-event-store-sqlite]] — implementación del event store sobre SQLite
- [[ADR-009-migraciones-por-bc]] — migraciones Alembic por archivo `.db`
- [[ADR-021-fly-io]] — estrategia de persistencia en producción (volumen persistente)
