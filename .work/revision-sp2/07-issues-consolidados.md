# Issues Consolidados — Revisión Cierre SP2
## Candidatos a SP-ADJ-01

**Fecha:** 2026-03-28
**Fuente:** DesignReviewer + análisis manual + revisión SOLID + ArchitectAnalyst

---

## Lista de Issues

| ID | Área | Issue | Severidad | Origen |
|---|---|---|---|---|
| ADJ-01 | `domain/aggregates/competencia.py` | Extraer `_recalcular_ots()` y `_aplicar_swap_posicion()` — `ajustar_grilla` de 127 → ~50 líneas | Alta | LongMethod + duplicación |
| ADJ-02 | `application/commands/` | Consolidar `_build_stream_id` duplicado 11 veces en `_stream_ids.py` | Alta | Duplicación cross-file |
| ADJ-03 | `domain/aggregates/performance.py` | Agregar `@property ot_programado` — eliminar acceso `_ot_programado` privado desde adapter | Media | `# noqa: SLF001` en infra |
| ADJ-04 | `api/router.py` + `app.py` | Mover cableado cross-BC P-08 (`CalcularRankingHandler`) de `router.py` a `app.py` | Alta | DIP + BC boundary |
| ADJ-05 | `api/router.py` | Corregir `EventStoreDep` de `SQLiteEventStore` → `EventStorePort` | Media | DIP |
| ADJ-06 | `domain/aggregates/competencia.py` | Mover dict `_handlers` de `_apply_stored` a `__init__` — consistencia con `Performance` | Baja | OCP inconsistencia |
| ADJ-07 | `api/router.py` | Separar en `router.py` + `schemas.py` + `dependencies.py` | Media | SRP |
| ADJ-08 | `domain/aggregates/performance.py` | Renombrar `registrarAP` → `registrar_ap` (snake_case) | Baja | Convención |

---

## Agrupación en US-IEDD para SP-ADJ-01

| US | Issues | Descripción | Capa |
|---|---|---|---|
| US-ADJ-1.1 | ADJ-03 + ADJ-06 + ADJ-08 | Domain cleanup: Performance property + OCP Competencia + snake_case | domain/ |
| US-ADJ-1.2 | ADJ-01 | Refactor ajustar_grilla: extraer helpers de OT y swap | domain/ |
| US-ADJ-1.3 | ADJ-02 | Consolidar stream IDs en módulo compartido | application/ |
| US-ADJ-1.4 | ADJ-04 + ADJ-05 | Router DIP: EventStorePort + cross-BC a app.py | api/ |
| US-ADJ-1.5 | ADJ-07 | Router SRP: separar schemas + dependencies | api/ |

**Criterio de agrupación:** misma capa arquitectural + pueden testearse juntos sin interferencia.
