# Reporte de Implementación — US-4.6.2
## Hash SHA-256 al cierre de disciplina

**Sprint:** SP4 — La Plataforma  
**Incremento:** INC-4.6  
**Branch:** `feature/US-4.6.2-hash-cierre`  
**Fecha:** 2026-04-16

---

## Resumen

Se implementó la segunda US de `INC-4.6` en el BC `competencia`: al cerrar una
disciplina se calcula un `hash_sha256` determinista sobre la secuencia canónica
de eventos de sus performances y se persiste dentro de `CompetenciaFinalizada`.

La solución reutiliza el event store existente como fuente oficial de eventos,
agrega un servicio de dominio puro para el cálculo del digest y ejecuta el hash
antes de persistir el cierre automático de la política `P-08`.

---

## Cambios implementados

### Código

| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/services/calculador_hash_competencia.py` | Nuevo servicio `CalculadorHashCompetencia` con serialización JSON canónica y SHA-256 del conjunto vacío |
| `src/competencia/domain/events/competencia_finalizada.py` | Extensión del evento con `hash_sha256`, manteniendo backward compatibility en `from_payload()` |
| `src/competencia/domain/aggregates/competencia.py` | `finalizar()` ahora recibe y persiste el hash calculado |
| `src/competencia/application/_p08_finalizacion.py` | `P-08` carga eventos de performance por competencia, filtra la disciplina, calcula el hash y recién después emite `CompetenciaFinalizada` |

### Tests

| Archivo | Cobertura |
|---------|-----------|
| `tests/unit/competencia/domain/test_calculador_hash_competencia.py` | determinismo, cambio ante alteración de payload y hash del conjunto vacío |
| `tests/unit/competencia/domain/test_competencia_finalizar.py` | persistencia de `hash_sha256`, reconstitución y cierre sin performances |
| `tests/unit/competencia/application/test_p08_finalizacion.py` | `P-08` persiste `CompetenciaFinalizada` con hash de 64 hex |
| `tests/integration/competencia/test_competencia_finalizada_integration.py` | payload real con `hash_sha256` al cerrar |
| `tests/unit/test_app_p09.py` y `tests/integration/test_p09_callback_integration.py` | no regresión del callback `P-09` tras extender `CompetenciaFinalizada` |
| `tests/features/steps/competencia_finalizada_steps.py` | adaptación del fixture legacy al nuevo contrato de `finalizar()` |

### Artefactos de proceso

| Archivo | Propósito |
|---------|-----------|
| `tests/features/US-4.6.2-hash-cierre-disciplina.feature` | escenarios BDD de la US |
| `docs/plans/sp4/US-4.6.2-plan.md` | plan aprobado de implementación |
| `docs/reports/US-4.6.2-bdd-waiver.md` | sustitución explícita de automatización BDD por tests unitarios + integración |
| `docs/traceability/matrix.md` | registro de `US-4.6.2` dentro de `INC-4.6` |
| `quality/reports/codeguard/US-4.6.2-codeguard.json` | evidencia del quality gate focalizado |

---

## Decisiones de diseño

### 1. Hash sobre eventos de performance, no sobre snapshots

El digest se calcula directamente desde el event store usando la misma fuente de
verdad que expone `US-4.6.1`. No se introduce snapshot ni tabla auxiliar.

Esto mantiene alineación con ADR-001 y preserva la trazabilidad completa del
cierre.

### 2. Cálculo previo al cierre para evitar autorreferencia

El hash se obtiene antes de emitir `CompetenciaFinalizada`, de modo que el propio
evento de cierre no contamina el conjunto hasheado.

La política `P-08` quedó como punto único de orquestación de ese orden.

### 3. Compatibilidad hacia atrás del stream existente

`CompetenciaFinalizada.from_payload()` usa `payload.get("hash_sha256")`, por lo
que streams históricos sin ese campo siguen reconstituyéndose correctamente.

---

## Validación ejecutada

### Pytest focalizado

Comandos ejecutados:

```bash
./.venv/bin/pytest \
  tests/unit/competencia/domain/test_calculador_hash_competencia.py \
  tests/unit/competencia/domain/test_competencia_finalizar.py \
  tests/unit/competencia/application/test_p08_finalizacion.py \
  tests/unit/test_app_p09.py

./.venv/bin/pytest \
  tests/integration/competencia/test_competencia_finalizada_integration.py \
  tests/integration/test_p09_callback_integration.py
```

Resultado:

```text
22 passed in 1.47s
5 passed in 1.45s
```

### CodeGuard focalizado

Comando ejecutado:

```bash
./.venv/bin/codeguard \
  src/competencia/domain/services/calculador_hash_competencia.py \
  src/competencia/domain/services/__init__.py \
  src/competencia/domain/events/competencia_finalizada.py \
  src/competencia/domain/aggregates/competencia.py \
  src/competencia/application/_p08_finalizacion.py \
  tests/unit/competencia/domain/test_calculador_hash_competencia.py \
  tests/unit/competencia/domain/test_competencia_finalizar.py \
  tests/unit/competencia/application/test_p08_finalizacion.py \
  tests/integration/competencia/test_competencia_finalizada_integration.py \
  tests/features/steps/competencia_finalizada_steps.py \
  -c pyproject.toml -a pre-commit -t 15 --format json \
  > quality/reports/codeguard/US-4.6.2-codeguard.json
```

Resultado:

```text
0 errors
11 warnings
69 infos
```

Los warnings remanentes provienen del análisis genérico sobre `assert` en tests;
no se detectaron issues de código productivo.

---

## Estado respecto de la spec

### Cumplido

- `CompetenciaFinalizada` persiste `hash_sha256`
- Hash determinista de 64 caracteres hex
- Hash calculado antes del cierre
- Cobertura del conjunto vacío con el SHA-256 conocido
- Sin regresión del callback `P-09`

### Diferencia menor respecto de la redacción original

- La spec nombra `CompetenciaCerrada`, pero el modelo implementado y vigente del
  BC usa `CompetenciaFinalizada`. La US extiende ese evento existente en lugar de
  introducir uno nuevo.

---

## Riesgos y próximos pasos

- El filtro por disciplina depende del formato actual de `stream_id` de
  performance; si ese convenio cambia, el cálculo del hash debe ajustarse en
  `P-08`.
- `US-4.6.3` puede reutilizar directamente el campo `hash_sha256` persistido para
  mostrarlo al organizador sin recalcular nada.
- `US-4.6.4` podrá exportar el valor de hash como metadato de integridad si la
  spec de exportación lo requiere.
