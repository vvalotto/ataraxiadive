# Plan de Pruebas UAT — INC-4.4 Offline-first

**Versión:** 2.0 (post-fix networkMode + refactor calidad)  
**Fecha:** 2026-04-13  
**Entorno:** local  
**Frontend:** `http://localhost:5173`  
**Backend:** `http://localhost:8000`  
**Usuario juez:** `juez@uat-sp4.test` / `juezsp4uat2025`

---

## Contexto

INC-4.4 implementa operación offline-first para el juez. Las tres US tienen dependencia secuencial:

- **US-4.4.1** — Precarga en IndexedDB (Dexie.js): la grilla se guarda localmente al abrir la disciplina
- **US-4.4.2** — Flujo de 6 pasos sin conexión: los comandos se encolan en IndexedDB
- **US-4.4.3** — Sincronización automática: al reconectar, la cola se envía al servidor en orden FIFO

### Invariantes críticos a verificar

| ID | Invariante |
|----|-----------|
| INV-4.4.1-01 | `usePrecarga` corre siempre al montar GrillaPage, online u offline |
| INV-4.4.1-02 | Sin cache + sin conexión → error explícito (no pantalla vacía) |
| INV-4.4.1-03 | Cache > 24h → aviso de antigüedad, datos se usan igual |
| INV-4.4.2-01 | Offline → todos los comandos van a la cola IndexedDB |
| INV-4.4.2-02 | Cola FIFO estricto (orden por `id` autoincremental) |
| INV-4.4.2-03 | Grilla refleja estado optimista de comandos encolados |
| INV-4.4.3-01 | Sync arranca en ≤ 2s al reconectar |
| INV-4.4.3-02 | Comandos procesados en orden FIFO |
| INV-4.4.3-03 | Error 4xx → comando marcado `error`, cola pausada |
| INV-4.4.3-04 | Error 5xx/red → hasta 3 reintentos con backoff 1s/2s/4s |
| INV-4.4.3-06 | Cola vacía → grilla se re-sincroniza con el servidor |

---

## Preparación del entorno

### Arranque

```bash
# Terminal 1 — backend
uv run uvicorn src.app:app --reload --env-file .env

# Terminal 2 — frontend
cd frontend && npm run dev
```

### Verificación inicial

1. `GET http://localhost:8000/health` → `{"status": "ok"}`
2. Abrir `http://localhost:5173` → página de login visible
3. Login con `juez@uat-sp4.test` / `juezsp4uat2025`
4. Verificar que aparecen disciplinas **DNF** y **STA** en "Mis disciplinas"
5. Abrir DevTools → Application → IndexedDB → confirmar que `AtaraxiaDiveDB` no tiene datos (o limpiarla si tiene residuos de sesiones anteriores)

**Resultado preparación:** `PASS / FAIL`

### Cómo simular offline en Chrome

- **DevTools → Network → throttling** → seleccionar `Offline`
- Para volver online: seleccionar `No throttling`
- **Alternativa:** DevTools → Application → Service Workers → marcar `Offline`

> **Nota:** el badge de conexión del browser NO es suficiente. Usar `navigator.onLine` en consola para confirmar.

---

## US-4.4.1 — Precarga y lectura offline

### Caso 1.1 — Precarga online (happy path)

**Precondición:** dispositivo online, sin cache previo en IndexedDB.

1. Tocar **DNF** en Mis disciplinas → abrir GrillaPage.
2. Verificar que la grilla carga desde el servidor.
3. Ir a DevTools → Application → IndexedDB → `AtaraxiaDiveDB` → `grilla_cache`.
4. Confirmar que existe un registro para `(competencia_dnf_id, DNF)` con `cached_at` reciente.

**Esperado:**
- Grilla visible con atletas.
- Registro en `grilla_cache` con `cached_at` de hace menos de 1 minuto.
- Sin aviso de modo offline ni de cache expirado.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 1.2 — Lectura offline con cache válido

**Precondición:** Caso 1.1 ejecutado (grilla cacheada). **No limpiar datos.**

1. En DevTools → Network → seleccionar **Offline**.
2. Recargar la página o navegar fuera y volver a GrillaPage DNF.
3. Observar la grilla y el aviso de estado.

**Esperado:**
- Grilla visible (datos del cache, no del servidor).
- Aviso visible: **"Modo offline. Datos actualizados hace X min"** (INV-4.4.1-01).
- No hay error de red visible.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 1.3 — Offline sin cache previo *(antes FAIL, ahora fix aplicado)*

**Precondición:** limpiar IndexedDB (`AtaraxiaDiveDB` → click derecho → Delete database), mantener offline.

1. Con dispositivo **offline**, navegar a Mis disciplinas → tocar **STA**.

**Esperado:**
- GrillaPage muestra el mensaje: **"Sin datos disponibles. Conectate a internet para cargar la disciplina por primera vez."** (INV-4.4.1-02).
- No queda bloqueado en "Cargando grilla...".
- No pantalla vacía.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 1.4 — Cache antiguo (> 24h) con red disponible

**Precondición:** modificar manualmente el `cached_at` del registro de grilla_cache en DevTools → Application → IndexedDB → editar el valor a `Date.now() - 25*3600*1000` (25 horas atrás). Volver a online.

1. Con dispositivo **online**, abrir GrillaPage DNF.

**Esperado:**
- Grilla se actualiza desde el servidor (INV-4.4.1-03).
- El `cached_at` en IndexedDB se actualiza al timestamp actual.
- **No** aparece aviso de expiración (el cache se refrescó).

> **Variante con red cortada:** si se mantiene offline con cache de 25h, debe aparecer aviso de antigüedad pero mostrar la grilla igualmente.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

## US-4.4.2 — Flujo offline con cola local

> **Preparación:** volver a **online**, abrir GrillaPage DNF para asegurar cache actualizado. Luego poner **offline**.

### Caso 2.1 — Flujo completo offline *(antes FAIL, ahora fix aplicado)*

**Precondición:** dispositivo **offline**, DNF precargado, atleta `e01` en estado `AnunciadaAP`.

1. En GrillaPage DNF, tocar atleta `e01`.
2. **Paso 1:** tocar **LLAMAR ATLETA**.
   - Verificar: UI avanza a Paso 2.
   - Verificar en DevTools → IndexedDB → `comando_queue`: 1 registro `{tipo: 'llamar', estado: 'pendiente'}`.
3. **Paso 2:** tocar **CONTINUAR**.
4. **Paso 3:** tocar **INICIAR VENTANA OT** → tocar **ATLETA INICIA**.
5. **Paso 4:** tocar **FINALIZAR PERFORMANCE**.
6. **Paso 5:** ingresar RP (ej: metros=72, cm=00) → tocar **CONFIRMAR MARCA**.
   - Verificar: IndexedDB → 2 registros (`llamar` + `resultado`).
7. **Paso 6:** seleccionar **Tarjeta Blanca** → tocar confirmar.
   - Verificar: IndexedDB → 3 registros (`llamar`, `resultado`, `tarjeta`).
8. Tocar **SIGUIENTE ATLETA** → volver a GrillaPage.

**Esperado:**
- UI avanza por todos los pasos sin error (INV-4.4.2-01).
- 3 comandos en `comando_queue` con `estado: 'pendiente'`.
- Atleta `e01` aparece en grilla con estado `FINALIZADA` y badge **⏳ 3** (INV-4.4.2-03).
- `pendingCount` en el badge del header refleja 3.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 2.2 — DNS offline

**Precondición:** dispositivo **offline**, atleta `e02` en `AnunciadaAP`.

1. En GrillaPage DNF, tocar atleta `e02`.
2. **Paso 1:** tocar **LLAMAR ATLETA**.
3. **Paso 2:** tocar **DNS — NO SE PRESENTA**.
4. Volver a GrillaPage.

**Esperado:**
- UI muestra confirmación de DNS y botón "SIGUIENTE ATLETA".
- IndexedDB → `comando_queue`: registros `llamar` + `dns` para `e02`.
- Atleta `e02` aparece como **FINALIZADA** con badge ⏳ en grilla.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 2.3 — Badge ⏳ acumulativo y FIFO

**Precondición:** tras Casos 2.1 y 2.2, la cola tiene ≥ 5 comandos. Dispositivo **offline**.

1. Verificar en `comando_queue`: los comandos están ordenados por `id` ascendente.
2. Verificar que el primer comando es `{tipo: 'llamar'}` para `e01` (el primero encolado).
3. Confirmar que el badge del header muestra el total acumulado de pendientes.

**Esperado:**
- Orden FIFO en IndexedDB (INV-4.4.2-02).
- Badge muestra `⏳ N` con el total correcto.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

## US-4.4.3 — Sincronización automática al reconectar

> **Precondición de toda la sección:** ejecutar Casos 2.1 y 2.2 para tener ≥ 5 comandos encolados.

### Caso 3.1 — Sincronización exitosa al reconectar

1. Verificar que el badge muestra **⏳ N pendientes**.
2. En DevTools → Network → cambiar a **No throttling** (volver a online).
3. Observar el header durante los siguientes 5 segundos.

**Esperado:**
- En ≤ 2s aparece **↻ Sincronizando** (INV-4.4.3-01).
- Badge transiciona a **✓ Sincronizado** cuando la cola queda en 0.
- Badge desaparece después de ~3 segundos.
- `comando_queue` en IndexedDB queda vacía.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 3.2 — Estado final consistente post-sync

**Precondición:** Caso 3.1 ejecutado exitosamente.

1. Navegar a GrillaPage DNF.
2. Observar el estado de `e01` y `e02`.
3. Verificar contra el servidor: `GET /competencia/{dnf_id}/grilla?disciplina=DNF`.

**Esperado:**
- `e01` en estado **FINALIZADA** (tarjeta blanca asignada) en la grilla.
- `e02` en estado **FINALIZADA** (DNS) en la grilla.
- Los estados coinciden con la respuesta del servidor (INV-4.4.3-06).
- No hay badge de pendientes.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 3.3 — Error 4xx en comando de cola

**Preparación:** crear una situación de conflicto. Opción más simple: con el dispositivo **online**, ejecutar manualmente `POST /competencia/{dnf_id}/llamar` para `e03` desde Postman/curl para avanzar su estado. Luego poner **offline**, intentar llamar `e03` desde la UI (estado ya no es AnunciadaAP en el servidor pero sí en cache local), volver **online**.

> **Alternativa práctica:** simplemente verificar este caso observando los logs del backend si el servidor rechaza un comando con 409.

1. Con comandos que generen 409 al sincronizar, reconectar.
2. Observar el badge.

**Esperado:**
- Badge muestra **⚠ Error (1)** (INV-4.4.3-03).
- Al tocar el badge, se muestra el mensaje de error del servidor.
- Los comandos **siguientes** en la cola **no** se envían (cola pausada).
- En IndexedDB → el comando en error tiene `estado: 'error'` y `error_mensaje` del servidor.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 3.4 — Badge visible en todas las pantallas del juez

**Precondición:** tener ≥ 1 comando encolado.

1. Navegar entre: **Mis disciplinas** → **GrillaPage** → **PerformanceFlowPage** → volver.
2. Verificar que el badge ⏳ / ↻ / ✓ es visible en el header en todas las pantallas (INV-4.4.3-05).

**Esperado:**
- `SyncStatusBadge` visible en header en todas las rutas de `JuezLayout`.
- El contador es consistente entre pantallas.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

## Resumen Final

| US | Caso | Resultado | Observaciones |
|----|------|-----------|---------------|
| US-4.4.1 | 1.1 Precarga online | `PASS / FAIL` | |
| US-4.4.1 | 1.2 Offline + cache válido | `PASS / FAIL` | |
| US-4.4.1 | 1.3 Offline sin cache | `PASS / FAIL` | fix networkMode |
| US-4.4.1 | 1.4 Cache > 24h | `PASS / FAIL` | |
| US-4.4.2 | 2.1 Flujo completo offline | `PASS / FAIL` | fix networkMode |
| US-4.4.2 | 2.2 DNS offline | `PASS / FAIL` | |
| US-4.4.2 | 2.3 Badge acumulativo + FIFO | `PASS / FAIL` | |
| US-4.4.3 | 3.1 Sync al reconectar | `PASS / FAIL` | |
| US-4.4.3 | 3.2 Estado final consistente | `PASS / FAIL` | |
| US-4.4.3 | 3.3 Error 4xx en cola | `PASS / FAIL` | |
| US-4.4.3 | 3.4 Badge en todas las pantallas | `PASS / FAIL` | |

**Conclusión general INC-4.4:** `PASS / FAIL`  
**Bloqueantes detectados:**  
**Acciones posteriores requeridas:**  
**Fecha de ejecución:**  
**Ejecutado por:** Victor Valotto
