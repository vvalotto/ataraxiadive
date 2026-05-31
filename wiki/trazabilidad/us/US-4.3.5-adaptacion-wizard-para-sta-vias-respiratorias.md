---
title: "US-4.3.5 — Adaptación wizard para STA (vías respiratorias)"
type: trazabilidad-us
sp: SP4
inc: INC-4.3
bc: frontend
estado: cerrada
fecha_cierre: "2026-04-12"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §14
us_id: US-4.3.5
tests_count: null
rf:
  - RF-EJ-02
---

# US-4.3.5 — Adaptación wizard para STA (vías respiratorias)

## Descripción

Adapta el paso 3 del wizard para la disciplina STA (Static Apnea), donde el inicio oficial no es "el atleta inicia" sino "vías respiratorias en agua".

## RFs / Wireframes cubiertos

wireframes-juez STA · RF-EJ-02

## Contenido implementado

- Paso 3 del wizard en STA: botón "Vías respiratorias en agua" reemplaza "Atleta inicia"
- BKO en STA registra `valor_rp=0` automáticamente (black-out en estático = 0 metros)
- UI móvil ajustada para el flujo específico de STA

## Tests

Frontend (build + lint). BDD waiver — frontend puro. UAT INC-4.3 — 2026-04-12.

DesignReviewer post-merge INC-4.3: **0 CRITICAL · 158 WARNING**.

## Estado

✅ Completado — 2026-04-12
