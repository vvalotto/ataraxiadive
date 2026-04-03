# Reporte de Implementación — US-ADJ-4.6
## Value Object `TiempoAP`

**Sprint:** SP-ADJ-04
**Branch:** `feature/US-ADJ-4.6-tiempo-ap`
**Fecha:** 2026-04-03

---

## Resumen

Se agregó `TiempoAP` en `shared/domain/value_objects` para encapsular el parsing
de APs expresados en `MM:SS` o `HH:MM:SS` hacia segundos (`Decimal`).

La conversión deja de depender de scripts o frontend y pasa a ser parte explícita
del modelo compartido del dominio.

---

## Cambios implementados

### Código
| Archivo | Cambio |
|---------|--------|
| `src/shared/domain/value_objects/tiempo_ap.py` | Nuevo VO con `desde_mmss()` y `desde_segundos()` |
| `src/shared/domain/value_objects/__init__.py` | Exporta `TiempoAP` |

### Tests
| Archivo | Cambio |
|---------|--------|
| `tests/unit/shared/domain/test_tiempo_ap.py` | Casos válidos e inválidos para `MM:SS`, `HH:MM:SS` y segundos directos |
| `tests/features/US-ADJ-4.6-tiempo-ap.feature` | Escenarios BDD del parsing |
| `tests/features/steps/tiempo_ap_steps.py` | Steps de validación BDD |

### Documentación
| Archivo | Cambio |
|---------|--------|
| `docs/design/domain-model.md` | `TiempoAP` agregado a los VOs compartidos |
| `docs/plans/sp-adj-04/PLAN-SP-ADJ-04.md` | `US-ADJ-4.6` marcada como implementada |

---

## Resultados de calidad

| Gate | Resultado |
|------|-----------|
| Pytest focalizado + BDD `TiempoAP` | ✅ 18/18 |
| CodeGuard componente impactado | ✅ 0 errores, 0 advertencias |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/shared/domain/test_tiempo_ap.py tests/features/steps/tiempo_ap_steps.py -q
./.venv/bin/codeguard src/shared/domain/value_objects
```

---

## Notas

- Se usó `ValueError` con mensajes claros (`FormatoTiempoInvalido`, `ValorTiempoInvalido`) para seguir el criterio pragmático del repo y evitar introducir una jerarquía nueva de excepciones sólo para esta US.
- Esta US no reabre la semántica de `SPE`; el VO es parser compartido, no cambia cómo `Disciplina` clasifica tiempo/distancia hoy.
