---
title: "US-7.1.2 — fly deploy + verificación flujos críticos + tag v1.0.1"
type: trazabilidad-us
sp: SP7
inc: INC-7.1
bc: infraestructura
estado: planificado
fecha_cierre: null
last_updated: "2026-05-21"
sources:
  - docs/plans/sp7/PLAN-SP7.md §INC-7.1
---

# US-7.1.2 — fly deploy + verificación flujos críticos + tag v1.0.1

## Descripción

Ejecutar el primer despliegue real en Fly.io y verificar los flujos críticos de los tres roles en producción. Cierra INC-7.1 y habilita el tagging de `v1.0.1` (BL-007).

## Contenido planificado

- `fly deploy` — primer deploy en producción con volumen `/app/data`
- Verificación de login para los tres roles (organizador, juez, atleta)
- Verificación del flujo crítico: crear torneo → grilla → flujo de ejecución
- Tag `v1.0.1` en `main` + registro BL-007

## DoD

URL pública Fly.io accesible con SSL · login funcional · flujo organizador → juez → atleta verificado end-to-end en producción.

## Estado

⏳ Planificado — pendiente tras US-7.1.1
