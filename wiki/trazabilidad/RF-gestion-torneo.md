---
title: "RF — Gestión del Torneo"
type: trazabilidad-rf
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
us_refs:
  - US-3.1.1
  - US-3.1.2
  - US-3.3.2
  - US-4.1.3
  - US-ADJ-4.1
---

# RF — Gestión del Torneo

Requerimientos funcionales del área de gestión del [[torneo]]. Fuente: elicitación inicial (feb 2026).
Para trazabilidad vigente hacia USs ver `docs/traceability/matrix.md` (pendiente Fase 3).

> ⚠️ Los IDs de esta página (RF-GT-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID | Requerimiento | Respuesta / Regla |
|----|--------------|-------------------|
| [[RF-GT-01]] | ¿Un torneo puede tener más de una sede? | **No.** Una sede por torneo. |
| [[RF-GT-02]] | ¿Qué disciplinas soporta el sistema? | **Configurable.** Inicialmente: STA, DNF, DBF, DYN, SPE. |
| [[RF-GT-03]] | ¿Pueden existir múltiples torneos activos simultáneamente? | **Sí.** |
| [[RF-GT-04]] | ¿Qué significa cancelar un torneo? | Estado cancelado conservando la información (no se elimina). |
| [[RF-GT-05]] | ¿Hay restricciones para transición entre fases? | **Sí.** Se puede volver de etapas (ej: Ejecución → Preparación). |
| [[RF-GT-06]] | ¿El cierre implica archivo o exportación? | **No.** |
| [[RF-GT-07]] | ¿Se registra la entidad organizadora (federación/club)? | **Sí.** Además del organizador como persona. |

## Reglas de negocio clave

- Las **disciplinas son configurables** — el sistema no asume un conjunto fijo.
- El set inicial es: **STA, DNF, DBF, DYN, SPE**.
- Un torneo cancelado **conserva toda su información** — no hay eliminación.
- Las transiciones entre fases **son reversibles** bajo criterio del [[roles|Organizador]].

## Pendientes en elicitación

*Ninguno en esta área.*

## BCs que implementan esta área

- [[torneo]] — gestión del ciclo de vida del torneo
- [[competencia]] — ejecución de cada disciplina dentro del torneo
