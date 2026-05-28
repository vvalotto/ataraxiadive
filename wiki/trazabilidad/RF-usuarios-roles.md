---
title: "RF — Usuarios, Roles y Permisos"
type: trazabilidad-rf
last_updated: "2026-05-20"
sources:
  - docs/dominio/05-requerimientos_funcionales.md
us_refs:
  - US-3.2.1
  - US-3.4.2
---

# RF — Usuarios, Roles y Permisos

Requerimientos funcionales del área de identidad y permisos. Fuente: elicitación inicial (feb 2026).

> ⚠️ Los IDs de esta página (RF-US-*) corresponden a la elicitación inicial. Los IDs canónicos del proyecto están en la matriz de trazabilidad.

## Requerimientos definidos

| ID | Requerimiento | Respuesta / Regla |
|----|--------------|-------------------|
| [[RF-US-01]] | ¿El administrador puede crear múltiples organizadores por torneo? | **No.** Un organizador por torneo. |
| [[RF-US-02]] | ¿Un usuario puede tener múltiples roles? | **Sí.** (ej: organizador en un torneo y juez en otro) |
| [[RF-US-03]] | ¿Cómo se autentican los atletas? | Mail + contraseña. |
| [[RF-US-04]] | ¿Un juez necesita ser asignado a disciplinas específicas? | **Sí.** Se asigna un juez a cada [[disciplina]]. |
| [[RF-US-05]] | ¿Los atletas pueden ver resultados de otros durante la competencia? | **Solo los resultados finales.** No en tiempo real. |

## Reglas de negocio clave

- **Un organizador por torneo** — el administrador no puede asignar múltiples.
- **Roles múltiples:** un usuario puede ser organizador en un torneo y juez en otro.
- **Autenticación:** mail + contraseña (no OAuth, no magic link en la elicitación inicial).
- **Asignación de juez:** obligatoria por disciplina — no puede actuar en cualquier disciplina sin asignación.
- **Visibilidad de resultados para atletas:** solo resultados finales publicados, no en tiempo real durante la ejecución.

## BCs que implementan esta área

- [[identidad]] — autenticación, roles, gestión de usuarios
