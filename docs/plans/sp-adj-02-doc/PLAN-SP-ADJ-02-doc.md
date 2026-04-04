# PLAN-SP-ADJ-02-doc — Sprint de Ajuste Documental Post-Revisión de Hito

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-02-doc |
| **Contexto** | Gaps documentales detectados en revisión de consistencia BL-002 |
| **Revisión fuente** | `.work/revision-consistencia.md` |
| **Branch base** | `develop` |
| **Fecha inicio** | 2026-03-28 |

---

## Objetivo

Cerrar los 12 gaps documentales identificados en la revisión de hito (bloques A, C, D, E),
dejando todos los artefactos sincronizados con el estado real del proyecto al cierre de BL-002.
El resultado debe ser que cualquier sesión nueva arranque con contexto 100% correcto.

---

## US-IEDD del Sprint

| US | Gaps | Descripción | Artefactos | Prioridad |
|----|------|-------------|------------|-----------|
| US-ADJ-2.1 | D-01, D-02, D-03 | Actualizar CLAUDE.md: §14 estado actual + §9 patrón SP-ADJ + §5 HITOs en contexto | `CLAUDE.md` | Alta |
| US-ADJ-2.2 | C-03, C-04 | Corregir baselines: BL-002.md tag v0.3.0 + BL-001.md fecha y tag de cierre | `.cm/baselines/BL-001-sp1-la-performance.md` `.cm/baselines/BL-002.md` | Alta |
| US-ADJ-2.3 | A-01, A-02, C-01, C-02 | Actualizar matrix.md: agregar sección SP-ADJ-01 + renumerar secciones duplicadas | `docs/traceability/matrix.md` | Media |
| US-ADJ-2.4 | A-03, A-04 | Actualizar domain-model.md: notas SP pendientes (SP2→SP3) | `docs/design/domain-model.md` | Baja |
| US-ADJ-2.5 | E-02 | Crear INDICE-HITOS.md: tabla resumen de los 13 HITOs con SP, hipótesis y ubicación | `docs/contexto/INDICE-HITOS.md` | Baja |

**Orden de implementación:** US-ADJ-2.1 → US-ADJ-2.2 → US-ADJ-2.3 → US-ADJ-2.4 → US-ADJ-2.5

Rationale: los más críticos primero (contexto de sesión + tags git), luego trazabilidad, luego mejoras menores.

---

## DoD del Sprint

- [ ] CLAUDE.md §14 refleja BL-002/v0.3.0 cerrado, SP3 como próximo paso
- [ ] CLAUDE.md §9 incluye el patrón SP-ADJ en la jerarquía
- [ ] CLAUDE.md §5 menciona HITOs en `docs/contexto/`
- [ ] BL-002.md dice `Git tag: v0.3.0`
- [ ] BL-001.md tiene fecha de cierre 2026-03-24 y tag v0.2.0 completos
- [ ] matrix.md incluye sección SP-ADJ-01 con US-ADJ-1.1 a US-ADJ-1.5
- [ ] matrix.md sin secciones con numeración duplicada
- [ ] domain-model.md notas de SP actualizadas a SP3
- [ ] `docs/contexto/INDICE-HITOS.md` creado con los 13 HITOs
- [ ] Cero tests rotos (los cambios son solo documentales)

---

## Gaps fuera de scope (SP-ADJ-02-code)

Los siguientes gaps de código se tratan en el sprint paralelo:

| Gap | Descripción |
|-----|-------------|
| B-01 | `Disciplina` → `shared/domain/` |
| B-02 | Imports cross-BC en `resultados/application/` |
| B-03 | Composition root en `app.py` |
| B-04 | Imports cross-BC en `resultados/api/` |
| B-05 | DIP fix en `competencia/api/router.py` |
| D-04 | Actualizar `memory/project_solid_deuda_sp2.md` (post-resolución B-05) |

---

## Branching

```
develop
  └── docs/US-ADJ-2.1-claude-md
  └── docs/US-ADJ-2.2-baselines
  └── docs/US-ADJ-2.3-matrix
  └── docs/US-ADJ-2.4-domain-model
  └── docs/US-ADJ-2.5-indice-hitos
```

---

## Archivos de especificación

- `docs/specs/sp-adj-02-doc/US-ADJ-2.1.md`
- `docs/specs/sp-adj-02-doc/US-ADJ-2.2.md`
- `docs/specs/sp-adj-02-doc/US-ADJ-2.3.md`
- `docs/specs/sp-adj-02-doc/US-ADJ-2.4.md`
- `docs/specs/sp-adj-02-doc/US-ADJ-2.5.md`

---

## Referencias

- Revisión de hito: `.work/revision-consistencia.md`
- Plan del sprint de código: `docs/plans/sp-adj-02-code/PLAN-SP-ADJ-02-code.md` (pendiente)
- Patrón SP-ADJ: `docs/contexto/HITO-13-SP-ADJ-DEUDA-TECNICA-COMO-ETAPA-FORMAL.md`
