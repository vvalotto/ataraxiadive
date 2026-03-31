# Plan de Implementación — US-3.3.1
## BC Competencia — torneo_id en ConfigurarIntervaloOT

**Branch:** `feature/US-3.3.1-torneo-id-competencia`
**Fecha:** 2026-03-31

---

## Estructura de Archivos

### Nuevos
```
src/competencia/application/queries/obtener_competencias_por_torneo.py
tests/features/US-3.3.1-torneo-id-competencia.feature   ← ya creado en Fase 1
```

### Modificados
```
src/competencia/domain/events/intervalo_ot_configurado.py  ← + torneo_id campo/payload
src/competencia/domain/aggregates/competencia.py           ← + torneo_id init/property/_apply
src/competencia/application/commands/configurar_intervalo_ot.py ← + torneo_id en command
src/competencia/api/router.py                              ← POST /competencia, GET ?torneo_id, torneo_id en estado
```

---

## Tareas

### T1 — Domain event: torneo_id en IntervaloOTConfigurado (5 min)
- Agregar `torneo_id: str | None = None` al dataclass
- `to_payload()`: incluir `"torneo_id": self.torneo_id`
- `from_payload()`: leer con `.get("torneo_id")` → backward compat con streams SP1/SP2

### T2 — Domain aggregate: torneo_id en Competencia (10 min)
- Agregar `torneo_id: UUID | None = None` a `__init__`, inicializar `self._torneo_id`
- Agregar property `torneo_id -> UUID | None`
- Actualizar `configurar_intervalo_ot()`: aceptar `torneo_id: UUID | None = None`,
  pasar `torneo_id=str(torneo_id) if torneo_id else None` al evento
- Actualizar `_apply_intervalo_ot_configurado()`: `self._torneo_id = UUID(p["torneo_id"]) if p.get("torneo_id") else None`

### T3 — Application command: torneo_id en ConfigurarIntervaloOTCommand (5 min)
- Agregar `torneo_id: UUID | None = None` al dataclass (campo con default → backward compat)
- `ConfigurarIntervaloOTHandler.handle()`: pasar `torneo_id=command.torneo_id` al método de dominio

### T4 — Application query: ObtenerCompetenciasPorTorneo (15 min)
- `ObtenerCompetenciasPorTorneoQuery(torneo_id: UUID)`
- `CompetenciaSummaryDTO(competencia_id: UUID, disciplina: str, torneo_id: UUID)`
- `ObtenerCompetenciasPorTorneoHandler`: itera streams del event store buscando `IntervaloOTConfigurado`
  con `torneo_id` coincidente en el payload del primer evento
- Puerto de lectura: `EventStorePort.load_all_streams()` si existe, o implementación directa en SQLite

### T5 — API: nuevos endpoints + torneo_id en estado (15 min)
- Schema `ConfigurarOTBody(disciplina, intervalo_minutos, configurado_por, torneo_id=None)`
- `POST /competencia` → llama `ConfigurarIntervaloOTCommand`, retorna 201 `{ competencia_id }`
- `GET /competencia?torneo_id={uuid}` → `ObtenerCompetenciasPorTorneoHandler`, retorna lista
- Actualizar respuesta de `GET /{competencia_id}/estado` para incluir `torneo_id`
- Actualizar `EstadoCompetenciaDTO` para incluir `torneo_id: UUID | None`

---

## Decisiones de Diseño

1. **Backward compat total**: `torneo_id` es `None` por default en todos los niveles.
   Los 643 tests existentes no pasan `torneo_id` → siguen funcionando sin modificación.

2. **`from_payload()` con `.get()`**: los streams persisitdos en SP1/SP2 no tienen
   `torneo_id` en el payload → se lee como `None` sin error.

3. **`POST /competencia`**: el primer comando de dominio (ConfigurarIntervaloOT) es el
   acto de "crear" una competencia desde la perspectiva de la API. Coherente con
   Event Sourcing: la competencia existe desde su primer evento.

4. **`ObtenerCompetenciasPorTorneo`**: escanea el event store buscando el primer evento
   `IntervaloOTConfigurado` por stream y filtra por `torneo_id`. Aceptable en SP3
   (volumen bajo); en producción se agregaría una tabla de proyección.

---

## Estimación Total: ~50 min
