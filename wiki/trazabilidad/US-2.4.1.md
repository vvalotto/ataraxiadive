---
title: "US-2.4.1 — CompetenciaFinalizada automático (política P-08)"
type: trazabilidad-us
sp: SP2
inc: INC-2.4
bc: competencia
estado: completado
fecha_cierre: "2026-03-28"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §5
---

# US-2.4.1 — CompetenciaFinalizada automático (política P-08)

## Descripción

Implementa la política P-08: cuando el último atleta de la grilla completa su performance, la competencia se marca como finalizada automáticamente sin intervención del organizador.

## RFs cubiertos

Sin RF directo — política de negocio del dominio.

## Contenido implementado

- Política P-08: `CompetenciaFinalizada` disparado automáticamente al completar todos los atletas
- Evento de dominio `CompetenciaFinalizada` publicado al Event Store
- Callback en composition root (`src/app.py`) que dispara la política

## Invariantes aplicadas

- INV-C-04: la competencia finaliza cuando no quedan performances pendientes

## Tests

Sin entrada explícita en §36 — validado como parte de la suite acumulada de INC-2.4.

## Estado

✅ Completado — 2026-03-28
