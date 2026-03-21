# Workflow de Desarrollo — AtaraxiaDive

**Versión:** 1.2
**Fecha:** 2026-03-21
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
  └── develop ← integración continua — recibe PRs individuales de cada US
        ├── feature/US-X.Y.Z-descripcion-corta  ← una branch por US-IEDD
        ├── feature/inc-X.Y-descripcion-corta   ← incrementos técnicos sin US
        └── fix/descripcion-corta               ← correcciones
```

### Nomenclatura de branches

| Tipo | Patrón | Ejemplo |
|------|--------|---------|
| US-IEDD | `feature/US-X.Y.Z-descripcion-corta` | `feature/US-1.2.1-registrar-ap` |
| Incremento técnico (sin US) | `feature/inc-X.Y-descripcion-corta` | `feature/inc-1.1-fundacion-tecnica` |
| Corrección | `fix/descripcion-corta` | `fix/invariante-ap-nulo` |

**Reglas:**
- Cada US-IEDD tiene su propia branch — PR individual directo a `develop`.
- Los incrementos técnicos (sin US-IEDD, como Inc 1.1) usan `feature/inc-X.Y-*` con commits por tarea.
- `develop` se mergea a `main` solo al cerrar un Subproyecto (Baseline).
- Descripción en kebab-case, máximo 4 palabras, en español.

---

## 5. Ciclo por US-IEDD

```
1. Crear branch feature/US-X.Y.Z-descripcion desde develop
2. Cambiar label del Issue: backlog → in-progress
3. Ejecutar /implement-us US-X.Y.Z  (10 fases, input: docs/plans/US-X.Y.Z.md)
4. [AUTO] CodeGuard corre en cada commit (pre-commit hook, ~5s, solo advierte)
5. Commits atómicos con referencia: feat(domain): ... [US-X.Y.Z]
6. Abrir PR hacia develop con /pr  → DesignReviewer corre en pre-push (bloquea si CRITICAL)
7. Merge del PR — Issue se cierra automáticamente
```

---

## 6. Ciclo por Incremento

Un Incremento cierra cuando todas sus US-IEDD están mergeadas a `develop`
y el DoD de integración es verificable de punta a punta.

```
1. Todas las US del Incremento mergeadas a develop (PR individual por US)
2. Verificar DoD de integración (test end-to-end observable)
3. [MANUAL] Correr DesignReviewer sobre el estado consolidado del incremento:
   designreviewer src/
   → Complementa el DesignReviewer automático (pre-push por US) — aquí se verifica
     que la interacción entre todas las US del incremento no introdujo violations.
   → Si hay CRITICAL: abrir fix/ branch, corregir, PR a develop
4. Registrar en BL-00N activa:
   → Agregar CIs nuevos a la tabla de inventario
   → Actualizar métricas del incremento
   → Registrar decisiones técnicas relevantes
5. Documentar aprendizajes experimentales en HITO-N si hay observaciones relevantes
6. Mini-retrospectiva: ¿qué funcionó? ¿qué ajustar en el próximo?
7. Cerrar Issue del incremento en GitHub con comentario de DoD verificado
```

**Para incrementos técnicos sin US (ej: Inc 1.1):**
```
1. Branch feature/inc-X.Y-descripcion desde develop
2. Commits por tarea (scaffold, migrations, health-check, etc.)
3. [AUTO] CodeGuard en cada commit
4. Abrir PR con /pr → DesignReviewer pre-push
5. Merge → verificar DoD
6. Registrar en BL-00N + HITO-N si hay aprendizajes
```

**DesignReviewer manual (en cualquier momento):**
```bash
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

| Nivel | Herramienta | Cuándo | Modo | Acción |
|-------|-------------|--------|------|--------|
| Commit | CodeGuard | Pre-commit (automático) | `codeguard src/` | Advierte, no bloquea |
| PR a develop | DesignReviewer | Pre-push (automático) | `designreviewer src/` | Bloquea si CRITICAL |
| Cierre de Incremento | DesignReviewer | Manual, después del último merge | `designreviewer src/` | Confirmar cero CRITICAL |
| Cierre de Subproyecto | ArchitectAnalyst | Manual, antes de merge a main | `architectanalyst src/ --sprint-id BL-NNN --format json` | Informa tendencias |

### Flujo de bloqueo por DesignReviewer

```
push → pre-push hook → designreviewer src/
  ├── OK: push procede
  └── CRITICAL: push bloqueado
        → fix/descripcion branch
        → corregir violación
        → PR a develop
        → push ok
```

---

## 9. Relación con /implement-us

El skill `/implement-us US-X.Y.Z` lee `docs/plans/US-X.Y.Z.md` como input y
ejecuta las 10 fases dentro de la branch `feature/US-X.Y.Z-descripcion`.
Al terminar, se abre PR con `/pr` y se mergea directo a `develop`.

```
# Ejemplo Inc 1.2 — 6 US individuales

feature/US-1.2.1-registrar-ap     → /implement-us → /pr → merge develop
feature/US-1.2.2-llamar-atleta    → /implement-us → /pr → merge develop
feature/US-1.2.3-registrar-resultado → /implement-us → /pr → merge develop
...
(última US mergeada) → designreviewer src/ manual → verificar DoD 1.2 → mini-retro
```

---

*v1.3 — 2026-03-21. Ciclo por incremento: agregar registro en BL activa + HITO experimental.*
*Complementa `docs/dominio/04-estrategia_desarrollo.md`.*
