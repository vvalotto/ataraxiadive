# Reporte US-6.4.6 — Decisión ARCH-03 + SRP RankingCompetencia + monitoreo identidad/shared

**Fecha:** 2026-05-10  
**Incremento:** INC-6.4 — Deuda Técnica Sistema  
**Duración estimada:** 40 min | **Real:** ~45 min  
**Estado:** ✅ Completado

---

## Resumen Ejecutivo

US documental/analítica que cierra formalmente los 4 hallazgos pendientes de INC-6.4:
- **ARCH-03**: ACL aceptable — sin imports cross-BC
- **DR-01**: Falso positivo ES — LCOM=2 inherente al patrón Aggregate+Reconstitución
- **AA-02**: `identidad` D=0.67 — no intervenir en v1.0
- **AA-04**: `shared` D=0.63 — diferir a post-despliegue

---

## Artefactos Creados

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `.cm/baselines/BL-006.md` | Nuevo | Baseline draft SP6 con decisiones INC-6.4 |
| `tests/features/US-6.4.6-cierre-arch-decisiones.feature` | Nuevo | 5 escenarios BDD |
| `tests/features/steps/arch_decisiones_646_steps.py` | Nuevo | Steps BDD |
| `tests/unit/resultados/domain/test_arch_diagnosticos_646.py` | Nuevo | 4 tests unitarios de análisis arquitectural |
| `docs/plans/sp6/US-6.4.6-plan.md` | Nuevo | Plan de implementación |
| `quality/reports/designreviewer/INC-6.4-report.txt` | Nuevo | DesignReviewer cierre INC-6.4 |
| `docs/traceability/matrix.md` | Actualizado | §32 INC-6.4 cerrado, US-6.4.1/6.4.2 corregidas a Done, v1.42 |
| `docs/plans/sp6/PLAN-SP6.md` | Actualizado | ARCH-03 y DR-01 cerrados con decisión |
| `docs/specs/sp6/US-6.4.6.md` | Actualizado | Estado → Done |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| black | ✅ OK |
| isort | ✅ OK |
| ruff | ✅ OK |
| Unit tests (4 nuevos) | ✅ 4/4 |
| Tests unitarios totales | ✅ 676/676 |
| Tests integración | ✅ 208/208 |
| BDD (5 escenarios) | ✅ 5/5 |
| DesignReviewer INC-6.4 | ✅ 0 CRITICAL · 253 WARNING · should_block=false |

---

## Decisiones Registradas en BL-006

### ARCH-03 — ACL aceptable ✅
`ResultadosCompetenciaAdapter` no importa `competencia.*`. Usa `EventStorePort` (shared) como abstracción.
Riesgo residual: renombrar event types silencia el cambio — mitigado por tests de integración.

### DR-01 — Falso positivo ES ✅
`RankingCompetencia` LCOM=2 es inherente al patrón ES: grupo comando (`calcular`) + grupo reconstitución (`reconstitute`, `_apply_stored`, `_rehidratar`). Helpers de módulo ya extraídos correctamente.

### AA-02 — identidad D=0.67: no intervenir en v1.0
Tendencia ↓ desde 0.87 (BL-004). Criterio de intervención futura: D > 0.70 en BL-007.

### AA-04 — shared D=0.63: diferir a post-despliegue
Estable. Reducir D requiere reestructuración sistémica — impacto alto para v1.0.

---

## DesignReviewer INC-6.4 — Resultado Consolidado

**0 CRITICAL · 253 WARNING · should_block=false**

Reducción de −5 WARNING respecto a INC-6.3 (258→253) — efecto neto positivo de los refactors
de US-6.4.3, 6.4.4, 6.4.5.

---

*Generado: 2026-05-10 — INC-6.4 ✅ cerrado*
