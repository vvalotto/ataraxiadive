# Reporte US-ADJ-1.1 — Domain Cleanup

**US:** US-ADJ-1.1
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Fecha:** 2026-03-28
**Issues resueltos:** ADJ-03 · ADJ-06 · ADJ-08
**BDD:** omitido (refactor técnico puro)

---

## Resumen de cambios

| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/aggregates/performance.py` | `@property ot_programado` + rename `registrarAP` → `registrar_ap` |
| `src/competencia/infrastructure/repositories/andariveles_activos_adapter.py` | Usa `perf.ot_programado`, eliminado `# noqa: SLF001` |
| `src/competencia/application/commands/registrar_ap.py` | Llamada actualizada a `registrar_ap` |
| `src/competencia/domain/aggregates/competencia.py` | `_event_handlers` inicializado en `__init__` (OCP pattern) |
| `tests/unit/competencia/domain/test_performance.py` | 31 referencias actualizadas a `registrar_ap` |

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Tests (481/481) | ✅ passed |
| Pylint | ✅ 9.78/10 |
| Encapsulación (`_ot_programado`) | ✅ sin accesos directos desde infra |
| `noqa: SLF001` | ✅ eliminado |
| snake_case consistente | ✅ `registrar_ap` en todo el codebase src/ + tests/ |

---

## Tiempo

- Estimado: 40 min
- Real: ~25 min

---

*Generado: 2026-03-28 — Fase 9 /implement-us US-ADJ-1.1*
