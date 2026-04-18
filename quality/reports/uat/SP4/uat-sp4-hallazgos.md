# Hallazgos UAT SP4 — BL-004

**Fecha:** 2026-04-18  
**Branch:** feature/US-ADJ-6.7-uat-sp4  
**Ejecutado por:** Victor Valotto

---

## Resumen Ejecutivo

| ID | Área | Severidad | Estado | Descripción breve |
|----|------|-----------|--------|-------------------|
| BUG-SP4-001 | INC-4.6 (Export) | ALTA | Pendiente fix | `SQLiteEventStore` no auto-crea tabla `events` |
| BUG-SP4-002 | INC-4.6 (Export) | ALTA | Pendiente fix | Seed omite proyección `competencias_por_torneo` |
| BUG-SP4-003 | Seed / Setup | BAJA | Workaround aplicado | Seed crea torneo en EJECUCION; N.1 requiere INSCRIPCION_ABIERTA |
| BUG-SP4-004 | INC-4.4 (Sync) | MEDIA | Pendiente fix | Refresh post-sync vacía lista de atletas; back navigation la restaura |
| UX-SP4-001 | INC-4.6 (UI) | BAJA | Pendiente fix | IDs de competencia expuestos en lista de torneos |
| UX-SP4-002 | INC-4.6 (UI) | BAJA | Pendiente fix | Nombres de eventos en audit log usan identificadores de código, no lenguaje ubicuo |
| UX-SP4-003 | INC-4.6 (UI) | BAJA | Pendiente fix | Contenido del evento `AtletaLlamado` no es legible para el usuario final |
| SCOPE-SP4-001 | INC-4.5 (P-11) | N/A | Diferido a SP5 | Callback P-11 no conectado a `AsignarTarjetaHandler` |

---

## Hallazgos Detallados

### BUG-SP4-001 — `SQLiteEventStore` no inicializa su schema

**Área:** INC-4.6 — Exportación de resultados  
**Severidad:** ALTA (500 en producción en instancia limpia)  
**Reproducción:** Instancia nueva, `data/resultados.db` vacío → `GET /resultados/{id}/export` → 500  

**Síntoma:**
```
sqlite3.OperationalError: no such table: events
  File "src/shared/infrastructure/event_store/sqlite_event_store.py", line 61, in load
```

**Causa raíz:**  
`SQLiteEventStore` asume que la tabla `events` ya existe. No tiene mecanismo de auto-creación (`CREATE TABLE IF NOT EXISTS`). Todos los otros repositorios del sistema sí auto-crean sus tablas en `__init__` o en el primer acceso. Solo el event store compartido omite este paso.

**Fix requerido:**  
Agregar inicialización del schema en `SQLiteEventStore.__init__` o en un método `_ensure_table()` async llamado antes del primer `append` / `load`.

**Workaround aplicado en UAT:**
```sql
-- Ejecutado manualmente en data/resultados.db
CREATE TABLE IF NOT EXISTS events (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    stream_id   TEXT    NOT NULL,
    event_type  TEXT    NOT NULL,
    payload     TEXT    NOT NULL,
    version     INTEGER NOT NULL,
    occurred_at TEXT    NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    UNIQUE (stream_id, version)
);
```

**Archivos afectados:**  
`src/shared/infrastructure/event_store/sqlite_event_store.py`

---

### BUG-SP4-002 — Seed no registra proyección `competencias_por_torneo`

**Área:** INC-4.6 — Exportación de resultados / Seed SP4  
**Severidad:** ALTA (export retorna `disciplinas: []` para torneos creados por seed)  
**Reproducción:** Ejecutar `seed_sp4.py` → `GET /resultados/{torneo_id}/export` → 200 con `disciplinas: []`

**Síntoma:**  
```json
{
  "torneo_id": "ff2ccbea-...",
  "disciplinas": [],
  "overall": []
}
```

**Causa raíz:**  
El seed crea las competencias llamando directamente a `ConfigurarIntervaloOTHandler(store)` sin la proyección `CompetenciasPorTorneoPort`. Cuando el handler se invoca vía HTTP (`POST /competencia`), el router le inyecta la proyección y llama a `proyeccion.guardar()`. Al bypassear el router, esa llamada nunca ocurre y la tabla `competencias_por_torneo` no registra la relación torneo ↔ competencia.

La exportación usa `competencias_por_torneo.listar_por_torneo(torneo_id)` para descubrir qué competencias pertenecen al torneo. Sin esa entrada, retorna lista vacía.

**Fix requerido (dos opciones):**  
- **Opción A:** Modificar `seed_sp4.py` para registrar la proyección manualmente después de crear cada competencia.
- **Opción B:** Que `ConfigurarIntervaloOTHandler` reciba la proyección como puerto opcional y la actualice si está presente — consistente con cómo lo hace el router.

**Workaround aplicado en UAT:**
```python
from competencia.infrastructure.repositories.sqlite_competencias_por_torneo import SQLiteCompetenciasPorTorneo

proj = SQLiteCompetenciasPorTorneo("data/competencia.db")
await proj.guardar(UUID("ea228d82-..."), "DNF", UUID("ff2ccbea-..."))
await proj.guardar(UUID("c4d0b8aa-..."), "STA", UUID("ff2ccbea-..."))
```

También fue necesario recalcular el ranking manualmente (P-08), ya que la primera ejecución de `on_finalizada` falló por BUG-SP4-001.

**Archivos afectados:**  
`tests/uat/sp4/seed_sp4.py`, `src/competencia/application/commands/configurar_intervalo_ot.py` (si se elige Opción B)

---

### BUG-SP4-003 — Seed crea torneo en EJECUCION; Caso N.1 requiere INSCRIPCION_ABIERTA

**Área:** INC-4.5 — Setup de datos para Caso N.1 (P-10)  
**Severidad:** BAJA (no afecta producción; solo impacta el setup del UAT)  
**Reproducción:** Ejecutar seed → intentar inscribir atleta en torneo UAT → 409 Conflict

**Síntoma:**  
El torneo del seed avanza hasta estado `EJECUCION` como parte del setup de competencias. Pero el Caso N.1 (P-10) requiere inscribir un atleta con email real, lo que solo es posible con el torneo en `INSCRIPCION_ABIERTA`.

**Workaround aplicado en UAT:**  
Se utilizó "Smoke Test Open 2026" (`deccbf8f-7dca-4bfc-9351-e1d377c55a98`), torneo pre-existente en estado `INSCRIPCION_ABIERTA`, para ejecutar el Caso N.1.

**Fix recomendado:**  
Agregar un torneo separado de "inscripcion" en el seed, que no avance a EJECUCION, dedicado a probar P-10.

---

### SCOPE-SP4-001 — P-11 callback no conectado a `AsignarTarjetaHandler`

**Área:** INC-4.5 — Notificación de resultado de performance  
**Tipo:** Fuera de scope SP4 (diferido a SP5)  

**Descripción:**  
`build_p11_handler()` está implementado en `src/app.py` (línea 151) y tiene unit tests. Sin embargo, el callback no está inyectado en `AsignarTarjetaHandler` — este solo recibe `on_finalizada` (P-08/P-09). La política P-11 no se dispara al asignar tarjeta.

**Estado:**  
Aceptado como N/A en UAT SP4. El handler existe y está probado a nivel unitario. El wiring del callback queda pendiente para SP5.

**Archivos afectados (cuando se implemente):**  
`src/competencia/api/router.py` → `get_asignar_tarjeta_handler()`, `src/app.py`

---

---

### UX-SP4-001 — IDs de competencia expuestos en lista de torneos

**Área:** INC-4.6 — UI organizador  
**Severidad:** BAJA (no afecta funcionalidad, afecta presentación)

**Síntoma:** En la lista de torneos, debajo del nombre de cada competencia (DNF, STA) se muestran los UUIDs de competencia. El usuario final no necesita ni puede operar con esos IDs.

**Fix recomendado:** Ocultar o mover los IDs a un tooltip / vista de debug. En la UI mostrar solo disciplina y estado.

---

### UX-SP4-002 — Nombres de eventos en audit log usan identificadores de código

**Área:** INC-4.6 — UI auditoría (AuditoriaCompetenciaPage)  
**Severidad:** BAJA

**Síntoma:** Los eventos en la traza de performance muestran nombres como `APRegistrado`, `AtletaLlamado`, `ResultadoRegistrado` — identificadores del código fuente, no lenguaje ubicuo del dominio.

**Fix recomendado:** Agregar un mapa de traducción en el frontend: `APRegistrado` → "AP declarado", `AtletaLlamado` → "Atleta en llamada", `ResultadoRegistrado` → "Resultado registrado", `TarjetaAsignada` → "Tarjeta asignada".

---

### UX-SP4-003 — Contenido del evento `AtletaLlamado` no es legible

**Área:** INC-4.6 — UI auditoría  
**Severidad:** BAJA

**Síntoma:** Al expandir el evento `AtletaLlamado`, el contenido mostrado no es comprensible para el usuario final (probablemente expone el payload JSON crudo con UUIDs y nombres de campos técnicos).

**Fix recomendado:** Formatear el payload de cada tipo de evento con una vista legible: OT programado en formato hora local, posición en grilla, andarivel como número.

---

---

### BUG-SP4-004 — Refresh post-sync vacía la lista de atletas

**Área:** INC-4.4 — Offline-first, sync automático  
**Severidad:** MEDIA (flujo recuperable, pero confuso para el juez en competencia)

**Síntoma:** Al reconectar WiFi y hacer refresh manual, la lista de atletas de la grilla aparece vacía. Navegar hacia atrás y volver restaura la lista correctamente. El sync sí funcionó — los eventos llegaron al backend.

**Causa probable:** El componente de grilla no re-hidrata desde IndexedDB al montar tras el refresh; espera datos del servidor que aún no llegaron por timing del sync.

**Fix recomendado:** Al montar el componente de grilla, leer primero desde IndexedDB como fuente de verdad local, luego reconciliar con el servidor en background.

---

## Bugs que Requieren Fix Antes de BL-004

| Bug | Fix estimado | Impacto si no se corrige |
|-----|-------------|--------------------------|
| BUG-SP4-001 | ~30 min — agregar `_ensure_table` en `SQLiteEventStore` | 500 en export en cualquier instancia limpia |
| BUG-SP4-002 | ~45 min — registrar proyección en seed o en handler | Export siempre retorna `disciplinas: []` para seeds |

**Recomendación:** resolver ambos antes de cerrar BL-004 y taggear `v0.5.0`.

---

## Verificación Post-Fix

Después de aplicar los fixes, ejecutar:

```bash
# Limpiar DBs
rm -f data/resultados.db data/competencia.db

# Re-ejecutar seed
uv run python tests/uat/sp4/seed_sp4.py

# Verificar export (debe retornar disciplinas con ranking)
curl http://localhost:8000/resultados/{torneo_id}/export?format=json \
  -H "Authorization: Bearer $ORG_TOKEN"
```

El export debe retornar `disciplinas` con ranking DNF y STA sin intervención manual.
