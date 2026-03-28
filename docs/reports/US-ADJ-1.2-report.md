# Reporte US-ADJ-1.2 — Refactor ajustar_grilla

**US:** US-ADJ-1.2
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Fecha:** 2026-03-28
**Issues resueltos:** ADJ-01
**BDD:** omitido (refactor técnico puro)

---

## Resumen de cambios

| Archivo | Cambio |
|---------|--------|
| `src/competencia/domain/aggregates/competencia.py` | Extraído `_recalcular_ots` + `_aplicar_swap_posicion` como funciones de módulo |
| `src/competencia/domain/aggregates/competencia.py` | `ajustar_grilla` usa los helpers — 127 → ~55 líneas |
| `src/competencia/domain/aggregates/competencia.py` | `_apply_grilla_de_salida_ajustada` usa `_recalcular_ots` |
| `src/competencia/domain/aggregates/competencia.py` | `generar_grilla` usa `_recalcular_ots` — triplicación eliminada |

**Resultado:** `timedelta(minutes=...` aparece en un único lugar: `_recalcular_ots`.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Tests (481/481) | ✅ passed |
| Pylint | ✅ 9.82/10 |
| Triplicación OT eliminada | ✅ timedelta solo en `_recalcular_ots` |

---

## Tiempo

- Estimado: 30 min
- Real: ~20 min

---

*Generado: 2026-03-28 — Fase 9 /implement-us US-ADJ-1.2*
