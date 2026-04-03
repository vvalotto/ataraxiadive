# Reporte de Implementación — US-ADJ-4.2
## Corregir orden de grilla STA a ascendente

**Sprint:** SP-ADJ-04
**Branch:** `feature/US-ADJ-4.2-orden-sta`
**Fecha:** 2026-04-03

---

## Resumen

Corrección de la política de dominio P-01: la grilla de STA ahora ordena de menor AP
a mayor AP, consistente con el dataset real "Apnea Indoor Buenos Aires 2025".

El comportamiento previo era incorrecto: trataba STA como la única disciplina con orden
descendente. La corrección aplica tanto al descriptor de disciplina como a los tests y a
la documentación que describía esa política invertida.

---

## Cambios implementados

### Código
| Archivo | Cambio |
|---------|--------|
| `src/shared/domain/value_objects/disciplina_descriptor.py` | `DisciplinaDescriptor.para(STA)` pasa de `orden_ascendente=False` a `True`; docstring alineado con P-01 corregida |

### Tests
| Archivo | Cambio |
|---------|--------|
| `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py` | STA ahora espera `orden_ascendente=True` |
| `tests/unit/competencia/domain/test_disciplina_descriptor.py` | STA ahora espera orden ascendente |
| `tests/unit/competencia/domain/test_generar_grilla.py` | Orden STA invertido a `285 → 330 → 360` |
| `tests/integration/competencia/test_generar_grilla_integration.py` | Validación de grilla STA actualizada a menor AP primero |
| `tests/integration/competencia/test_flujo_e2e_inc21.py` | DoD E2E actualizado a `120 → 180 → 300` |
| `tests/integration/e2e/test_flujo_torneo_competencia.py` | RF-PR-05 actualizado a STA ascendente |
| `tests/features/US-2.2.1-disciplina-descriptor.feature` | Escenarios BDD de descriptor y grilla STA actualizados |
| `tests/features/US-2.2.2-api-disciplina-aware.feature` | Background y expectativas de próximas performances alineadas |
| `tests/features/steps/api_disciplina_aware_steps.py` | Seed STA y expectativas de orden alineadas |
| `tests/features/steps/ejecucion_multi_andarivel_steps.py` | Comentario/documentación de orden alineados |

### Documentación
| Archivo | Cambio |
|---------|--------|
| `docs/design/event-storming-competencia.md` | P-01 corregida: STA también ordena menor AP primero |
| `docs/design/event-storming-big-picture.md` | P-05 corregida con orden ascendente para STA |
| `docs/specs/sp2/US-2.2.1.md` | Especificación histórica alineada con la política corregida |
| `docs/plans/sp2/US-2.2.1-plan.md` | Plan histórico alineado con STA ascendente |
| `docs/reports/US-2.2.1-report.md` | Reporte histórico alineado con STA ascendente |
| `docs/plans/sp3/US-3.3.2-plan.md` | Referencia RF-PR-05 corregida |

---

## Resultados de calidad

| Gate | Resultado |
|------|-----------|
| Unit tests focalizados | ✅ 25/25 |
| Integración focalizada | ✅ 11/11 |
| BDD focalizado | ✅ 22/22 |
| Regresión focalizada total | ✅ 58/58 |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py tests/unit/competencia/domain/test_generar_grilla.py -q
./.venv/bin/pytest tests/unit/competencia/domain/test_disciplina_descriptor.py tests/integration/competencia/test_generar_grilla_integration.py tests/integration/competencia/test_flujo_e2e_inc21.py tests/integration/e2e/test_flujo_torneo_competencia.py -q
./.venv/bin/pytest tests/features/steps/disciplina_descriptor_steps.py tests/features/steps/api_disciplina_aware_steps.py tests/features/steps/ejecucion_multi_andarivel_steps.py -q
```

---

## Trazabilidad

| Elemento | Referencia |
|----------|------------|
| Discrepancia origen | DISC-04 |
| Análisis | HITO-17 · `.work/analisis-discrepancias-dataset-reales.md` |
| Política corregida | P-01 / P-05 |
| Invariante aplicada | Menor AP primero en todas las disciplinas, incluida STA |
