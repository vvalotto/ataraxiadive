# Reporte de Implementacion: US-6.4.2

## Resumen Ejecutivo

- **Historia de Usuario:** US-6.4.2 - Materializar proyeccion `competencias_por_torneo` en CalcularOverallHandler
- **Incremento:** INC-6.4 - Deuda Tecnica Sistema
- **Producto:** resultados + competencia
- **Puntos estimados:** 5
- **Tiempo estimado:** 2h 00min
- **Tiempo registrado:** 9 min
- **Estado:** Completado
- **Fecha completado:** 2026-05-09

## Componentes Implementados

- `src/resultados/application/commands/calcular_overall.py`
  - `CalcularOverallHandler` ahora recibe `CompetenciasPorTorneoPort`.
  - Se elimino `_mapear_competencias_por_torneo()` basado en event store.
  - El handler consulta `listar_por_torneo(torneo_id)` y filtra por disciplinas pedidas.
  - Si no hay competencias materializadas, retorna `[]` sin persistir eventos.
- `src/app.py`
  - P-09 inyecta `SQLiteCompetenciasPorTorneo` al calcular overall.
- Tests y BDD
  - Unitarios actualizados para verificar que no se escanea el event store de competencia.
  - Integracion actualizada con `SQLiteCompetenciasPorTorneo` real.
  - BDD de overall extendido con escenarios de US-6.4.2.
- `tests/uat/sp3/seed_sp3.py`
  - Seed UAT actualizado a la nueva firma del handler.

## Metricas de Calidad

| Gate | Resultado | Estado |
|------|-----------|--------|
| Unitarios resultados + P-09 | 77 passed | OK |
| Integracion overall + P-09 | 3 passed | OK |
| BDD overall | 8 passed | OK |
| Suite acotada combinada | 85 passed | OK |
| CodeGuard handler | 0 errores, 0 advertencias | OK |
| DesignReviewer resultados | 0 CRITICAL, 40 warnings | OK con warnings preexistentes |

## Validacion Ejecutada

```bash
.venv/bin/python -m pytest tests/unit/resultados/application/test_calcular_overall_handler.py -q
# 3 passed

.venv/bin/python -m pytest tests/unit/resultados/ tests/unit/test_app_p09.py -q
# 77 passed

.venv/bin/python -m pytest tests/integration/resultados/test_calcular_overall_integration.py tests/integration/test_p09_callback_integration.py -q
# 3 passed

.venv/bin/python -m pytest tests/features/steps/calcular_overall_steps.py -q
# 8 passed

.venv/bin/python -m pytest tests/unit/resultados/ tests/integration/resultados/test_calcular_overall_integration.py tests/integration/test_p09_callback_integration.py tests/features/steps/calcular_overall_steps.py -q
# 85 passed

.venv/bin/codeguard src/resultados/application/commands/calcular_overall.py
# 0 errores; 0 advertencias

.venv/bin/designreviewer src/resultados/ --config pyproject.toml
# 0 CRITICAL; 40 warnings
```

## Criterios de Aceptacion

- [x] `CalcularOverallHandler` no llama a `load_all_streams_with_prefix`.
- [x] `CalcularOverallHandler` llama a `competencias_por_torneo.listar_por_torneo(torneo_id)`.
- [x] El resultado del overall se preserva para rankings calculados.
- [x] Torneo sin competencias materializadas retorna `[]` sin error.
- [x] P-09 en `app.py` usa la proyeccion existente.

## Riesgos y Observaciones

- `DesignReviewer` no reporto CRITICAL. Los 40 warnings pertenecen al estado actual del BC
  `resultados` y no bloquean esta US.
- La capa application de `resultados` importa un port del domain de `competencia`. Es una
  dependencia cross-BC por port, no por infraestructura, y reemplaza un acoplamiento mas costoso
  al event store completo.
- La correcta ejecucion de P-09 depende de que la proyeccion se encuentre poblada antes del
  calculo overall. Ese flujo ya existe en `app.py`.

## Archivos Creados o Modificados

- `CHANGELOG.md`
- `docs/plans/sp6/US-6.4.2-plan.md`
- `docs/reports/US-6.4.2-report.md`
- `src/app.py`
- `src/resultados/application/commands/calcular_overall.py`
- `tests/features/US-6.4.2-proyeccion-overall.feature`
- `tests/features/steps/calcular_overall_steps.py`
- `tests/integration/resultados/test_calcular_overall_integration.py`
- `tests/uat/sp3/seed_sp3.py`
- `tests/unit/resultados/application/test_calcular_overall_handler.py`

## Proximo Paso

- Continuar con US-6.4.3 cuando se apruebe iniciar la siguiente US del incremento.
