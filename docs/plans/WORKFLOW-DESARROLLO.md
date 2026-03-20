# Workflow de Desarrollo — AtaraxiaDive

**Versión:** 1.1
**Fecha:** 2026-03-20
**Alcance:** Convenciones de branching, PRs, quality gates y gestión administrativa para SP1 en adelante

---

## 1. Jerarquía de Trabajo

```
SP (Subproyecto)          → Baseline (BL-NNN) + tag git (v0.N.0) + Milestone GitHub
  └── Incremento (X.Y)    → PR a develop + DoD de integración verificable
        └── US-IEDD (X.Y.Z) → GitHub Issue + docs/plans/US-X.Y.Z.md + branch feature/
```

No existe un nivel "iteración" — el Incremento cubre esa función.

---

## 2. Gestión Administrativa (GitHub)

### División de responsabilidades

| Artefacto | Dónde vive | Propósito |
|-----------|-----------|-----------|
| **GitHub Issue** | GitHub Issues | Fuente de verdad del estado — qué hay que hacer, criterios de aceptación, seguimiento |
| **`docs/plans/US-X.Y.Z.md`** | Repositorio | Artefacto técnico de implementación — precondición, postcondición, invariantes IEDD, input de `/implement-us` |

### Estructura en GitHub

- **Milestones** = uno por Subproyecto (`SP1 — La Performance`, `SP2 — La Competencia`, etc.)
- **Labels** = `us-iedd`, `incremento-1.1`, `incremento-1.2`, `blocked`, `in-progress`, `done`
- **Sin Project board** — los Milestones + Labels proveen seguimiento suficiente para desarrollo en solitario

### Template de Issue (US-IEDD)

```markdown
## Descripción
Como <rol>, quiero <acción> para <valor>.

## Criterios de Aceptación
- [ ] ...

## Precondición
...

## Postcondición
...

## Invariantes
- INV-1: ...

## Referencias
- Incremento: X.Y
- Bounded Context: ...
- docs/plans/US-X.Y.Z.md
```

---

## 3. Ciclo de Elaboración de US por SP

```
1. Claude elabora el archivo de US candidatas: docs/plans/SP-N-candidatas.md
   → Lista todas las US del SP con descripción, criterios y estimación
2. Victor revisa y aprueba (con ajustes si corresponde)
3. Por cada US aprobada:
   a. Crear GitHub Issue con template US-IEDD → asignar Milestone + Labels
   b. Crear docs/plans/US-X.Y.Z.md con el detalle técnico completo
4. Las US quedan en estado "backlog" hasta iniciar su Incremento
```

---

## 4. Branching

```
main          ← baselines etiquetadas (v0.1.0, v0.2.0...)
  └── develop ← integración continua — recibe PRs de Incremento
        └── feature/US-X.Y.Z-descripcion  ← una branch por US-IEDD
```

**Reglas:**
- Cada US-IEDD tiene su propia branch `feature/US-X.Y.Z-descripcion`.
- Las branches de US se mergean a `develop` **al cerrar el Incremento**, no individualmente.
- `develop` se mergea a `main` solo al cerrar un Subproyecto (Baseline).

---

## 5. Ciclo por US-IEDD

```
1. Crear branch feature/US-X.Y.Z desde develop
2. Cambiar label del Issue: backlog → in-progress
3. Ejecutar /implement-us US-X.Y.Z  (10 fases, input: docs/plans/US-X.Y.Z.md)
4. CodeGuard corre automático en cada commit (pre-commit, no bloquea)
5. Commit atómico con referencia: feat(domain): ... [US-X.Y.Z]
6. Branch queda lista; label → done (branch pendiente de merge al cerrar Incremento)
```

---

## 6. Ciclo por Incremento

Un Incremento agrupa una o más US-IEDD relacionadas que juntas producen
una funcionalidad cohesiva y verificable de punta a punta.

```
1. Todas las US del Incremento en estado done en sus branches
2. Merge de todas las branches feature/ a develop (local)
3. Abrir PR: Incremento X.Y → develop  (referencia los Issues de las US)
4. Push a develop → pre-push hook ejecuta DesignReviewer automáticamente
   → Bloquea el push si hay violaciones CRITICAL
   → Corregir y re-pushear si es necesario
5. Verificar DoD de integración (test end-to-end observable)
6. Merge del PR en GitHub — Issues de las US se cierran automáticamente
7. Mini-retrospectiva: ¿qué funcionó? ¿qué ajustar en el próximo?
```

**El PR cubre el Incremento completo**, no cada US individual. Esto le da
coherencia arquitectónica al review: la funcionalidad es verificable de
punta a punta antes del análisis de diseño.

**DesignReviewer manual (opcional):**
```bash
# Correr manualmente en cualquier momento antes del push
designreviewer src/
```

---

## 7. Ciclo por Subproyecto (Baseline)

```
1. Todos los Incrementos del SP cerrados en develop — Milestone al 100%
2. Correr ArchitectAnalyst manualmente:
   architectanalyst src/ --sprint-id BL-NNN --format json \
     > quality/reports/architectanalyst/BL-NNN-arquitectura.json
   → Leer y analizar el reporte antes de continuar
   → Copiar también a .cm/baselines/BL-NNN-arquitectura.json
3. Registrar métricas en .cm/baselines/BL-NNN.md
4. Merge develop → main
5. Tag: git tag vN.0.0  — cerrar Milestone en GitHub
6. Retrospectiva documentada en BL-NNN.md (alimenta el libro y el paper)
```

**ArchitectAnalyst es siempre manual** — su valor está en la lectura consciente
del reporte antes de cerrar el Baseline, no en la automatización.

---

## 8. Quality Gates por Nivel

| Nivel | Herramienta | Momento | Acción |
|-------|-------------|---------|--------|
| US-IEDD (commit) | CodeGuard | Pre-commit automático | Advierte, no bloquea |
| Incremento (PR merge) | DesignReviewer | Antes de merge a develop | Bloquea si CRITICAL |
| Subproyecto (Baseline) | ArchitectAnalyst | Al cerrar el SP | Informa tendencias |

---

## 9. Relación con /implement-us

El skill `/implement-us US-X.Y.Z` lee `docs/plans/US-X.Y.Z.md` como input y
ejecuta las 10 fases dentro de la branch `feature/US-X.Y.Z`. Al terminar,
la branch está lista pero **no se mergea** hasta que el Incremento completo
esté listo para el PR.

```
/implement-us US-1.1.1  → branch feature/US-1.1.1 lista, Issue → done
/implement-us US-1.1.2  → branch feature/US-1.1.2 lista, Issue → done
→ PR Incremento 1.1: merge ambas branches + DesignReviewer + DoD → Issues cerrados
```

---

*v1.1 — 2026-03-20. Complementa `docs/dominio/04-estrategia_desarrollo.md`.*
