# PLAN-SP-ADJ-03 — Sprint de Ajuste Post-SP3

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-03 |
| **Contexto** | Ajuste documental y arquitectónico post-SP3 (BL-003) |
| **Fuente** | HITO-14 — Análisis crítico metodología y estructura |
| **Branch base** | `develop` (después de cerrar BL-003) |
| **Estado** | ⏳ Pendiente — ejecutar después de cerrar SP3 |

---

## Objetivo

Cerrar las debilidades de mayor impacto identificadas en HITO-14, más cualquier deuda
adicional que emerja durante INC-3.3/3.4/3.5.

El criterio para iniciar SP-ADJ-03 es que todos los incrementos de SP3 estén
mergeados en `develop` y BL-003 esté lista para taggear.

---

## Acciones base (HITO-14)

| ID | Debilidad | Acción | Tipo | Prioridad |
|----|-----------|--------|------|-----------|
| D-02 | Múltiples fuentes de verdad | Simplificar README; declarar jerarquía `baseline > CLAUDE.md > README` | Documental | Alta |
| D-03 | Documentación desalineada | Corregir README, `docker-compose.yml`, `docs/dominio/02-arquitectura_referencia.md`, `docs/dominio/04-estrategia_desarrollo.md` — eliminar refs a PostgreSQL | Documental | Alta |
| D-05 | Regla hexagonal no cumplida en `api/` | Composition root explícito en `app.py` — sacar inyección de repositorios concretos de los routers | Arquitectónico | Alta |
| D-06 | Imports cross-BC en `resultados/` | Auditar `resultados_competencia_adapter.py` y clasificar: aceptable / temporal / corregir | Arquitectónico | Media-Alta |

---

## Acciones adicionales (a completar al cierre de SP3)

| ID | Descripción | Tipo | Estado |
|----|-------------|------|--------|
| — | (se completará con deuda que emerja en INC-3.3/3.4/3.5) | — | ⏳ |

---

## Descartado por ahora

- **D-04** (`/implement-us` no ajustado al proyecto): el skill produce estructura correcta con adaptación manual mínima. Reescribir el perfil no es prioritario hasta tener más evidencia de fricción sistemática.
- **D-01/D-07/D-08/D-09/D-10**: observaciones válidas, impacto inmediato bajo. Revisar en retrospectiva SP3.

---

*Iniciado: 2026-03-31 — basado en HITO-14*
*Actualizar a medida que avanza SP3*
