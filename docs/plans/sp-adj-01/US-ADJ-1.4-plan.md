# Plan de Implementación — US-ADJ-1.4

**US:** US-ADJ-1.4 — Router DIP (EventStorePort + mover cross-BC a app.py)
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Estimado:** 20 min
**BDD:** omitido (refactor técnico puro)

---

## Contexto adicional descubierto

`get_on_finalizada_callback` está definida en router.py pero no está conectada a ningún
endpoint HTTP (no hay endpoint asignar-tarjeta en el router aún). Es dead code cross-BC.
El movimiento a app.py la coloca en el composition root listo para cuando se agreguen
los endpoints de performance en SP futuro.

## Tareas

| ID | Tarea | Archivo | Est. |
|----|-------|---------|------|
| T1 | Cambiar tipo de `get_event_store` y `EventStoreDep` a `EventStorePort` (ADJ-05) | `competencia/api/router.py` | 5 min |
| T2 | Eliminar imports de `resultados` + `get_on_finalizada_callback` de router.py (ADJ-04) | `competencia/api/router.py` | 5 min |
| T3 | Mover función de construcción del callback P-08 a `app.py` (composition root) | `src/app.py` | 5 min |
| T4 | Suite completa — validar 0 fallos | — | 5 min |

---

## Issues resueltos

- **ADJ-05** — `EventStoreDep` tipado como `SQLiteEventStore` → `EventStorePort`
- **ADJ-04** — Router importa de BC `resultados` → cableado movido a composition root `app.py`

---

*Generado: 2026-03-28 — Fase 2 /implement-us US-ADJ-1.4*
