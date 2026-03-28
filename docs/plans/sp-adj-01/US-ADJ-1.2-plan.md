# Plan de Implementación — US-ADJ-1.2

**US:** US-ADJ-1.2 — Refactor ajustar_grilla (extraer helpers OT y swap)
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Estimado:** 30 min
**BDD:** omitido (refactor técnico puro — sin cambio de comportamiento observable)

---

## Tareas

| ID | Tarea | Archivo | Est. |
|----|-------|---------|------|
| T1 | Extraer `_recalcular_ots(grilla, ot_inicio, intervalo)` como función de módulo | `src/competencia/domain/aggregates/competencia.py` | 10 min |
| T2 | Extraer `_aplicar_swap_posicion(grilla_mutable, perf_id, pos_nueva, cambios_payload)` como función de módulo | `src/competencia/domain/aggregates/competencia.py` | 10 min |
| T3 | Refactorizar `ajustar_grilla` para usar los dos helpers | `src/competencia/domain/aggregates/competencia.py` | 5 min |
| T4 | Refactorizar `_apply_grilla_de_salida_ajustada` para usar `_recalcular_ots` | `src/competencia/domain/aggregates/competencia.py` | 5 min |
| T5 | Correr suite completa — validar 0 fallos | — | 5 min |

---

## Issues resueltos

- **ADJ-01** — `ajustar_grilla` 127 líneas con lógica duplicada → ≤ 60 líneas, helpers de módulo

## Invariante

Los tests existentes de `ajustar_grilla` no se modifican — son el contrato de comportamiento.

---

*Generado: 2026-03-28 — Fase 2 /implement-us US-ADJ-1.2*
