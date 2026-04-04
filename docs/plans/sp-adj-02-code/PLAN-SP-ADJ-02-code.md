# PLAN-SP-ADJ-02-code — Sprint de Ajuste Técnico Post-Revisión BL-002

| Campo | Valor |
|-------|-------|
| **Sprint** | SP-ADJ-02-code |
| **Contexto** | Gaps de código detectados en revisión de consistencia BL-002 |
| **Revisión fuente** | `.work/revision-consistencia.md` (bloque B) |
| **Branch base** | `develop` |
| **Fecha inicio** | 2026-03-28 |
| **Pipeline** | `/implement-us` — 10 fases por US |

---

## Objetivo

Cerrar los 5 gaps de código (B-01 a B-05) identificados en la revisión de hito.
Los gaps son violaciones de la Regla de Oro (§6 CLAUDE.md) y del DIP que quedaron
fuera del scope de SP-ADJ-01.

El resultado debe ser:
- `shared/domain/value_objects/` contiene `Disciplina`, `DisciplinaDescriptor`, `UnidadMedida`
- `resultados/` no importa nada de `competencia.domain` ni `competencia.infrastructure`
- `competencia/api/router.py` no importa nada de `resultados/`
- `EventStoreDep` tipado como `EventStorePort` (no `SQLiteEventStore`)

---

## Gaps a cerrar

| Gap | Descripción | Prioridad | US |
|-----|-------------|-----------|-----|
| B-01 | `resultados/domain/` importa `Disciplina` y `DisciplinaDescriptor` desde `competencia.domain` | Crítica | US-ADJ-2.6 |
| B-02 | `resultados/application/` importa `DisciplinaDescriptorAdapter` desde `competencia.infrastructure` | Crítica | US-ADJ-2.6 |
| B-03 | `competencia/api/router.py` importa `CalcularRankingHandler` desde `resultados/` | Crítica | US-ADJ-2.7 |
| B-04 | `resultados/api/router.py` importa `SQLiteEventStore` desde `competencia.infrastructure` | Crítica | US-ADJ-2.7 |
| B-05 | `EventStoreDep` tipado como `SQLiteEventStore` en vez de `EventStorePort` | Moderada | US-ADJ-2.8 |

---

## US-IEDD del Sprint

| US | Gaps | Descripción | Artefactos principales | Prioridad |
|----|------|-------------|------------------------|-----------|
| US-ADJ-2.6 | B-01, B-02 | Mover `Disciplina`, `DisciplinaDescriptor`, `UnidadMedida` a `shared/domain/value_objects/` y actualizar todos los imports | `shared/domain/value_objects/`, `competencia/domain/`, `resultados/domain/`, todos los ~41 import sites | Crítica |
| US-ADJ-2.7 | B-03, B-04 | Mover el cableado de la política P-08 (CalcularRankingHandler) desde `competencia/api/router.py` a `src/app.py` (composition root) | `src/app.py`, `competencia/api/router.py`, `resultados/api/router.py` | Crítica |
| US-ADJ-2.8 | B-05 | Corregir DIP en `competencia/api/router.py`: `get_event_store() → EventStorePort` y `EventStoreDep = Annotated[EventStorePort, ...]` | `competencia/api/router.py` | Moderada |

**Orden de implementación:** US-ADJ-2.6 → US-ADJ-2.7 → US-ADJ-2.8

Rationale: US-ADJ-2.6 es bloqueante — elimina la violación de imports antes de reorganizar
el wiring en US-ADJ-2.7. US-ADJ-2.8 es independiente pero va al final por menor impacto.

---

## DoD del Sprint

- [ ] `shared/domain/value_objects/disciplina.py` existe y es la fuente canónica de `Disciplina`
- [ ] `shared/domain/value_objects/disciplina_descriptor.py` existe y es la fuente canónica de `DisciplinaDescriptor`
- [ ] `shared/domain/value_objects/unidad_medida.py` existe y es la fuente canónica de `UnidadMedida`
- [ ] `competencia/domain/value_objects/disciplina.py` redirige (re-export) o se elimina con backward-compat
- [ ] `grep -r "from competencia.domain" src/resultados/` devuelve cero matches
- [ ] `grep -r "from competencia.infrastructure" src/resultados/` devuelve cero matches
- [ ] `grep -r "from resultados" src/competencia/api/router.py` devuelve cero matches
- [ ] `get_event_store()` declara retorno `EventStorePort`
- [ ] `EventStoreDep = Annotated[EventStorePort, ...]`
- [ ] `pytest tests/` — 100% pass, sin regresiones
- [ ] DesignReviewer — cero violations CRITICAL

---

## Consideraciones técnicas

### US-ADJ-2.6 — Estrategia de migración de imports

El movimiento de `Disciplina` impacta ~41 archivos. Estrategia recomendada:

1. Crear los tres archivos en `shared/domain/value_objects/`
2. En `competencia/domain/value_objects/`, reemplazar la definición por un re-export
   hacia `shared.domain.value_objects` — así los tests de competencia no se rompen
3. Actualizar los 6 archivos de `resultados/` que importan desde `competencia.domain`
4. Actualizar `shared/domain/value_objects/__init__.py`
5. Actualizar `competencia/domain/value_objects/__init__.py`

El re-export en competencia es transitorio — en SP3 se migran los ~35 imports internos
si se decide eliminar la indirección.

### US-ADJ-2.7 — Inyección del callback P-08

El mecanismo existente: `competencia/api/router.py` tiene `get_on_finalizada_callback()`
que construye el `CalcularRankingHandler`. Esto se mueve a `app.py`.

FastAPI soporta `app.dependency_overrides` pero la solución más simple es que `app.py`
construya el callback y lo pase al router antes de `include_router()`.

### US-ADJ-2.8 — Mínimo cambio

Solo cambia el tipo declarado. El runtime sigue retornando `SQLiteEventStore`.
El import de `SQLiteEventStore` permanece en `router.py` (dentro del factory `get_event_store`).

---

## Branching

```
develop
  └── feature/US-ADJ-2.6-disciplina-shared-domain
  └── feature/US-ADJ-2.7-composition-root-app
  └── feature/US-ADJ-2.8-dip-event-store
```

---

## Archivos de especificación

- `docs/specs/sp-adj-02-code/US-ADJ-2.6.md`
- `docs/specs/sp-adj-02-code/US-ADJ-2.7.md`
- `docs/specs/sp-adj-02-code/US-ADJ-2.8.md`

---

## Referencias

- Revisión de hito: `.work/revision-consistencia.md` (bloque B)
- Plan documental: `docs/plans/sp-adj-02-doc/PLAN-SP-ADJ-02-doc.md`
- Regla de Oro: `CLAUDE.md §6`
- ADR-006: `docs/adr/ADR-006-estructura-bc-first.md`
- Patrón SP-ADJ: `docs/contexto/HITO-13-SP-ADJ-DEUDA-TECNICA-COMO-ETAPA-FORMAL.md`

---

*Redactado: 2026-03-28 — SP-ADJ-02-code*
*Mantenido por: Claude Cowork + Victor Valotto*
