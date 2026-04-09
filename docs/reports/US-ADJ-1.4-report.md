# Reporte US-ADJ-1.4 — Router DIP

**US:** US-ADJ-1.4
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Fecha:** 2026-03-28
**Issues resueltos:** ADJ-04 · ADJ-05
**BDD:** omitido (refactor técnico puro)

---

## Resumen de cambios

| Archivo | Cambio |
|---------|--------|
| `src/competencia/api/router.py` | `EventStoreDep: Annotated[EventStorePort, ...]` (era SQLiteEventStore) |
| `src/competencia/api/router.py` | Eliminados imports de `resultados` + `get_on_finalizada_callback` |
| `src/app.py` | `build_on_finalizada_callback()` — cableado P-08 en el composition root |

## Contexto adicional

`get_on_finalizada_callback` era dead code en el router (no hay endpoints HTTP de performance
aún). El movimiento a `app.py` elimina la violación ADR-006 y lo coloca en el lugar correcto
para cuando se agreguen los endpoints en SP futuro.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Tests (481/481) | ✅ passed |
| Imports `resultados` en router.py | ✅ 0 ocurrencias |
| `EventStoreDep` tipado con puerto | ✅ `EventStorePort` |

---

*Generado: 2026-03-28 — Fase 9 /implement-us US-ADJ-1.4*
