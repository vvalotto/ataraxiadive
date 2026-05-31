---
title: "US-4.1.8 — Limpieza Torneo, SQLiteTorneoRepository, DisciplinaDescriptor, TarjetaAsignacion"
type: trazabilidad-us
sp: SP4
inc: INC-4.1
bc: torneo, competencia
estado: cerrada
fecha_cierre: "2026-04-08"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §12
us_id: US-4.1.8
tests_count: 91
rf: []
software_items:
  - src/torneo/infrastructure/repositories/sqlite_torneo_repository.py
test_units: null
origen_tipo: calidad
componentes_wiki:
  - arquitectura/torneo/sqlite-torneo-repository
---

# US-4.1.8 — Limpieza Torneo, SQLiteTorneoRepository, DisciplinaDescriptor, TarjetaAsignacion

## Descripción

Refactoring técnico de cierre del DesignReviewer INC-4.1: simplifica y aligera cuatro componentes que acumularon complejidad durante el sprint.

## Capas afectadas

`torneo/domain/`, `torneo/infrastructure/`, `competencia/domain/`

## Contenido implementado

| Componente | Mejora |
|-----------|--------|
| `Torneo` | Métodos auxiliares extraídos; aggregate más cohesivo |
| `SQLiteTorneoRepository` | Simplificación de queries y mapeo de filas |
| `DisciplinaDescriptor` | Eliminación de lógica condicional redundante |
| `TarjetaAsignacion` | Limpieza post-extensión con `MotivoDQ` y `PenalizacionTecnica` |

## Tests

| Suite | Resultado |
|-------|-----------|
| unit/torneo/domain | ✅ |
| unit/competencia/domain | ✅ |
| unit/competencia/infrastructure | ✅ |
| **Total acumulado** | **91 passed** |

BDD waiver — refactoring estructural.

## Estado

✅ Completado — 2026-04-08
