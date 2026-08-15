---
title: "US-ADJ-4.1 — Renombrar DYNB→DBF y SPE2X50→SPE (acrónimos dominio real)"
type: trazabilidad-us
sp: SP-ADJ-04
inc: SP-ADJ-04
bc: competencia, shared
estado: cerrada
fecha_cierre: "2026-04-03"
last_updated: "2026-05-21"
sources:
  - docs/traceability/matrix.md §11
us_id: US-ADJ-4.1
tests_count: null
rf:
  - RF-GT-02-disciplinas-configurables
software_items:
  - src/competencia/domain/value_objects/disciplina.py
test_units: null
origen_tipo: calidad
componentes_wiki:
  - arquitectura/competencia/competencia-aggregate
---

# US-ADJ-4.1 — Renombrar DYNB→DBF y SPE2X50→SPE

## Descripción

Corrige los acrónimos incorrectos en el enum `Disciplina` descubiertos al comparar el sistema con el dataset real "Apnea Indoor Buenos Aires 2025" (HITO-17).

## RFs corregidos

| RF | Corrección |
|----|-----------|
| RF-GT-02 | `DYNB` → `DBF` (Dynamic Bi-Fins) — acrónimo FAAS correcto |
| RF-GT-02 | `SPE2X50` → `SPE` — acrónimo simplificado según nomenclatura real |

## Discrepancias resueltas

| DISC | Descripción | Severidad |
|------|-------------|-----------|
| DISC-02 | `DYNB` ≠ `DBF` | CRÍTICO |
| DISC-03 | `SPE2X50` ≠ `SPE` | CRÍTICO |

## Contexto

Hallazgos del análisis HITO-17 sobre datos reales de competencia. Los acrónimos incorrectos habrían causado inconsistencias al importar resultados de torneos reales.

## Tests

Corrección propagada a todos los tests con fixtures que usaban los acrónimos anteriores.

## Estado

✅ Completado — 2026-04-03

## Trazabilidad

- **Implementa:** [[rf/RF-GT-02-disciplinas-configurables]]
- **Código sin página de componente propia:** `src/competencia/domain/value_objects/disciplina.py`
