# Revisión de Calidad — Cierre SP4
## Issues Consolidados — Candidatos a SP-ADJ-06

**Fecha:** 2026-04-16
**Fuentes:**
- `01-designreviewer.md` — DesignReviewer BL-004 (0 CRITICAL, 196 WARNING)
- `02-analisis-bc-notificaciones.md` — BC Notificaciones (INC-4.5)
- `03-analisis-frontend.md` — Frontend arquitectura (INC-4.2..4.4)
- `04-revision-solid.md` — Revisión SOLID código nuevo SP4
- `05-architectanalyst.md` — ArchitectAnalyst BL-004 (6 CRITICAL, 56 WARNING)

---

## Issues resueltos durante esta revisión

| ID | Issue | Resolución |
|----|-------|-----------|
| DOC-01 | P-11 documentada como TarjetaAsignada(roja) en `notificaciones.md` y `CLAUDE.md` | ✅ Corregido en sesión — commit `735cf7e` |

---

## Acción requerida ANTES del tag v0.5.0

### LAZY-01 — Lazy import cross-BC en `exportar_resultados.py`

```python
# resultados/application/queries/exportar_resultados.py
def _performance_a_resultado_final(...):
    from src.competencia.domain.aggregates.performance import Performance
```

`resultados/application/` importa `Performance` de `competencia/domain/`. Si este import
es necesario en runtime (no solo bajo TYPE_CHECKING), hay un acoplamiento cross-BC real
que viola la arquitectura hexagonal.

**Verificación requerida:** ¿qué se usa de `Performance`? ¿Es posible eliminarlo usando
el repositorio de Competencia como puerto o proyectando solo los datos necesarios?

**Bloqueante:** si el import es necesario y no tiene alternativa limpia, hay un problema
de diseño que debe resolverse antes del tag. Si el import se puede eliminar o mover bajo
TYPE_CHECKING, es deuda media.

**Responsable:** investigar antes de ejecutar `merge develop → main`.

---

## SP-ADJ-06 — Candidatos clasificados

### Prioridad Alta

| ID | Área | Issue | Fuente |
|----|------|-------|--------|
| AA-01 | `competencia/domain/aggregates/performance_state.py` | Ciclo ADP: `reconstituir_performance()` hace lazy import de `Performance` — debería ser `Performance.reconstituir()` classmethod | AA |
| DR-01 | `torneo` aggregate | LCOM=6 (doble vs BL-003). Si supera 8 en BL-005 → separar responsabilidades | DR |

**AA-01 — Fix concreto:**
```python
# Antes: función en performance_state.py que importa Performance (ciclo)
def reconstituir_performance(events) -> "Performance":
    from competencia.domain.aggregates.performance import Performance
    ...

# Después: classmethod en Performance (sin ciclo)
@classmethod
def reconstituir(cls, events: list[dict]) -> "Performance":
    from competencia.domain.aggregates import performance_state
    # performance_state.apply_* ya reciben self — sin necesidad de importar Performance
```

---

### Prioridad Media

| ID | Área | Issue | Fuente | Fix estimado |
|----|------|-------|--------|:------------:|
| OCP-01 | `competencia/application/_p08_finalizacion.py` | `inspect.signature(on_finalizada)` para ramificar por aridad del callback — unificar firma | SOLID | S |
| DES-01 | `notificaciones/application/policies/` | `_registrar_fallo_sin_email` duplicado entre P-10 y P-11 — extraer función compartida | NOTIF | S |
| DR-04 | `competencia/domain/events/performance_events.py` | DataClumps ×7: `(performance_id, participante_id, disciplina)` → candidato `PerformanceContext` VO | DR | M |
| SRP-01 | `resultados/application/queries/exportar_resultados.py` | Handler mezcla replay de eventos, ranking y exportación. Funciones de módulo duplican lógica del aggregate | SOLID | L |
| FE-ARCH-02 | `frontend/src/pages/juez/GrillaPage.tsx` | Importa `getCommandsByCompetencia` de `db/queries` directamente — mover a `useComandoQueue` o `useCommandStatus` | FE | S |
| DR-02 | `competencia/domain/aggregates/performance.py` | LongMethod 65/20 — identificar cuál método y si hay complejidad accidental | DR | M |
| DR-03 | `competencia/application/_p08_finalizacion.py` | LongMethod 62/20 — crecimiento SP3→SP4 continuo (parcialmente aliviado por OCP-01) | DR | M |

**Leyenda Fix:** S = small (< 2h) · M = medium (2-4h) · L = large (> 4h)

---

### Prioridad Baja

| ID | Área | Issue | Fuente |
|----|------|-------|--------|
| DES-02 | `notificaciones/application/policies/politica_p11.py` | `_evento_fuente_id` sin `@staticmethod` — causa LCOM=2 | NOTIF |
| FE-DES-01 | `frontend/src/hooks/usePerformanceFlow.ts` | `formatMarca` y `buildResultadoValue` exportadas desde hook — mover a `utils/marca.ts` | FE |
| FE-ARCH-01 | `frontend/src/pages/organizador/` | Páginas del organizador llaman `api/` directamente sin hooks — inconsistente con patrón del juez | FE |
| DR-06 | `competencia/domain/entities/grilla_de_salida.py` | LCOM=3/1 + 3 LongMethod — cohesión baja desde la extracción en SP-ADJ-03 | DR |
| DR-07 | `competencia/infrastructure/` | `AndarivelesActivosAdapter` LongMethod 52/20 — 3er SP consecutivo sin atacar | DR |

**Nota FE-ARCH-01:** es deuda de consistencia, no de correctitud. Solo justifica US-IEDD si SP5 introduce requisito de caché o estado compartido en el organizador. Si no, puede documentarse como deuda aceptada (ver HITO-25).

---

### No candidatos (aceptados)

| ID | Área | Razón |
|----|------|-------|
| ARCH-01 | `sqlite_notificacion_repository.py` | DIP leve — funciona correctamente, inyección ocurre en `app.py` |
| ARCH-02 | `sqlite_notificacion_event_store.py` | `_ensure_schema` en cada operación — deuda compartida con Competencia, bajo impacto |
| SRP-02 | `resolucion_tarjeta.py` | Mezcla construcción + serialización — inevitable en VO con Event Sourcing |
| AA-02 | `torneo` D=0.64 | Mismo patrón que BCs CRUD aceptados — documentar, no actuar |
| DR-01 (monitor) | `torneo` LCOM=6 | Umbral de acción: LCOM > 8 en BL-005 |
| 56 warnings Instability | Todo el backend | Falso positivo estructural de hexagonal — capas internas siempre I≈1 |
| 100+ warnings FeatureEnvy | commands/, queries/, repositories/ | Falso positivo CQRS/Repository — patrón intencional |

---

## Resumen por área

| Área | Alta | Media | Baja | Total candidatos |
|------|:----:|:-----:|:----:|:----------------:|
| Arquitectura (AA) | 1 | — | — | 1 |
| DesignReviewer (DR) | 1 | 3 | 2 | 6 |
| BC Notificaciones | — | 1 | 1 | 2 |
| SOLID | — | 2 | — | 2 |
| Frontend (FE) | — | 1 | 2 | 3 |
| **Total** | **2** | **7** | **5** | **14** |

---

## Pendiente de SP-ADJ-05 (diferido post-BL-003)

Los siguientes items de SP-ADJ-05 siguen pendientes y deberían evaluarse para SP-ADJ-06:

| Item | Descripción |
|------|-------------|
| FAZ→FAAS | 9 archivos con "FAZ" en lugar de "FAAS" — corrección en docs y código |
| D-01..D-09 | Issues documentales/metodológicos de HITO-14 (ver `docs/plans/sp-adj-05/`) |

---

## Propuesta de scope SP-ADJ-06

Un SP-ADJ equilibrado atacaría:

1. **LAZY-01** — verificar y resolver antes del tag (no es SP-ADJ, es pre-merge)
2. **AA-01** — eliminar el único ciclo ADP del codebase (alta, fix claro)
3. **OCP-01** + **DES-01** — dos fixes pequeños con alto impacto de claridad
4. **DES-02** — fix trivial de una línea (@staticmethod)
5. **FE-ARCH-02** + **FE-DES-01** — dos ajustes frontend de cohesión
6. **DR-04** — `PerformanceContext` VO si hay tiempo (deuda creciente con cada nueva factory)
7. **FAZ→FAAS** — corrección documental heredada

Los items DR-02, DR-03, SRP-01 y FE-ARCH-01 son candidatos a SP5-US o a un SP-ADJ-07
post-BL-005, dependiendo del scope que tome SP5.

---

*Creado: 2026-04-16 — Revisión pre-BL-004 — consolidación de pasos 01–05*
