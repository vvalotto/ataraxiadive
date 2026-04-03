# Reporte de Implementacion — US-ADJ-3.3
## Refactorizar `app.py` y extraer constante de event type

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se refactorizo el composition root en `src/app.py` para que la construccion del
callback de finalizacion quede mas legible y con helpers privados alineados a
las politicas P-08 y P-09.

Ademas, `resultados/application/commands/calcular_overall.py` deja de depender
del string magico `"IntervaloOTConfigurado"` y pasa a usar una constante de
modulo.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/app.py` | Composition root | Refactor del callback P-08/P-09 con helpers privados |
| `src/resultados/application/commands/calcular_overall.py` | Application | Extraccion de constante `_EVENTO_INTERVALO_OT` |
| `docs/plans/sp-adj-03/US-ADJ-3.3-plan.md` | Plan | Plan tecnico de la US |
| `docs/reports/US-ADJ-3.3-report.md` | Reporte | Cierre documental de la US |
| `quality/reports/codeguard/US-ADJ-3.3-quality.txt` | Quality gate | Evidencia de CodeGuard de la US |

---

## Decisiones Tecnicas

### Refactor de P-08 y P-09 en `app.py`

`build_on_finalizada_callback()` quedo reducido a ensamblar el flujo principal:

- construir `ranking_store`
- delegar P-08 a `_calcular_ranking_por_finalizacion()`
- delegar P-09 a `_calcular_overall_si_corresponde()`

Los helpers `_verificar_todas_disciplinas_finalizadas()` y
`_obtener_disciplinas_torneo()` se mantienen en el mismo modulo, con docstrings
que explicitan su rol dentro de P-09.

### Eliminacion del string magico

Se introdujo `_EVENTO_INTERVALO_OT = "IntervaloOTConfigurado"` en
`calcular_overall.py` y se reutiliza en el filtro de eventos que resuelve el
mapeo torneo -> competencia.

No se movio la constante a `shared`, porque la US busca eliminar el literal
hardcodeado sin agregar acoplamiento extra.

---

## Invariantes Verificadas

| ID | Descripcion | Estado |
|----|-------------|--------|
| `INV-ADJ-3.3-1` | P-08 y P-09 mantienen el mismo comportamiento observable | ✅ |
| `INV-ADJ-3.3-2` | Los tests existentes pasan sin cambios | ✅ |
| `INV-ADJ-3.3-3` | `app.py` no incorpora imports nuevos | ✅ |

---

## Validacion Ejecutada

| Suite / Gate | Resultado |
|-------------|-----------|
| `tests/unit/test_app_p09.py` | ✅ |
| `tests/integration/test_p09_callback_integration.py` | ✅ |
| `tests/unit/resultados/application/test_calcular_overall_handler.py` | ✅ |
| `tests/integration/resultados/test_calcular_overall_integration.py` | ✅ |
| `py_compile` de archivos impactados | ✅ |
| `git diff --check` | ✅ |
| `CodeGuard` sobre `app.py` y `calcular_overall.py` | ✅ 0 errores, 0 warnings |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/test_app_p09.py tests/integration/test_p09_callback_integration.py tests/unit/resultados/application/test_calcular_overall_handler.py tests/integration/resultados/test_calcular_overall_integration.py -q
./.venv/bin/python -m py_compile src/app.py src/resultados/application/commands/calcular_overall.py
git diff --check
./.venv/bin/codeguard src/app.py src/resultados/application/commands/calcular_overall.py
```

Resultado consolidado:

- `7 passed` en la regresion focalizada
- `CodeGuard` sin errores ni advertencias
- sin activos BDD nuevos generados para esta US

---

## Resultado

`US-ADJ-3.3` queda cerrada funcionalmente: el composition root quedo mas claro,
la logica de P-09 es mas legible y `calcular_overall.py` ya no depende de un
literal magico para identificar `IntervaloOTConfigurado`.
