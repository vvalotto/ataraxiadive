# PLAN-SP-ADJ-01 — Sprint de Ajuste Técnico Post-SP2

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-01 |
| **Contexto** | Deuda técnica identificada en revisión de cierre SP2 |
| **Baseline objetivo** | BL-ADJ-001 |
| **Branch base** | `develop` |
| **Fecha inicio** | 2026-03-28 |

---

## Objetivo

Resolver los 8 issues de refactoring identificados en la revisión de calidad de cierre SP2,
agrupados en 5 US-IEDD de ajuste técnico. El código debe quedar con:
- Cero regresiones en los 481 tests existentes
- DesignReviewer sin nuevos CRITICAL respecto a BL-002
- Issues ADJ-01 a ADJ-08 resueltos y trazados

---

## US-IEDD del Sprint

| US | Issues | Descripción | Capa | Prioridad |
|---|---|---|---|---|
| US-ADJ-1.1 | ADJ-03, ADJ-06, ADJ-08 | Domain cleanup: `ot_programado` property + OCP Competencia + snake_case | `domain/` | Media |
| US-ADJ-1.2 | ADJ-01 | Refactor `ajustar_grilla`: extraer helpers OT y swap | `domain/` | Alta |
| US-ADJ-1.3 | ADJ-02 | Consolidar `_build_stream_id` en `_stream_ids.py` | `application/` | Alta |
| US-ADJ-1.4 | ADJ-04, ADJ-05 | Router DIP: `EventStorePort` + mover cross-BC a `app.py` | `api/` | Alta |
| US-ADJ-1.5 | ADJ-07 | Router SRP: separar `schemas.py` + `dependencies.py` | `api/` | Media |

**Orden de implementación recomendado:** US-ADJ-1.1 → US-ADJ-1.2 → US-ADJ-1.3 → US-ADJ-1.4 → US-ADJ-1.5

Rationale: dominio primero (más estable, sin dependencias externas), luego aplicación, luego API.

---

## DoD del Sprint

- [ ] Los 5 US-IEDD implementadas con `/implement-us`
- [ ] 481+ tests pasando (cero regresiones)
- [ ] DesignReviewer: sin nuevos CRITICAL vs BL-002
- [ ] `ajustar_grilla` ≤ 60 líneas
- [ ] `_build_stream_id` no duplicado (1 sola definición por tipo de stream)
- [ ] `router.py` sin imports de `resultados`
- [ ] `EventStoreDep` tipado como `EventStorePort`
- [ ] BL-ADJ-001.md registrada con retrospectiva

---

## Branching

```
develop
  └── refactor/US-ADJ-1.1-domain-cleanup
  └── refactor/US-ADJ-1.2-ajustar-grilla
  └── refactor/US-ADJ-1.3-stream-ids
  └── refactor/US-ADJ-1.4-router-dip
  └── refactor/US-ADJ-1.5-router-srp
```

---

## Archivos de especificación

- `docs/specs/sp-adj-01/US-ADJ-1.1.md`
- `docs/specs/sp-adj-01/US-ADJ-1.2.md`
- `docs/specs/sp-adj-01/US-ADJ-1.3.md`
- `docs/specs/sp-adj-01/US-ADJ-1.4.md`
- `docs/specs/sp-adj-01/US-ADJ-1.5.md`

---

## Referencias

- Revisión de calidad: `.work/revision-sp2/` (01 al 07)
- Decisión metodológica: `docs/contexto/HITO-13-SP-ADJ-DEUDA-TECNICA-COMO-ETAPA-FORMAL.md`
- Issues software_limpio: `vvalotto/software_limpio#45`
