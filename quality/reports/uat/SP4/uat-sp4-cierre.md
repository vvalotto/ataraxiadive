# Plan de Pruebas UAT — SP4 Cierre (US-ADJ-6.7)

**Versión:** 2.0 (resultados completos)
**Fecha:** 2026-04-18  
**Sprint:** SP-ADJ-06  
**Baseline objetivo:** BL-004 (`v0.5.0`)  
**Ejecutado por:** Victor Valotto  
**Resultado final:** `PARCIAL — PASS con bugs registrados, pendiente fix BUG-SP4-001 y BUG-SP4-002`

---

## Alcance

Este UAT valida los tres incrementos pendientes de SP4 antes de cerrar BL-004:

| INC | Descripción | Método |
|-----|-------------|--------|
| INC-4.4 | Offline-first (Service Worker + IndexedDB + Background Sync) | Manual — iPhone, guion existente |
| INC-4.5 | BC Notificaciones — email real vía Resend | Manual — smoke test |
| INC-4.6 | Auditoría y exportación (audit log UI + hash SHA-256 + CSV/JSON) | HTTP + UI |

**Prerequisito:** US-ADJ-6.1 a US-ADJ-6.6 mergeadas en `develop`. ✅

---

## Entorno de Pruebas

| Variable | Valor |
|----------|-------|
| Backend | `http://localhost:8000` (Mac) / `http://192.168.0.20:8000` (LAN) |
| Frontend | `http://192.168.0.20:5173` |
| Juez | `juez@uat-sp4.test` / `juezsp4uat2025` |
| Organizador | `organizador@uat-sp4.test` / `orgsp4uat2025` |
| Dispositivo juez | **iPhone** (Safari iOS) — INC-4.4 offline-first |
| Dispositivo organizador | **iPad** (Safari iPadOS) — INC-4.6 audit log UI |
| Datos de prueba | `quality/reports/uat/SP4/uat_ids.json` |

**Nota IP:** La IP de la Mac cambió de `192.168.0.28` a `192.168.0.20` respecto al plan original. El Vite proxy se corrió sin override de `VITE_API_URL` para evitar ECONNRESET por firewall macOS.

---

## Área 1 — INC-4.4 Offline-first

> **Guion completo:** `quality/reports/uat/SP4/guion-validacion-inc-4.4.md` (v4.0)
> **Dispositivo:** iPhone — Safari iOS

### Resumen INC-4.4

| US | Casos ejecutados | Resultado | Observaciones |
|----|-----------------|-----------|---------------|
| US-4.4.1 — Precarga | 1.1, 1.2 | **PASS** | Grilla visible sin conexión (WiFi desactivado). Navegación al detalle de atleta funciona offline. |
| US-4.4.2 — Cola offline | 2.1 | **PASS** | Performance completa registrada offline. UI muestra "3 pendientes". |
| US-4.4.3 — Sync automático | 3.1, 3.2 | **PASS** | Al reconectar WiFi, sync automático. Estado "sincronizado" visible. Eventos `AtletaLlamado` + `ResultadoRegistrado` + `TarjetaAsignada` persistidos en backend (verificado en competencia.db). |

**Conclusión INC-4.4:** `PASS`

**Bug detectado:** BUG-SP4-004 — Refresh manual post-sync vacía la lista de atletas. Navegar hacia atrás la restaura. No bloquea la funcionalidad core pero es confuso en competencia real.

**Fecha de ejecución INC-4.4:** 2026-04-18

---

## Área 2 — INC-4.5 Notificaciones (smoke test email real)

> Los emails son disparados por dos políticas:
> - **P-10** → `AtletaInscripto` → email de confirmación de inscripción
> - **P-11** → `PerformanceFinalizada` → email de resultado al atleta

---

### Caso N.1 — Email de confirmación de inscripción (P-10)

**Atleta creado:** Victor UAT (`vvalotto@gmail.com`), inscripto en DNF del torneo "Smoke Test Open 2026" (`deccbf8f`).

> **Nota:** Se usó "Smoke Test Open 2026" en lugar del torneo del seed porque el torneo UAT SP4 ya estaba en estado `EJECUCION` y no acepta nuevas inscripciones. Ver BUG-SP4-003.

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | POST `/registro/inscripciones` → 201 | **PASS** |
| 2 | `NotificacionSolicitada` + `NotificacionEnviada` en notificaciones.db | **PASS** |
| 3 | `proveedor_id` es UUID real de Resend (no prefijo `log-`) | **PASS** — `776f774f-0641-41ab-b806-b0b09d6b4b7a` |
| 4 | Inbox vvalotto@gmail.com → email recibido | **PASS** |

**Contenido del email recibido:**
```
Hola Victor UAT,
Tu inscripcion al torneo Smoke Test Open 2026 ha sido confirmada.
Fecha: 2026-06-01 · Sede: Club Náutico Test · Disciplinas inscriptas: DNF
Buena suerte! El equipo de AtaraxiaDive
```

**Resultado N.1:** `PASS`

---

### Caso N.2 — Idempotencia: doble inscripción no genera doble email (P-10)

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | Segunda llamada a inscripción → 409 Conflict | **PASS** |
| 2 | Solo 1 `NotificacionEnviada` para `evento_fuente_id = 2f83e1fb-...` en notificaciones.db | **PASS** |
| 3 | Sin email duplicado en inbox | **PASS** |

**Resultado N.2:** `PASS`

---

### Caso N.3 — Email de resultado de performance (P-11)

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | Al asignar tarjeta, P-11 se dispara | **N/A** |
| 2 | `NotificacionSolicitada` + `NotificacionEnviada` generados | **N/A** |
| 3 | Email recibido en inbox | **N/A** |

**Resultado N.3:** `N/A`

**Observación:** `build_p11_handler()` está implementado en `src/app.py:151` con unit tests. El wiring del callback a `AsignarTarjetaHandler` no está conectado en SP4. El handler solo recibe `on_finalizada` (P-08/P-09). Diferido a SP5. Ver SCOPE-SP4-001 en hallazgos.

---

### Resumen INC-4.5

**Conclusión INC-4.5:** `PASS` (P-10 completamente validado; P-11 diferido a SP5)

**Fecha de ejecución INC-4.5:** 2026-04-18

---

## Área 3 — INC-4.6 Auditoría y Exportación

---

### Caso A.1 — Audit log via API

```
GET /competencia/ea228d82-.../performances/aec7f8b4-.../audit-log
```

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | GET → 200 | **PASS** |
| 2 | Response contiene `eventos` con al menos 1 entrada | **PASS** — 1 evento `APRegistrado` |
| 3 | Eventos en orden cronológico ascendente | **PASS** |
| 4 | Cada evento tiene `tipo`, `timestamp` y `datos` | **PASS** |

**Resultado A.1:** `PASS`

---

### Caso A.2 — Audit log via UI (organizador)

> Ejecutado en iPad — Safari iPadOS como `organizador@uat-sp4.test`

| Paso | Acción | Resultado |
|------|--------|-----------|
| 1 | Login como organizador | **PASS** — Panel del Organizador visible |
| 2 | Navegar a auditoría de competencia DNF | **PASS** — "Ver Auditoría" accesible |
| 3 | Lista de atletas visible con su estado | **PASS** — Lista con estados (Ejecutada / Pendiente) |
| 4 | Seleccionar atleta → ver traza de performance con 4 eventos | **PASS** — Eventos con nombre y timestamp |
| 5 | Acceder como juez → redirige a "Mis disciplinas" | **PASS** — Control de acceso por rol funciona |

**Resultado A.2:** `PASS`

**Hallazgos UX:**
- UX-SP4-001: IDs de competencia (UUIDs) expuestos debajo del nombre en la lista de torneos
- UX-SP4-002: Nombres de eventos en audit log usan identificadores de código (`APRegistrado`, `AtletaLlamado`), no lenguaje ubicuo
- UX-SP4-003: Contenido del evento `AtletaLlamado` no es legible para el usuario final

---

### Caso A.3 — Hash SHA-256 al finalizar disciplina

```
GET /competencia/ea228d82-.../estado?disciplina=DNF
→ { "estado": "Finalizada", "hash_sha256": "58e78043de5bc29bd552e13d3c7268efbe187f7871463ab920ad2ced3b7aa33e" }
```

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | Campo `hash_sha256` presente cuando `estado=Finalizada` | **PASS** |
| 2 | Hash tiene 64 caracteres hexadecimales | **PASS** — `58e78043...` (64 chars) |
| 3 | Hash coincide con el del export JSON | **PASS** — mismo valor en A.4 |
| 4 | Hash visible en UI de auditoría | **PASS** (verificado en A.2 UI) |

**Resultado A.3:** `PASS`

---

### Caso A.4 — Exportación JSON

```
GET /resultados/ff2ccbea-.../export?format=json → 200
```

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | GET `?format=json` → 200 | **PASS** |
| 2 | Response tiene `torneo_id`, `torneo_nombre`, `exportado_en`, `disciplinas`, `overall` | **PASS** |
| 3 | Disciplina DNF (Finalizada) incluye `hash_sha256` | **PASS** |
| 4 | Disciplina STA (EnEjecucion) tiene `ranking: []` sin hash | **PASS** |
| 5 | `overall: []` — no hay overall porque STA no finalizó | **PASS** (comportamiento correcto) |

**Resultado A.4:** `PASS`

**Nota:** Requirió workaround manual por BUG-SP4-001 (crear tabla `events` en resultados.db) y BUG-SP4-002 (registrar proyección `competencias_por_torneo` + recalcular ranking P-08).

---

### Caso A.5 — Exportación CSV

```
GET /resultados/ff2ccbea-.../export?format=csv → 200 text/csv
```

| Paso | Check | Resultado |
|------|-------|-----------|
| 1 | GET `?format=csv` → 200 con `Content-Type: text/csv` | **PASS** |
| 2 | Separador `;` | **PASS** |
| 3 | Columnas: `disciplina;posicion;atleta_nombre;categoria;club;ap;rp;tarjeta;penalizaciones;puntos` | **PASS** |
| 4 | 5 atletas DNF con datos coherentes | **PASS** |
| 5 | Abre en Numbers/Excel | **N/A** — no verificado en este UAT |

**Resultado A.5:** `PASS`

---

### Resumen INC-4.6

| Caso | Resultado |
|------|-----------|
| A.1 — Audit log API | PASS |
| A.2 — Audit log UI + control de acceso | PASS |
| A.3 — Hash SHA-256 | PASS |
| A.4 — Export JSON | PASS (con workaround) |
| A.5 — Export CSV | PASS |

**Conclusión INC-4.6:** `PASS` (con 2 bugs ALTA que requieren fix antes de BL-004 y 3 hallazgos UX no bloqueantes)

**Fecha de ejecución INC-4.6:** 2026-04-18

---

## Checklist de Cierre

### Criterios DoD — BL-004

| Área | Criterio | OK |
|------|----------|----|
| INC-4.4 | Grilla precargada visible sin conexión | ☑ |
| INC-4.4 | Performance registrada offline encolada correctamente | ☑ |
| INC-4.4 | Sync automático al reconectar — eventos persistidos en backend | ☑ |
| INC-4.5 | P-10: email de inscripción recibido en inbox real | ☑ |
| INC-4.5 | P-10: idempotencia confirmada (un solo email por inscripción) | ☑ |
| INC-4.5 | P-11: handler implementado y testeado (wiring diferido SP5) | ☑ |
| INC-4.6 | Audit log API: eventos en orden cronológico | ☑ |
| INC-4.6 | Audit log UI: accesible para organizador, bloqueado para juez | ☑ |
| INC-4.6 | Hash SHA-256: presente al finalizar disciplina | ☑ |
| INC-4.6 | Export JSON: estructura correcta con hash en disciplinas cerradas | ☑ |
| INC-4.6 | Export CSV: separador `;`, columnas correctas | ☑ |

### Resultado Final

**UAT SP4:** `PARCIAL — APROBADO CON CONDICIÓN`

Los tres incrementos (INC-4.4, INC-4.5, INC-4.6) pasan funcionalmente. BL-004 puede cerrarse **después de corregir** los dos bugs ALTA detectados durante el UAT.

**Bloqueantes para BL-004:**
- **BUG-SP4-001** — `SQLiteEventStore` no auto-crea tabla `events` en DB nueva → 500 en export en instancia limpia
- **BUG-SP4-002** — Seed no registra proyección `competencias_por_torneo` → export retorna `disciplinas: []`

**Hallazgos no bloqueantes (registrados para SP5):**
- BUG-SP4-003 — Seed crea torneo en EJECUCION; setup N.1 requirió torneo alternativo
- BUG-SP4-004 — Refresh post-sync vacía lista de atletas (recuperable con back navigation)
- UX-SP4-001 — UUIDs expuestos en lista de torneos
- UX-SP4-002 — Nombres de eventos en audit log usan identificadores de código
- UX-SP4-003 — Payload de `AtletaLlamado` no legible para usuario final
- SCOPE-SP4-001 — P-11 callback no conectado (diferido SP5)

**Acciones posteriores requeridas:**
1. Fix BUG-SP4-001: agregar `_ensure_table` en `SQLiteEventStore`
2. Fix BUG-SP4-002: registrar proyección en seed o en `ConfigurarIntervaloOTHandler`
3. DesignReviewer final → PR → merge `develop→main` → tag `v0.5.0` → BL-004

---

## Evidencias

| Artefacto | Ubicación |
|-----------|-----------|
| IDs del seed | `quality/reports/uat/SP4/uat_ids.json` |
| Hallazgos detallados | `quality/reports/uat/SP4/uat-sp4-hallazgos.md` |
| Guion INC-4.4 | `quality/reports/uat/SP4/guion-validacion-inc-4.4.md` |
| Log backend | `/tmp/uvicorn.log` |
| Email P-10 recibido | Inbox vvalotto@gmail.com — 2026-04-18T13:43 |
| DB notificaciones | `data/notificaciones.db` — evento_fuente_id `2f83e1fb-2336-40b2-895c-7b35d1a0061f` |

---

*Plan redactado: 2026-04-17 — US-ADJ-6.7 pre-BL-004*  
*Resultados completados: 2026-04-18 — Victor Valotto*
