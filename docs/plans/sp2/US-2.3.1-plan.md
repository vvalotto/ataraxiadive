# Plan de Implementación: US-2.3.1 — Ejecución Multi-Andarivel

**Patrón:** Hexagonal DDD — BC Competencia (Event Sourcing)
**Estimación Total:** 1h 35min
**Branch:** `feature/US-2.3.1-ejecucion-multi-andarivel`

---

## Componentes a Implementar

### Tarea 1 — Port `AndarivelesActivosPort` (Domain)
- [ ] `src/competencia/domain/ports/andariveles_activos_port.py` (15 min)
  - `AndarivelesActivosData`: DTO con `numero`, `ocupado`, `atleta_id`, `performance_id`, `ot_programado`
  - `AndarivelesActivosPort` (ABC):
    - `get_andariveles_activos(competencia_id, disciplina, andariveles)` → `list[AndarivelesActivosData]`
    - `is_andarivel_activo(competencia_id, disciplina, numero_andarivel)` → `bool` (para verificar INV-C-05)

### Tarea 2 — Modificar `LlamarAtletaHandler` (Application)
- [ ] `src/competencia/application/commands/llamar_atleta.py` (20 min)
  - Agregar excepción `AndarivelesConflicto`
  - `LlamarAtletaCommand`: agregar campo `andarivel: int`
  - `LlamarAtletaHandler.__init__`: inyectar `AndarivelesActivosPort`
  - `handle()`: verificar INV-C-05 con `is_andarivel_activo()` antes de cargar Performance

### Tarea 3 — Query `ObtenerAndarivelesActivosHandler` (Application)
- [ ] `src/competencia/application/queries/obtener_andariveles_activos.py` (15 min)
  - `ObtenerAndarivelesActivosQuery`: `competencia_id`, `disciplina`, `andariveles`
  - `ObtenerAndarivelesActivosHandler.handle()` → `list[AndarivelesActivosData]`

### Tarea 4 — `AndarivelesActivosAdapter` (Infrastructure)
- [ ] `src/competencia/infrastructure/repositories/andariveles_activos_adapter.py` (25 min)
  - Lee todos los streams `performance-{cid}-*` de la disciplina
  - Reconstituye cada `Performance` y proyecta el estado del andarivel
  - Andarivel `ocupado = True` solo si `estado == EstadoPerformance.Llamada`
  - Construye `list[AndarivelesActivosData]` para todos los andariveles 1..N

### Tarea 5 — Endpoint `GET /competencia/{id}/andariveles` (API)
- [ ] `src/competencia/api/router.py` (20 min)
  - Agregar dependencia `AndarivelesActivosAdapter`
  - `GET /competencia/{id}/andariveles?disciplina=STA&andariveles=2`
  - Response schema: lista de `{ numero, ocupado, atleta_id, performance_id, ot_programado }`

---

## Dependencias entre tareas

```
Tarea 1 → Tarea 2
Tarea 1 → Tarea 3
Tarea 1 → Tarea 4
Tarea 3 + Tarea 4 → Tarea 5
```

---

## Aclaraciones de diseño

- `LlamarAtletaCommand` agrega `andarivel: int` — el router ya conoce el andarivel
  del atleta (lo tiene en la grilla); los tests existentes de `LlamarAtleta` deben
  actualizarse para incluir este campo.
- `AndarivelesActivosPort.is_andarivel_activo()` es el método usado por `LlamarAtletaHandler`
  para verificar INV-C-05. El método `get_andariveles_activos()` lo usa el query handler
  para el endpoint READ.
- El número total de andariveles se infiere del evento `GrillaDeSalidaGenerada`
  (campo `andariveles`) o se pasa como query param al endpoint.

---

**Estado:** 0/5 tareas completadas
