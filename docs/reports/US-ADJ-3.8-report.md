# Reporte de Implementacion — US-ADJ-3.8
## Auditoria y correccion cross-BC en `ResultadosCompetenciaAdapter`

**Fecha:** 2026-04-03
**Branch:** `feature/sp-adj-03-ajuste-sp3`
**Sprint:** SP-ADJ-03 — Ajuste Tecnico Post-SP3

---

## Resumen

Se elimino el acoplamiento directo del BC `resultados` con el aggregate
`Performance` del BC `competencia`.

`ResultadosCompetenciaAdapter` ahora lee eventos crudos del stream
`performance-{competencia_id}-*` y traduce esos eventos a `ResultadoFinal`
sin reconstituir el modelo interno del upstream.

---

## Artefactos Producidos

| Artefacto | Tipo | Descripcion |
|-----------|------|-------------|
| `src/resultados/infrastructure/repositories/resultados_competencia_adapter.py` | Infraestructura | ACL refactorizado para leer eventos crudos |
| `docs/plans/sp-adj-03/US-ADJ-3.8-plan.md` | Plan | Plan tecnico de la US |
| `docs/reports/US-ADJ-3.8-report.md` | Reporte | Cierre documental de la US |
| `quality/reports/codeguard/US-ADJ-3.8-quality.txt` | Quality gate | Evidencia de CodeGuard del adapter |

---

## Decisiones Tecnicas

### Traduccion desde eventos crudos

Se reemplazo:

- import de `Performance`
- import de `EstadoPerformance`
- reconstitucion cross-BC del aggregate

Por una traduccion directa de eventos del stream, interpretando solo los datos
necesarios para `ResultadoFinal`:

- `APRegistrado`
- `ResultadoRegistrado`
- `TarjetaAsignada`
- `DNSRegistrado`

### Refactor de complejidad

La primera version del cambio dejo un helper con complejidad elevada. Se
separo en funciones privadas mas chicas para que `CodeGuard` quede sin
advertencias.

---

## Invariantes Verificadas

| ID | Descripcion | Estado |
|----|-------------|--------|
| `INV-ADJ-3.8-1` | `resultados_competencia_adapter.py` no importa `competencia.domain` | ✅ |
| `INV-ADJ-3.8-2` | `get_resultados_finales` mantiene el contrato observable | ✅ |
| `INV-ADJ-3.8-3` | los tests existentes de `resultados` pasan sin cambios | ✅ |

---

## Validacion Ejecutada

| Suite / Gate | Resultado |
|-------------|-----------|
| `tests/unit/resultados/application/test_calcular_ranking_handler.py` | ✅ 7/7 |
| `tests/integration/resultados/test_calcular_ranking_integration.py` | ✅ 6/6 |
| `py_compile` del adapter | ✅ |
| `grep "from competencia.domain"` sobre el adapter | ✅ 0 matches |
| `git diff --check` | ✅ |
| `CodeGuard` sobre el adapter | ✅ 0 errores, 0 warnings |

Comandos ejecutados:

```bash
./.venv/bin/pytest tests/unit/resultados/application/test_calcular_ranking_handler.py -q
./.venv/bin/pytest tests/integration/resultados/test_calcular_ranking_integration.py -q
./.venv/bin/python -m py_compile src/resultados/infrastructure/repositories/resultados_competencia_adapter.py
grep "from competencia.domain" src/resultados/infrastructure/repositories/resultados_competencia_adapter.py
git diff --check
./.venv/bin/codeguard src/resultados/infrastructure/repositories/resultados_competencia_adapter.py
```

---

## Resultado

`US-ADJ-3.8` queda cerrada funcionalmente: el ACL de `resultados` ya no depende
del modelo interno de `competencia` y el calculo de ranking mantiene el mismo
comportamiento observable.
