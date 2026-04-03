# Plan de Implementacion — US-ADJ-3.3

## Resumen

Refactorizar el composition root en `src/app.py` para que la politica P-08/P-09
quede ensamblada con helpers de modulo mas claros, y eliminar el string magico
`"IntervaloOTConfigurado"` de `resultados/application/commands/calcular_overall.py`
reemplazandolo por una constante de modulo.

## Objetivo observable

- `build_on_finalizada_callback()` reduce su cuerpo a ensamblar el flujo de P-08
  y P-09
- `_verificar_todas_disciplinas_finalizadas()` y
  `_obtener_disciplinas_torneo()` quedan como helpers de modulo con docstrings
  explicitas sobre su rol en P-09
- `calcular_overall.py` deja de comparar contra el literal
  `"IntervaloOTConfigurado"` y usa `_EVENTO_INTERVALO_OT`

## Alcance

- `src/app.py`
- `src/resultados/application/commands/calcular_overall.py`
- tests unitarios e integracion de P-09 y overall
- artefactos de plan, tracking, calidad y reporte de la US

No incluye:

- nuevos modulos o rediseno del composition root
- cambios funcionales en P-08 o P-09
- activos BDD nuevos

## Decisiones de diseño

1. Mantener todo en los mismos modulos; el ajuste es de legibilidad y OCP, no
   de redistribucion de capas.
2. Extraer helpers privados de `app.py` para separar:
   - construccion de dependencias para ranking
   - decision de disparar overall por torneo
   - lectura de disciplinas del torneo
3. Definir `_EVENTO_INTERVALO_OT = "IntervaloOTConfigurado"` al nivel de modulo
   en `calcular_overall.py`, sin mover la constante a `shared`.

## Implementacion por area

### Composition root

- reducir `build_on_finalizada_callback()` a un flujo corto y legible
- extraer helpers privados con nombres alineados a P-08/P-09
- mantener la misma firma publica del callback
- no introducir imports nuevos en `app.py`

### Resultados

- agregar constante `_EVENTO_INTERVALO_OT`
- reemplazar la comparacion hardcodeada dentro de
  `_mapear_competencias_por_torneo()`

### Validacion

- correr `tests/unit/test_app_p09.py`
- correr `tests/integration/test_p09_callback_integration.py`
- correr `tests/unit/resultados/application/test_calcular_overall_handler.py`
- correr `tests/integration/resultados/test_calcular_overall_integration.py`
- ejecutar `py_compile`, `CodeGuard` y `git diff --check`

## Riesgos a controlar

1. cambiar sin querer el orden o las precondiciones de P-09
2. introducir imports extra en `app.py`, violando la spec
3. romper el mapeo torneo -> competencia en `CalcularOverallHandler`

## Artefactos esperados al cierre

- `src/app.py` mas legible, sin cambiar comportamiento
- `src/resultados/application/commands/calcular_overall.py` sin string magico
- evidencia de quality gates
- `docs/reports/US-ADJ-3.3-report.md`
