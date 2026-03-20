# Workflow de Desarrollo — AtaraxiaDive

**Versión:** 1.0
**Fecha:** 2026-03-20
**Alcance:** Convenciones de branching, PRs y quality gates para SP1 en adelante

---

## 1. Jerarquía de Trabajo

```
SP (Subproyecto)          → Baseline (BL-NNN) + tag git (v0.N.0)
  └── Incremento (X.Y)    → PR a develop + DoD de integración verificable
        └── US-IEDD (X.Y.Z) → branch feature/ + commit atómico
```

No existe un nivel "iteración" — el Incremento cubre esa función.

---

## 2. Branching

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

## 3. Ciclo por US-IEDD

```
1. Crear branch feature/US-X.Y.Z
2. Ejecutar /implement-us US-X.Y.Z  (10 fases)
3. CodeGuard corre automático en cada commit (pre-commit, no bloquea)
4. Commit atómico con referencia: feat(domain): ... [US-X.Y.Z]
5. Branch queda lista; se acumula hasta cerrar el Incremento
```

---

## 4. Ciclo por Incremento

Un Incremento agrupa una o más US-IEDD relacionadas que juntas producen
una funcionalidad cohesiva y verificable de punta a punta.

```
1. Todas las US del Incremento están implementadas en sus branches
2. Merge de todas las branches feature/ a develop (squash opcional)
3. Abrir PR: feature/US-X.Y.* → develop
4. Correr DesignReviewer: designreviewer src/
   → Bloquea el merge si hay violaciones CRITICAL
5. Verificar DoD de integración (test end-to-end observable)
6. Merge a develop
7. Mini-retrospectiva: ¿qué funcionó? ¿qué ajustar en el próximo?
```

**El PR cubre el Incremento completo**, no cada US individual. Esto le da
coherencia arquitectónica al review: la funcionalidad es verificable de
punta a punta antes del análisis de diseño.

---

## 5. Ciclo por Subproyecto (Baseline)

```
1. Todos los Incrementos del SP están cerrados en develop
2. Correr ArchitectAnalyst: architectanalyst src/ --sprint-id BL-NNN --format json
   → Guardar output en .cm/baselines/BL-NNN-arquitectura.json
3. Registrar métricas en .cm/baselines/BL-NNN.md
4. Merge develop → main
5. Tag: git tag vN.0.0
6. Retrospectiva documentada en BL-NNN.md (alimenta el libro y el paper)
```

---

## 6. Quality Gates por Nivel

| Nivel | Herramienta | Momento | Acción |
|-------|-------------|---------|--------|
| US-IEDD (commit) | CodeGuard | Pre-commit automático | Advierte, no bloquea |
| Incremento (PR merge) | DesignReviewer | Antes de merge a develop | Bloquea si CRITICAL |
| Subproyecto (Baseline) | ArchitectAnalyst | Al cerrar el SP | Informa tendencias |

---

## 7. Relación con /implement-us

El skill `/implement-us US-X.Y.Z` ejecuta las 10 fases dentro de la branch
`feature/US-X.Y.Z`. Al terminar, la branch está lista pero **no se mergea**
hasta que el Incremento completo esté listo para el PR.

```
/implement-us US-1.1.1  → branch feature/US-1.1.1 lista
/implement-us US-1.1.2  → branch feature/US-1.1.2 lista
→ PR Incremento 1.1: merge ambas branches + DesignReviewer + DoD
```

---

*Documento generado en sesión 2026-03-20. Complementa `docs/dominio/04-estrategia_desarrollo.md`.*
