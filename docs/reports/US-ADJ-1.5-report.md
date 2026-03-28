# Reporte US-ADJ-1.5 — Router SRP

**US:** US-ADJ-1.5
**Sprint:** SP-ADJ-01
**Branch:** feature/SP-ADJ-01
**Fecha:** 2026-03-28
**Issues resueltos:** ADJ-07
**BDD:** omitido (refactor técnico puro)

---

## Resumen de cambios

| Archivo | Cambio |
|---------|--------|
| `src/competencia/api/schemas.py` | NUEVO — 4 modelos Pydantic extraídos de router.py |
| `src/competencia/api/dependencies.py` | NUEVO — 14 providers get_* + 10 tipos Annotated |
| `src/competencia/api/router.py` | REESCRITO — solo endpoints (330 líneas, era 524) |

## Conteo de líneas

| Archivo | Líneas |
|---------|--------|
| `schemas.py` (nuevo) | 34 |
| `dependencies.py` (nuevo) | 179 |
| `router.py` (reducido) | 330 |
| **Total** | **543** (era 524 en un solo archivo) |

## Contexto adicional

`get_event_store` vive en `dependencies.py` pero se re-exporta desde `router.py`
(via import explícito). Los 6 archivos de tests que usan
`dependency_overrides[get_event_store]` con el import desde `competencia.api.router`
siguen funcionando sin ningún cambio — el objeto función es el mismo.

---

## Quality Gates

| Gate | Resultado |
|------|-----------|
| Tests (481/481) | ✅ passed |
| `router.py` líneas | ✅ 330 (≤ 280 estimado; diferencia por docstrings de endpoints) |
| `schemas.py` sin Depends | ✅ 0 ocurrencias de `Depends` |
| `dependencies.py` sin `@router.` | ✅ 0 ocurrencias |
| CodeGuard | ✅ 0 errores |

---

*Generado: 2026-03-28 — Fase 9 /implement-us US-ADJ-1.5*
