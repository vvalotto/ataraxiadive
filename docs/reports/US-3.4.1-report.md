# Reporte de Implementación — US-3.4.1

**US:** Torneo: AsignarDisciplinas + AsignarJuez
**Fecha:** 2026-04-01
**Incremento:** INC-3.4
**Branch:** feature/US-3.4.1-asignar-disciplinas-juez
**Estado:** ✅ Completo

---

## Resumen

Extensión del aggregate `Torneo` con soporte para configurar disciplinas habilitadas y asignar
jueces por disciplina. Nuevo VO `DisciplinaTorneo`, 2 commands + 1 query, 4 endpoints REST,
persistencia SQLite con migración automática de columna.

---

## Artefactos creados

| Artefacto | Tipo | Líneas |
|-----------|------|--------|
| `torneo/domain/value_objects/disciplina_torneo.py` | VO nuevo | ~30 |
| `torneo/domain/aggregates/torneo.py` | Aggregate extendido | +40 |
| `torneo/domain/exceptions.py` | Excepciones | +6 |
| `torneo/application/commands/asignar_disciplinas.py` | Command+Handler | ~30 |
| `torneo/application/commands/asignar_juez.py` | Command+Handler | ~30 |
| `torneo/application/queries/obtener_disciplinas_juez.py` | Query+Handler | ~20 |
| `torneo/infrastructure/repositories/sqlite_torneo_repository.py` | Repo extendido | +20 |
| `torneo/api/router.py` | Router extendido | +55 |
| `tests/unit/torneo/domain/test_disciplinas_torneo.py` | Tests unitarios | ~180 |
| `tests/integration/torneo/test_disciplinas_torneo_api.py` | Tests integración | ~160 |
| `tests/features/US-3.4.1-asignar-disciplinas-juez.feature` | BDD feature | ~30 |
| `tests/features/steps/test_US_3_4_1_steps.py` | BDD steps | ~170 |

---

## Tests

| Suite | Tests | Resultado |
|-------|-------|-----------|
| Unitarios dominio | 19 | ✅ 19/19 |
| Integración API | 10 | ✅ 10/10 |
| BDD escenarios | 6 | ✅ 6/6 |
| **Suite completa** | **709** | ✅ **709/709** |

Tests previos: 674 → Delta: **+35**

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Black | ✅ Formateado |
| CodeGuard | ✅ 0 errores, 1 advertencia (pre-existente) |
| DesignReviewer | ✅ 0 CRITICAL |

---

## Invariantes implementados

| ID | Descripción | Estado |
|----|-------------|--------|
| INV-TD-01 | Solo disciplinas SP3: STA, DNF, DYN, DYNB, SPE2X50 | ✅ |
| INV-TD-02 | No asignar en estado EJECUCION/PREMIACION/CERRADO | ✅ |
| INV-TD-03 | No asignar juez a disciplina que no está en el torneo | ✅ |
| INV-TD-04 | Una disciplina → máximo un juez (reasignación permitida) | ✅ |

---

## Decisiones técnicas

- `disciplinas_torneo` serializado como JSON en columna TEXT (igual que `sede` y `entidad`)
- Migración automática: `ALTER TABLE ADD COLUMN IF NOT EXISTS` en `_ensure_table()`
- `sorted()` sobre `frozenset[Disciplina]` garantiza orden determinístico en persistencia
- `DisciplinaTorneo.con_juez()` retorna nueva instancia (inmutabilidad del VO)
- RF-EJ-01 (múltiples jueces por disciplina) diferido a SP4

---

## Tiempo

| Fase | Tiempo |
|------|--------|
| Tracker | ~11 min total |

*Nota: tracker inició en Fase 0 y cubrió hasta Fase 9.*
