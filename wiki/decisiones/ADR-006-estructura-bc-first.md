---
title: "ADR-006: Estructura de Código Fuente BC-First"
type: decision
last_updated: "2026-05-20"
sources:
  - docs/adr/ADR-006-estructura-bc-first.md
estado: Aceptada
fecha: 2026-03-20
bcs_afectados: [todos]
rnf_refs:
  - RNF-07-mantenibilidad-sin-desarrollador
---

# ADR-006: Estructura de Código Fuente BC-First

## Decisión

El código fuente se organiza por Bounded Context (BC-first), no por capa técnica (layer-first).

## Estructura vigente

```
src/
├── competencia/
│   ├── domain/          ← aggregates, value_objects, events, ports, exceptions
│   ├── application/     ← commands, queries
│   ├── infrastructure/  ← event_store, repositories (solo BCs con ES)
│   └── api/             ← router, schemas, exception_handlers
├── torneo/ registro/ resultados/ identidad/  ← igual, sin infrastructure/event_store
├── notificaciones/      ← igual a competencia (tiene ES)
├── shared/
│   └── domain/          ← value_objects y base classes cross-BC
└── app.py               ← ensamble central de routers FastAPI
```

## Regla de oro — capas dentro de cada BC

```
domain/        → no importa nada fuera de su propio domain/
application/   → importa domain/, nunca infrastructure/
infrastructure → implementa puertos definidos en domain/ports/
api/           → importa application/, nunca domain/ directamente
```

Excepción permitida: cualquier capa puede importar desde `shared/domain/`.

## Por qué BC-first y no layer-first

Layer-first dispersa la cohesión del dominio: entender `Competencia` requiere navegar 4 carpetas top-level. Con BC-first, todo lo de un contexto de negocio está en un lugar, alineado con el principio DDD de que los BCs son unidades autónomas.

## Consecuencias vigentes

- **Tests:** `tests/unit/<bc>/`, `tests/integration/<bc>/`, `tests/features/` por US-IEDD.
- **Quality Gates:** reportes por US (CodeGuard), por Incremento (DesignReviewer), por Baseline (ArchitectAnalyst).
- La comunicación entre BCs es **solo por puertos** — nunca imports directos entre paquetes BC.
- Los ACLs viven en `<bc>/infrastructure/` del BC consumidor.

## ADRs relacionados

- [[ADR-005-bounded-contexts-ddd-estrategico]] — define los 6 BCs
- [[ADR-007-sqlite-persistencia-bc]] — cada BC tiene su propio `.db`
- [[ADR-009-migraciones-por-bc]] — migraciones Alembic por BC
