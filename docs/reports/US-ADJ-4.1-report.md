# Reporte de Implementación — US-ADJ-4.1
## Renombrar disciplinas DYNB→DBF y SPE2X50→SPE

**Sprint:** SP-ADJ-04
**Branch:** `feature/US-ADJ-4.1-renombrar-disciplinas`
**Fecha:** 2026-04-03

---

## Resumen

Refactor de lenguaje ubicuo: los acrónimos `DYNB` y `SPE2X50` fueron reemplazados por
los acrónimos oficiales AIDA `DBF` y `SPE` en todo el codebase.

El error fue detectado al contrastar el modelo con el dataset real "Apnea Indoor Buenos Aires 2025"
(HITO-17, DISC-02 y DISC-03).

---

## Cambios implementados

### Código
| Archivo | Cambio |
|---------|--------|
| `src/shared/domain/value_objects/disciplina.py` | `DYNB="DYNB"` → `DBF="DBF"`, `SPE2X50="SPE2X50"` → `SPE="SPE"`, docstring actualizado |

### Tests (7 archivos)
| Archivo | Cambio |
|---------|--------|
| `tests/unit/torneo/domain/test_disciplinas_torneo.py` | `Disciplina.DYNB` → `Disciplina.DBF` (3 ocurrencias) |
| `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py` | `Disciplina.DYNB` → `Disciplina.DBF` |
| `tests/unit/competencia/domain/test_disciplina_descriptor.py` | `Disciplina.DYNB` → `Disciplina.DBF` |
| `tests/integration/torneo/test_disciplinas_torneo_api.py` | `"DYNB"` → `"DBF"` (2 ocurrencias) |
| `tests/features/steps/test_US_3_4_1_steps.py` | `Disciplina.DYNB` → `Disciplina.DBF` |
| `tests/features/US-3.4.1-asignar-disciplinas-juez.feature` | `DYNB` → `DBF` |
| `tests/features/US-2.2.1-disciplina-descriptor.feature` | `DYNB` → `DBF` |

### BDD nuevo
| Archivo | Descripción |
|---------|-------------|
| `tests/features/US-ADJ-4.1-disciplinas-acronimos-aida.feature` | 4 escenarios: DBF válido, SPE válido, DYNB rechazado, SPE2X50 rechazado |
| `tests/features/steps/disciplinas_acronimos_steps.py` | Step definitions para los 4 escenarios |

### Documentación
| Archivo | Cambio |
|---------|--------|
| `docs/design/domain-model.md` | Tabla Disciplina: `DYNB, SPE2X50` → `DBF, SPE` |
| `docs/dominio/05-requerimientos_funcionales.md` | RF-GT-02 y RF-EJ-08 actualizados |
| `docs/plans/sp-adj-04/US-ADJ-4.1-plan.md` | Plan de implementación creado |

---

## Resultados de calidad

| Gate | Resultado |
|------|-----------|
| pytest (suite completa) | ✅ 757 passed, 0 failed |
| BDD US-ADJ-4.1 | ✅ 4/4 escenarios pasando |
| CodeGuard | ✅ 0 errores, 0 advertencias |
| DesignReviewer | ✅ 0 CRITICAL |

---

## Trazabilidad

| Elemento | Referencia |
|----------|------------|
| Discrepancias origen | DISC-02 (DYNB≠DBF), DISC-03 (SPE2X50≠SPE) |
| Análisis | HITO-17 · `.work/analisis-discrepancias-dataset-reales.md` |
| INV aplicada | INV-D-01: acrónimos deben coincidir con estándar AIDA/CMAS |
