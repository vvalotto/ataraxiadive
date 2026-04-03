# Plan de Implementación — US-ADJ-4.6
## Value Object `TiempoAP`

**Branch:** `feature/US-ADJ-4.6-tiempo-ap`
**Sprint:** SP-ADJ-04

---

## Cambios identificados

### src/ (impacto bajo)
| Archivo | Cambio |
|---------|--------|
| `src/shared/domain/value_objects/tiempo_ap.py` | Crear nuevo VO con `desde_mmss()` y `desde_segundos()` |
| `src/shared/domain/value_objects/__init__.py` | Exportar `TiempoAP` |
| `src/shared/domain/value_objects/disciplina.py` | Verificar si hace falta referencia cruzada en docstring de disciplinas de tiempo |

### tests/ (impacto bajo)
| Archivo | Cambio |
|---------|--------|
| `tests/unit/shared/domain/test_tiempo_ap.py` | Casos válidos `MM:SS`, `HH:MM:SS`, constructor directo y rechazos |
| `tests/features/steps/tiempo_ap_steps.py` | BDD del parsing si se decide cubrir la spec con feature |
| `tests/features/US-ADJ-4.6-tiempo-ap.feature` | Escenarios de parseo y validación |

### docs/ (mínimas de la US)
| Archivo | Cambio |
|---------|--------|
| `docs/design/domain-model.md` | Agregar `TiempoAP` en Value Objects compartidos |
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | Marcar progreso cuando la US cierre |
| `docs/reports/US-ADJ-4.6-report.md` | Evidencia de implementación |

---

## Tareas de implementación

1. **[T1]** Crear `TiempoAP` en `shared/domain/value_objects/tiempo_ap.py`
2. **[T2]** Implementar parsing `MM:SS` y `HH:MM:SS` a `Decimal` segundos
3. **[T3]** Validar formato y valor positivo con mensajes claros de error
4. **[T4]** Exportar el VO y alinear documentación mínima de dominio
5. **[T5]** Agregar cobertura unitaria y BDD de la spec

---

## Validación pipeline

1. Ejecutar `pytest` focalizado sobre `tests/unit/shared/domain/test_tiempo_ap.py` y BDD de `TiempoAP`
2. Ejecutar `CodeGuard` sobre `src/shared/domain/value_objects`
3. Crear reporte de implementación
4. Actualizar tracking y cerrar la US

---

## Riesgos

- El proyecto no tiene hoy una jerarquía clara de excepciones de dominio compartidas en `shared/domain`; conviene evitar sobre-diseñar y usar `ValueError` con mensajes claros si no aparece un patrón más fuerte.
- `Disciplina.es_tiempo()` hoy sólo reconoce `STA`; la spec menciona `SPE`, pero el modelo vigente sigue tratando `SPE` como distancia. Esta US no debería reabrir esa decisión.
- Hay que evitar mezclar este VO con el `AP` de Competencia: `TiempoAP` es parser/normalizador de entrada, no reemplazo del VO existente.

---

## Notas

- Esta US es intencionalmente acotada y no debería tocar `competencia/` ni `resultados/`.
- Los tests pertenecen a la validación del pipeline, no a las tareas de implementación.
