# ARTEFACTOS-WORKFLOW — Clasificación de Artefactos del Proceso de Desarrollo

**Versión:** 1.0
**Fecha:** 2026-04-04
**Fuente:** HITO-14 D-01 — poda metodológica al cierre de SP3
**Complementa:** `docs/plans/WORKFLOW-DESARROLLO.md`

---

## Propósito

Este documento clasifica cada artefacto del workflow por su carácter operativo:

| Categoría | Definición |
|-----------|------------|
| **obligatorio** | Sin él el workflow no funciona o la trazabilidad se rompe |
| **opcional** | Aporta valor pero se puede omitir sin consecuencias sistémicas |
| **derivado** | Se genera automáticamente — no requiere mantenimiento manual |

El objetivo es identificar qué se puede eliminar o automatizar para reducir el overhead de sesión.

---

## Nivel US-IEDD

| Artefacto | Categoría | Cuándo se crea | Quién lo crea |
|-----------|-----------|----------------|---------------|
| `feature/US-X.Y.Z-*` (branch) | **obligatorio** | Antes de cualquier trabajo | Claude |
| `.claude/tracking/US-X.Y.Z-tracking.json` | **obligatorio** | Fase 0 de `/implement-us` | `/implement-us` |
| `docs/specs/spX/US-X.Y.Z.md` | **obligatorio** | Antes del sprint, Fase 0 lo usa como input | Claude (planificación) |
| GitHub Issue | **obligatorio** | Al inicio del sprint | Claude |
| Tests (unit + integration + BDD) | **obligatorio** | Fases 5–6 de `/implement-us` | `/implement-us` |
| `docs/reports/US-X.Y.Z-report.md` | **obligatorio** | Fase 10 de `/implement-us` | `/implement-us` |
| `quality/reports/codeguard/US-X.Y.Z-*.txt` | **derivado** | Pre-commit hook automático | CodeGuard |
| `quality/reports/designreviewer/*` (pre-push) | **derivado** | Pre-push hook automático | DesignReviewer |
| `.feature` file (BDD) | **opcional** | Fase 5, si hay comportamiento observable desde fuera | `/implement-us` |

---

## Nivel Incremento

| Artefacto | Categoría | Cuándo se crea | Quién lo crea |
|-----------|-----------|----------------|---------------|
| Ajuste de umbrales `pyproject.toml` (CBO/WMC) | **obligatorio** | Antes de la primera US del incremento | Claude |
| Registro en BL activa (inventario de CIs) | **obligatorio** | Al cerrar el último PR del incremento | Claude |
| DesignReviewer manual post-incremento | **obligatorio** | Después del último merge del incremento | Claude |
| `quality/reports/designreviewer/INC-X.Y-report.txt` | **opcional** | Solo si hay hallazgos o CRITICAL | Claude |
| Mini-retrospectiva en BL activa | **opcional** | Al cierre del incremento, si hay aprendizajes | Claude |
| Cierre del Issue en GitHub | **derivado** | Automático al mergear PR con referencia `Closes #N` | GitHub |

---

## Nivel Subproyecto (Baseline)

| Artefacto | Categoría | Cuándo se crea | Quién lo crea |
|-----------|-----------|----------------|---------------|
| `docs/plans/spX/SP-N-candidatas.md` | **obligatorio** | Planificación del SP, antes de la primera US | Claude |
| `docs/plans/spX/PLAN-SP-N.md` | **obligatorio** | Planificación del SP | Claude |
| `quality/reports/architectanalyst/BL-NNN-*.json` | **obligatorio** | Antes del merge a main | Claude (manual) |
| `quality/reports/uat/SPN/design.md` | **obligatorio** | Antes del UAT | Claude |
| `tests/uat/spN/` (seed + script) | **obligatorio** | Antes del UAT | Claude |
| `quality/reports/uat/SPN/report.md` | **obligatorio** | Al ejecutar el UAT | Claude |
| `.cm/baselines/BL-NNN.md` | **obligatorio** | Al cerrar el SP | Claude |
| Actualización CLAUDE.md §14 | **obligatorio** | Al cerrar el SP | Claude |
| Merge develop → main + tag vN | **obligatorio** | Al cerrar el SP | Claude |
| `docs/contexto/HITO-N-*.md` | **opcional** | Si hay aprendizajes experimentales relevantes | Claude |
| ADR nuevo | **opcional** | Si hay decisión arquitectónica nueva | Claude |
| Actualización matrix.md | **opcional** | Si el SP incluye SP-ADJ con US-ADJ-N.M | Claude |
| SP-ADJ (sprint de ajuste) | **opcional** | Si hay deuda acumulada técnica o documental | Victor + Claude |
| `.cm/baselines/BL-NNN-arquitectura.json` (copia) | **derivado** | Copia del reporte ArchitectAnalyst | Claude |

---

## Observaciones de Poda (post-SP3)

### Lo que se puede eliminar sin pérdida sistémica

- **`quality/reports/designreviewer/` por US individual:** el pre-push automático ya persiste el resultado en el log del hook. El archivo manual por US es redundante salvo que haya CRITICAL que documentar.
- **Mini-retrospectiva en BL por incremento:** valioso si hay aprendizajes, pero en incrementos simples (CRUD) genera overhead sin retorno. Condicionarlo a si hay algo relevante para el paper o futuras sesiones.
- **`.feature` files para lógica de dominio pura:** pytest-bdd agrega overhead real (datatables, glue code, lenguaje Gherkin). Reservar para flujos end-to-end observables desde el exterior.

### Lo que no se puede automatizar fácilmente

- **DesignReviewer manual post-incremento:** requiere lectura consciente del reporte consolidado, no solo ejecución.
- **ArchitectAnalyst:** ídem — su valor está en la interpretación de tendencias, no en la ejecución.
- **UAT design.md:** requiere conocimiento del dominio para diseñar los checks correctos.

### Candidatos a automatización en SP4

- **Cierre de Issue GitHub** ya es automático con `Closes #N` en el PR.
- **Registro en BL activa post-incremento:** podría generarse parcialmente desde git log + tracker.

---

*Creado: 2026-04-04 — SP-ADJ-05 / SP-ADJ-5.1 — HITO-14 D-01*
