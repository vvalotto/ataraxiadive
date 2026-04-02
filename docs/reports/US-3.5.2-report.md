# Reporte de Implementación — US-3.5.2
## Política P-09 — todas las disciplinas finalizadas

**Fecha:** 2026-04-02
**Branch:** `feature/US-3.5.2-politica-p09`
**Sprint:** SP3 — El Torneo
**Incremento:** INC-3.5

---

## Resumen

Implementación de la política `P-09` en el composition root para disparar
`CalcularOverall` cuando la competencia finalizada completa todas las
disciplinas de un torneo.

La política mantiene `P-08` sin cambios funcionales: cada
`CompetenciaFinalizada` sigue disparando el cálculo del ranking de disciplina, y
solo si existe `torneo_id` y todas las competencias del torneo están
finalizadas se calcula el overall.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `src/app.py` | Integración | Extensión de callback `P-08 + P-09` con verificación de torneo completo |
| `src/competencia/application/_p08_finalizacion.py` | Helper aplicación | Reenvío de `torneo_id` al callback y compatibilidad backward con callbacks de 2 args |
| `src/competencia/application/commands/asignar_tarjeta.py` | Aplicación | Ajuste del tipo del callback |
| `src/competencia/application/commands/registrar_dns.py` | Aplicación | Ajuste del tipo del callback |
| `tests/unit/test_app_p09.py` | Unit | Casos torneo completo, incompleto y standalone |
| `tests/integration/test_p09_callback_integration.py` | Integración | Flujo callback real hasta persistencia de `ranking-overall-{torneo_id}` |
| `tests/features/US-3.5.2-politica-p09.feature` | BDD | Escenarios de la política `P-09` |
| `tests/features/steps/politica_p09_steps.py` | Steps BDD | Ejecución observable de `P-08 + P-09` |
| `quality/reports/codeguard/US-3.5.2-quality.txt` | Quality gate | Evidencia de validaciones ejecutadas |
| `docs/plans/sp3/US-3.5.2-plan.md` | Plan | Plan técnico aprobado para la US |

---

## Decisiones Técnicas

### Ubicación de la política

`P-09` se implementó en `src/app.py`, junto a `P-08`, preservando el
composition root como punto de orquestación entre `competencia`, `torneo` y
`resultados`.

### Fuente de verdad de disciplinas

La lista de disciplinas del torneo se obtiene desde `SQLiteTorneoRepository`.
La condición "todas finalizadas" se verifica escaneando competencias del torneo
en el event store de `competencia`.

### Backward compatibility

El callback de finalización ahora puede recibir `torneo_id`, pero
`trigger_finalizacion_si_corresponde(...)` mantiene compatibilidad con
callbacks existentes de dos argumentos mediante inspección de firma.

---

## Tests

| Suite | Tests | Resultado |
|-------|-------|-----------|
| Unitarios focalizados | 5 | ✅ 5/5 |
| Integración focalizada | 2 | ✅ 2/2 |
| BDD focalizado + regresión P-08 | 10 | ✅ 10/10 |
| **Total ejecutado** | **17** | ✅ **17/17** |

Comandos validados:

```bash
./.venv/bin/pytest tests/unit/test_app_p09.py tests/unit/resultados/application/test_calcular_overall_handler.py -q
./.venv/bin/pytest tests/integration/test_p09_callback_integration.py tests/integration/resultados/test_calcular_overall_integration.py -q
./.venv/bin/pytest tests/features/steps/politica_p09_steps.py tests/features/steps/competencia_finalizada_steps.py -q
```

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| `py_compile` sobre código y tests nuevos | ✅ |
| `git diff --check` | ✅ |
| Pytest focalizado | ✅ 17/17 |
| CodeGuard sobre componentes impactados | ✅ 0 errores, 0 warnings |

**Artefacto:** `quality/reports/codeguard/US-3.5.2-quality.txt`

---

## Invariantes Cubiertos

| ID | Descripción | Estado |
|----|-------------|--------|
| INV-P09-01 | `P-09` solo se activa si `torneo_id` está presente | ✅ |
| INV-P09-02 | El overall solo se calcula si todas las disciplinas finalizaron | ✅ |
| INV-P09-03 | `P-08` se preserva sin cambios funcionales | ✅ |
| INV-P09-04 | Un torneo de una sola disciplina dispara overall al finalizarla | ✅ |
| INV-P09-05 | La ruta cubierta evita duplicación funcional del overall ya calculado | ✅ |

---

## Pendiente para la siguiente US

- `US-3.5.3`: exponer `GET /resultados/{torneo_id}/overall`
