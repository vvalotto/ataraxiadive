# Plan de Implementación — US-2.2.2
## API Disciplina-Aware + Avance Automático

**Fecha:** 2026-03-27
**BC:** `competencia` | **Incremento:** Inc 2.2 | **Puntos:** 3

---

## Análisis de impacto

### Prerequisitos satisfechos (US-2.2.1)
- `DisciplinaDescriptor` VO — `src/competencia/domain/value_objects/disciplina_descriptor.py` ✅
- `DisciplinaDescriptorPort` — `src/competencia/domain/ports/disciplina_descriptor_port.py` ✅
- `DisciplinaDescriptorAdapter` — `src/competencia/infrastructure/repositories/disciplina_descriptor_adapter.py` ✅

### Componentes afectados
| Componente | Cambio | Capa |
|---|---|---|
| `Performance` aggregate | Add `_posicion_grilla` state + property + `disciplina` property | domain |
| `RegistrarResultadoHandler` | Inject `DisciplinaDescriptorPort`, validar unidad | application |
| `RegistrarAPHandler` | Inject `DisciplinaDescriptorPort`, validar unidad | application |
| `ObtenerProximasPerformancesHandler` | Sort por posicion_grilla desde Competencia.grilla | application |
| `ObtenerPerformanceActualHandler` | Add `unidad_esperada` al DTO | application |
| `PerformanceActualDTO` | Add campo `unidad_esperada: str` | application |
| `ObtenerProximasPerformancesQuery` | Add `disciplina: Disciplina` | application |
| `router.py` | Inyectar adapter, exponer `unidad_esperada`, pasar `disciplina` a query proximas | api |

---

## Tareas

### T1 — `Performance` aggregate: `posicion_grilla` + `disciplina` (domain)
**Archivo:** `src/competencia/domain/aggregates/performance.py`
- Add `self._posicion_grilla: int | None = None` en `__init__`
- En `_apply_atleta_llamado`: `self._posicion_grilla = payload["posicion_grilla"]`
- Add property `posicion_grilla: int | None`
- Add property `disciplina: Disciplina` (requerido por ObtenerPerformanceActualHandler)
**Est:** 10 min

### T2 — `UnidadIncompatible` + validación en `RegistrarResultadoHandler` (application)
**Archivo:** `src/competencia/application/commands/registrar_resultado.py`
- Add `class UnidadIncompatible(Exception)` en sección excepciones
- Agregar `disciplina_descriptor: DisciplinaDescriptorPort` al `__init__`
- En `handle()`, ANTES de llamar `Performance.reconstitute`: obtener `descriptor = self._disciplina_descriptor.describe(command.disciplina)`, verificar `command.unidad == descriptor.unidad_esperada` → raise `UnidadIncompatible`
**Est:** 15 min

### T3 — Validación de unidad en `RegistrarAPHandler` (application)
**Archivo:** `src/competencia/application/commands/registrar_ap.py`
- Import `UnidadIncompatible` desde `registrar_resultado`
- Agregar `disciplina_descriptor: DisciplinaDescriptorPort` al `__init__`
- En `handle()`, como primera validación: obtener descriptor, verificar unidad → raise `UnidadIncompatible`
**Est:** 10 min

### T4 — `ObtenerProximasPerformancesHandler`: sort por posicion_grilla (application)
**Archivo:** `src/competencia/application/queries/obtener_proximas_performances.py`
- Add `disciplina: Disciplina` a `ObtenerProximasPerformancesQuery`
- En `handle()`: cargar stream `competencia-{query.competencia_id}`, reconstitute `Competencia`, build map `{performance_id: posicion}` desde `competencia.grilla`
- Cambiar sort de `occurred_at` a posicion del mapa (fallback `float("inf")` si no está en grilla)
- Set `posicion=grilla_map[performance.performance_id]` en lugar del índice del loop
**Est:** 20 min

### T5 — `ObtenerPerformanceActualHandler`: `unidad_esperada` en DTO (application)
**Archivo:** `src/competencia/application/queries/obtener_performance_actual.py`
- Add `unidad_esperada: str` a `PerformanceActualDTO`
- Agregar `disciplina_descriptor: DisciplinaDescriptorPort` al `__init__`
- En `_to_dto()`: `descriptor = self._disciplina_descriptor.describe(performance.disciplina)`, set `unidad_esperada=descriptor.unidad_esperada.value`
**Est:** 10 min

### T6 — `router.py`: inyectar adapter + exponer nuevos campos (api)
**Archivo:** `src/competencia/api/router.py`
- Import `DisciplinaDescriptorAdapter`, `DisciplinaDescriptorPort`
- Add dependency provider `get_disciplina_descriptor()` → `DisciplinaDescriptorAdapter()`
- `DisciplinaDescriptorDep = Annotated[DisciplinaDescriptorPort, Depends(get_disciplina_descriptor)]`
- Update `get_obtener_performance_actual_handler` para inyectar adapter
- Update endpoint `GET /performance/actual` JSON para incluir `unidad_esperada`
- Update `GET /performance/proximas` para aceptar `disciplina: Disciplina` como query param y pasarlo a `ObtenerProximasPerformancesQuery`
**Est:** 15 min

---

## Estimación total: ~80 min

---

## Decisiones de diseño

1. **`UnidadIncompatible` definida en `registrar_resultado.py`, importada en `registrar_ap.py`** — evita duplicación. La spec dice "respectivamente" pero el significado es el mismo.

2. **`ObtenerProximasPerformancesHandler` carga Competencia para obtener posiciones** — única fuente de verdad para el orden de grilla es `competencia.grilla`. Se añade `disciplina` a la query para poder reconstitute Competencia.

3. **`posicion_grilla` en Performance.`_apply_atleta_llamado`** — almacena el valor al momento de ser llamado, para consultas futuras sin re-parsear eventos. Para AnunciadaAP, `posicion_grilla` es `None` (no llamadas), pero la query obtiene posición desde el aggregate Competencia.

4. **`disciplina` property en Performance** — expone la disciplina del aggregate para que handlers de query puedan obtener el descriptor sin re-parsear eventos.
