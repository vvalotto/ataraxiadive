# Reporte de Implementacion — US-ADJ-3.2
## Extraer `TarjetaAsignacion` como Value Object

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se extrajo `TarjetaAsignacion` como Value Object del dominio de `competencia`
para encapsular las invariantes de asignacion de tarjeta fuera del aggregate
`Performance`.

`Performance.asignar_tarjeta()` mantiene el control del estado y la emision del
evento `TarjetaAsignada`, pero ya no concentra la validacion de
`tipo`/`motivo`/`distancia_blackout`.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/competencia/domain/value_objects/tarjeta_asignacion.py` | Dominio | Nuevo VO para encapsular la asignacion de tarjeta |
| `src/competencia/domain/aggregates/performance.py` | Dominio | Refactor del aggregate para delegar validaciones al VO |
| `docs/plans/sp-adj-03/US-ADJ-3.2-plan.md` | Plan | Plan tecnico de la US |
| `docs/reports/US-ADJ-3.2-report.md` | Reporte | Cierre documental de la US |
| `quality/reports/codeguard/US-ADJ-3.2-quality.txt` | Quality gate | Evidencia de CodeGuard de la US |

---

## Decisiones Tecnicas

### Extraccion del concepto de dominio

`TarjetaAsignacion` concentra dos invariantes:

- motivo obligatorio para tarjetas `Amarilla` y `Roja`
- distancia obligatoria cuando el motivo es `black-out`

Esto hace explicito el concepto y evita seguir propagando tres parametros
relacionados como data clump dentro del dominio.

### Compatibilidad del aggregate

`Performance` conserva:

- validacion del estado `ResultadoRegistrado`
- emision del evento `TarjetaAsignada`
- actualizacion de `_tarjeta` y `_distancia_blackout`

Tambien se mantiene el re-export de `DistanciaBlackoutObligatoria` desde
`performance.py` para no romper imports existentes en tests y consumidores
internos.

---

## Invariantes Verificadas

| ID | Descripcion | Estado |
|----|-------------|--------|
| `INV-ADJ-3.2-1` | `TarjetaAsignacion` valida motivo obligatorio para Amarilla y Roja | ✅ |
| `INV-ADJ-3.2-2` | `TarjetaAsignacion` valida distancia positiva para `black-out` | ✅ |
| `INV-ADJ-3.2-3` | `Performance.asignar_tarjeta()` mantiene el contrato observable | ✅ |

---

## Validacion Ejecutada

| Suite / Gate | Resultado |
|-------------|-----------|
| `tests/unit/competencia/application/test_asignar_tarjeta_handler.py` | ✅ |
| `tests/integration/competencia/test_asignar_tarjeta_integration.py` | ✅ |
| `py_compile` de archivos impactados | ✅ |
| `git diff --check` | ✅ |
| `CodeGuard` sobre aggregate y VO | ✅ 0 errores, 0 warnings |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/competencia/application/test_asignar_tarjeta_handler.py tests/integration/competencia/test_asignar_tarjeta_integration.py -q
./.venv/bin/python -m py_compile src/competencia/domain/aggregates/performance.py src/competencia/domain/value_objects/tarjeta_asignacion.py
git diff --check
./.venv/bin/codeguard src/competencia/domain/aggregates/performance.py src/competencia/domain/value_objects/tarjeta_asignacion.py
```

Resultado consolidado:

- `17 passed` en suites focalizadas
- `CodeGuard` sin errores ni advertencias
- sin activos BDD nuevos generados para esta US

---

## Resultado

`US-ADJ-3.2` queda cerrada funcionalmente: el concepto `TarjetaAsignacion` ya
existe en el Core Domain, `Performance` queda mas simple en la asignacion de
tarjetas y el comportamiento observable se mantiene estable.
