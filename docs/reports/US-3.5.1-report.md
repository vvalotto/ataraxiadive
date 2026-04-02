# Reporte de Implementación — US-3.5.1
## RankingOverall — fórmula posicional

**Fecha:** 2026-04-02
**Branch:** `feature/US-3.5.1-overall-posicional`
**Sprint:** SP3 — El Torneo
**Incremento:** INC-3.5

---

## Resumen

Implementación del aggregate `RankingOverall` en el BC `resultados` para calcular
el overall de un torneo a partir de rankings por disciplina, usando fórmula
posicional: menor puntaje total = mejor posición.

La US deja listo el núcleo de dominio y aplicación para que `US-3.5.2` dispare
el cálculo automáticamente y `US-3.5.3` lo exponga por API.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripción |
|-----------|------|-------------|
| `src/resultados/domain/value_objects/entrada_overall.py` | VO nuevo | Línea del overall con posición, puntaje y detalle por disciplina |
| `src/resultados/domain/events/ranking_overall_calculado.py` | Evento nuevo | Persistencia del overall calculado |
| `src/resultados/domain/aggregates/ranking_overall.py` | Aggregate nuevo | Cálculo posicional multi-disciplina + reconstitución ES |
| `src/resultados/application/commands/calcular_overall.py` | Command + Handler | Orquesta lectura de competencias/rankings y persistencia del overall |
| `tests/unit/resultados/domain/test_ranking_overall.py` | Unit | Reglas de suma, empates, podio, ausencia y reconstitución |
| `tests/unit/resultados/application/test_calcular_overall_handler.py` | Unit | Persistencia del evento y caso sin rankings fuente |
| `tests/integration/resultados/test_calcular_overall_integration.py` | Integración | Event stores reales de Competencia + Resultados |
| `tests/features/US-3.5.1-ranking-overall.feature` | BDD | 5 escenarios Gherkin |
| `tests/features/steps/calcular_overall_steps.py` | Steps BDD | Siembra de competencias/rankings y validación overall |
| `docs/plans/sp3/US-3.5.1-plan.md` | Plan | Plan técnico de la US |
| `quality/reports/codeguard/US-3.5.1-quality.txt` | Quality gate | Salida de CodeGuard sobre `src/resultados` |

---

## Decisiones Técnicas

### Fuente de datos del overall

El overall no se calcula desde performances crudas, sino desde rankings de
disciplina ya calculados en el BC `resultados`. El handler usa:

- `competencia_store` para mapear `torneo_id -> competencia/disciplina`
- `ranking_store` para leer los streams `ranking-{competencia_id}-{disciplina}`

Esto deja a `US-3.5.2` la responsabilidad de decidir cuándo disparar el cálculo.

### Penalización por ausencia

La ausencia en una disciplina ejecutada se resuelve con `peor_posicion + 1`.
Si una disciplina todavía no tiene ranking calculado, se excluye completamente
del overall en esta US.

### Empates y podio

- empate en puntaje total -> misma posición
- la posición siguiente se omite
- `en_podio = True` si `posicion <= 3`

---

## Tests

| Suite | Tests | Resultado |
|-------|-------|-----------|
| Unitarios dominio + aplicación | 7 | ✅ 7/7 |
| Integración | 1 | ✅ 1/1 |
| BDD | 5 | ✅ 5/5 |
| **Total nuevo** | **13** | ✅ **13/13** |

**Regresiones observadas en la suite focalizada:** 0

Comando validado:

```bash
./.venv/bin/pytest \
  tests/unit/resultados/domain/test_ranking_overall.py \
  tests/unit/resultados/application/test_calcular_overall_handler.py \
  tests/integration/resultados/test_calcular_overall_integration.py \
  tests/features/steps/calcular_overall_steps.py
```

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Black | ✅ Formateado |
| Pytest focalizado | ✅ 13/13 |
| CodeGuard sobre `src/resultados` | ✅ sin errores críticos para esta US |

**Artefacto:** `quality/reports/codeguard/US-3.5.1-quality.txt`

Observación: durante la sesión hubo inestabilidad del CLI de tracking y del modo
de invocación más fino de CodeGuard; el barrido útil que se preserva es el
ejecutado sobre `src/resultados`.

---

## Invariantes Cubiertos

| ID | Descripción | Estado |
|----|-------------|--------|
| INV-OV-01 | Ausente en disciplina ejecutada -> peor posición + 1 | ✅ |
| INV-OV-02 | Empates en puntaje -> misma posición | ✅ |
| INV-OV-03 | Solo atletas presentes en al menos una disciplina | ✅ |
| INV-OV-04 | `en_podio` si `posicion <= 3` | ✅ |
| INV-OV-05 | Sin rankings calculados -> overall vacío | ✅ |

---

## Pendiente para la siguiente US

- `US-3.5.2`: política P-09 en `src/app.py` para disparar `CalcularOverall`
- `US-3.5.3`: endpoint `GET /resultados/{torneo_id}/overall`

---

## Nota Operativa

El CLI de tracking dejó el tracker en estado inconsistente durante la ejecución.
Debe corregirse al cierre para que `US-3.5.1` no quede como tracking activo.
