# Plan de Implementación — US-ADJ-1.1

**US:** US-ADJ-1.1 — Domain Cleanup (Performance property + OCP Competencia + snake_case)
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Estimado:** 40 min
**BDD:** omitido (refactor técnico puro — sin cambio de comportamiento observable)

---

## Tareas

| ID | Tarea | Archivo | Est. |
|----|-------|---------|------|
| T1 | Agregar `@property ot_programado` en `Performance` | `src/competencia/domain/aggregates/performance.py` | 5 min |
| T2 | Actualizar `AndarivelesActivosAdapter` — usar propiedad pública, eliminar `# noqa: SLF001` | `src/competencia/infrastructure/repositories/andariveles_activos_adapter.py` | 5 min |
| T3 | Renombrar `registrarAP` → `registrar_ap` en `Performance` | `src/competencia/domain/aggregates/performance.py` | 5 min |
| T4 | Actualizar llamadas en handlers/application | `src/competencia/application/commands/` | 5 min |
| T5 | Actualizar referencias en tests | `tests/unit/competencia/`, `tests/integration/competencia/` | 5 min |
| T6 | Mover `_handlers` dict a `__init__` en `Competencia` (OCP) | `src/competencia/domain/aggregates/competencia.py` | 10 min |
| T7 | Correr suite completa — validar 0 fallos | — | 5 min |

---

## Issues resueltos

- **ADJ-03** — `_ot_programado` accedido desde infraestructura con noqa → property pública
- **ADJ-06** — `_apply_stored` en Competencia recrea dict en cada llamada → mover a `__init__`
- **ADJ-08** — `registrarAP` camelCase → `registrar_ap` snake_case

---

## Capas afectadas

```
competencia/domain/aggregates/      ← T1, T3, T6
competencia/infrastructure/         ← T2
competencia/application/commands/   ← T4
tests/                              ← T5
```

Arquitectura hexagonal respetada — sin cambios cross-BC.

---

*Generado: 2026-03-28 — Fase 2 /implement-us US-ADJ-1.1*
