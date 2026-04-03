# Plan de Implementación — US-ADJ-4.2
## Corregir orden de grilla STA a ascendente

**Branch:** `feature/US-ADJ-4.2-orden-sta`
**Sprint:** SP-ADJ-04

---

## Cambios identificados

### src/ (1 archivo)
| Archivo | Cambio |
|---------|--------|
| `src/shared/domain/value_objects/disciplina_descriptor.py` | `DisciplinaDescriptor.para(STA)` cambia `orden_ascendente=False` → `True`; actualizar docstring de P-01 |

### tests/ (9 archivos)
| Archivo | Cambio |
|---------|--------|
| `tests/unit/competencia/infrastructure/test_disciplina_descriptor_adapter.py` | STA pasa a esperar `orden_ascendente=True` |
| `tests/unit/competencia/domain/test_disciplina_descriptor.py` | Idem |
| `tests/unit/competencia/domain/test_generar_grilla.py` | Orden STA invertido a menor AP primero |
| `tests/integration/competencia/test_generar_grilla_integration.py` | Validación STA actualizada a ascendente |
| `tests/integration/competencia/test_flujo_e2e_inc21.py` | DoD de Inc 2.1 alineado con STA ascendente |
| `tests/integration/e2e/test_flujo_torneo_competencia.py` | RF-PR-05 alineado con STA ascendente |
| `tests/features/US-2.2.1-disciplina-descriptor.feature` | Descriptor y grilla STA actualizados |
| `tests/features/US-2.2.2-api-disciplina-aware.feature` | Background y orden esperado actualizados |
| `tests/features/steps/api_disciplina_aware_steps.py` | Seed y asserts alineados con el nuevo orden |

### docs/ (6 archivos)
| Archivo | Cambio |
|---------|--------|
| `docs/design/event-storming-competencia.md` | P-01: STA menor AP primero |
| `docs/design/event-storming-big-picture.md` | P-05: STA menor AP primero |
| `docs/specs/sp2/US-2.2.1.md` | Histórica alineada con la política corregida |
| `docs/plans/sp2/US-2.2.1-plan.md` | Histórica alineada |
| `docs/reports/US-2.2.1-report.md` | Histórica alineada |
| `docs/plans/sp3/US-3.3.2-plan.md` | Referencia RF-PR-05 alineada |

---

## Tareas de implementación

1. **[T1]** Corregir `DisciplinaDescriptor.para(STA)` a `orden_ascendente=True`
2. **[T2]** Actualizar tests unitarios e integración que asumen STA descendente
3. **[T3]** Actualizar BDD de descriptor y API disciplina-aware
4. **[T4]** Corregir documentación de diseño y artefactos históricos mínimos
5. **[T5]** Ejecutar pytest focalizado sobre unit, integración y BDD afectados
6. **[T6]** Ejecutar `codeguard src/` y guardar evidencia en el reporte

---

## Notas

- El cambio es deliberadamente correctivo: la implementación previa estaba alineada con una política de dominio mal especificada.
- Se corrigen documentos históricos que todavía funcionaban como fuente de verdad visible del comportamiento.
- El alcance no toca ranking ni overall; solo la política de orden de grilla STA.
