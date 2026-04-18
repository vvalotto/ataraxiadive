# Plan de Pruebas UAT — INC-4.4 Offline-first

**Versión:** 4.0 (iPhone como juez + iPad como Remote Web Inspector)  
**Fecha:** 2026-04-18  
**Entorno:** local (WiFi local)  
**Frontend:** `http://192.168.0.28:5173`  
**Backend:** `http://192.168.0.28:8000`  
**Usuario juez:** `juez@uat-sp4.test` / `juezsp4uat2025`  
**Dispositivo principal:** iPhone (Safari iOS) — rol juez  
**Dispositivo secundario:** iPad (Safari iPadOS, conectado al Mac por USB) — Remote Web Inspector para casos 1.4, 2.3 y 3.3

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

## Cómo verificar el estado — iPhone y iPad

**iPhone (juez):** toda la verificación es **por comportamiento observable en la UI**:  
**iPad (Remote Web Inspector):** permite inspeccionar IndexedDB directamente desde Mac — úsalo para los casos 1.4, 2.3 y 3.3.

| Lo que querías ver en DevTools | Cómo verificarlo en iPhone |
|-------------------------------|---------------------------|
| IndexedDB `grilla_cache` tiene datos | Grilla visible en modo offline sin pantalla vacía |
| `cached_at` reciente | Aviso de la app "Datos actualizados hace X min" |
| `comando_queue` tiene N registros | Badge ⏳ N en el header de la app |
| Comando con `estado: 'error'` | Badge ⚠ Error (1) en el header |
| Cola vacía tras sync | Badge ✓ Sincronizado → desaparece |
| `navigator.onLine` = false | Banner offline de la app + WiFi desactivado en Configuración |

### Cómo simular offline en iPhone

**Método principal — WiFi:**
1. `Configuración` → `WiFi` → apagar el switch
2. Para volver: `Configuración` → `WiFi` → encender

**Método alternativo — Modo Avión:**
1. Centro de Control → tap en el ícono de avión  
2. Para volver: mismo tap para desactivar

> **Nota:** Modo Avión también corta Bluetooth. Si el backend está en la misma red WiFi, cualquier método funciona. Lo que importa es que el iPhone no pueda llegar a `192.168.0.28`.

### Remote Web Inspector — con iPad (recomendado para casos avanzados)

Usar el iPad (conectado al Mac por USB) para los casos 1.4, 2.3 y 3.3 que requieren editar o inspeccionar IndexedDB.

**Setup (una sola vez):**
1. iPad: `Configuración` → `Safari` → `Avanzado` → activar `Inspector Web`
2. Conectar iPad al Mac por USB
3. Mac: `Safari` → menú `Desarrollar` → `[nombre del iPad]` → `http://192.168.0.28:5173`
4. Pestaña `Almacenamiento` → `IndexedDB` → `AtaraxiaDiveDB`

> **¿Por qué iPad y no iPhone?** El iPad tiene pantalla más grande — más cómodo para inspeccionar IndexedDB mientras el iPhone ejecuta el flujo del juez. Ambos tienen el mismo procedimiento de conexión.

**Si solo tenés el iPhone disponible:** mismos pasos con iPhone en lugar de iPad.

---

## Preparación del entorno

### Verificación inicial (desde iPhone — rol juez)

1. Abrir Safari → `http://192.168.0.28:5173` → página de login visible
2. Login con `juez@uat-sp4.test` / `juezsp4uat2025`
3. Verificar que aparecen disciplinas **DNF** y **STA** en "Mis disciplinas"
4. Confirmar que no hay badge ⏳ ni ⚠ en el header (no hay cola residual)

> Si hay badge residual de una sesión anterior: usar Remote Web Inspector para limpiar `AtaraxiaDiveDB`, o pedir al tester desktop que limpie la IndexedDB.

**Resultado preparación:** `PASS / FAIL`

### Datos de prueba disponibles

- **DNF:** atletas `e02`, `e03`, `e04`, `e05`, `e06` → estado `AnunciadaAP`
- **STA:** atletas `t01`, `t02`, `t03` → estado `AnunciadaAP`

---

## US-4.4.1 — Precarga y lectura offline

### Caso 1.1 — Precarga online (happy path)

**Precondición:** iPhone online (WiFi conectado al mismo router que `192.168.0.28`). Sin cache previo.

1. Tocar **DNF** en Mis disciplinas → abrir GrillaPage.
2. Verificar que la grilla carga con atletas visibles.
3. Salir de GrillaPage (volver a Mis disciplinas).

**Esperado:**
- Grilla visible con atletas (carga desde servidor).
- Sin aviso de modo offline ni de cache expirado.
- Sin badge ⏳ en el header.

**Resultado:** `PASS`  
**Evidencia:** OkP

---

### Caso 1.2 — Lectura offline con cache válido

**Precondición:** Caso 1.1 ejecutado. **No reiniciar Safari.**

1. `Configuración` → `WiFi` → **apagar**.
2. Volver a Safari → Mis disciplinas → tocar **DNF**.
3. Observar la grilla y el aviso de estado.

**Esperado:**
- Grilla visible (datos del cache local, no del servidor).
- Banner o aviso: **"Modo offline. Datos actualizados hace X min"** (INV-4.4.1-01).
- No hay pantalla vacía ni error de red.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 1.3 — Offline sin cache previo

**Precondición:** WiFi ya apagado. Limpiar la cache de la app (Remote Web Inspector → borrar `AtaraxiaDiveDB`) O usar STA (disciplina no visitada antes → sin cache).

1. Con WiFi **apagado**, en Mis disciplinas → tocar **STA**.

**Esperado:**
- GrillaPage muestra: **"Sin datos disponibles. Conectate a internet para cargar la disciplina por primera vez."** (INV-4.4.1-02).
- No queda bloqueado en "Cargando grilla...".
- No pantalla vacía.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 1.4 — Cache antiguo (> 24h) con red disponible

**Precondición:** iPad conectado al Mac con Remote Web Inspector habilitado (ver setup arriba).

> **Si no tenés iPad disponible:** saltar este caso o marcarlo como N/A.

1. En Remote Web Inspector del iPad → `AtaraxiaDiveDB` → `grilla_cache` → editar `cached_at` a `Date.now() - 25*3600*1000`.
   > El iPad debe estar abriendo la misma URL `http://192.168.0.28:5173` en Safari para que aparezca en el menú Desarrollar del Mac.
2. `Configuración` → `WiFi` → **encender**.
3. Volver a GrillaPage DNF.

**Esperado:**
- Grilla se actualiza desde el servidor (INV-4.4.1-03).
- No aparece aviso de expiración (cache se refrescó).

> **Variante sin editar cache:** mantener offline con cache de 25h → debe aparecer aviso de antigüedad pero mostrar la grilla igualmente.

**Resultado:** `PASS / FAIL / N/A`  
**Evidencia:**

---

## US-4.4.2 — Flujo offline con cola local

> **Preparación:** volver a **online** (WiFi encendido). Abrir GrillaPage DNF para asegurar cache actualizado. Luego apagar WiFi.

### Caso 2.1 — Flujo completo offline

**Precondición:** WiFi **apagado**, DNF precargado (Caso 1.1 ejecutado), atleta `e02` en estado `AnunciadaAP`.

1. En GrillaPage DNF, tocar atleta `e02`.
2. **Paso 1:** tocar **LLAMAR ATLETA**.
   - Verificar: UI avanza al Paso 2.
   - Verificar: badge ⏳ aparece en el header (≥ 1).
3. **Paso 2:** tocar **CONTINUAR**.
4. **Paso 3:** tocar **INICIAR VENTANA OT** → tocar **ATLETA INICIA**.
5. **Paso 4:** tocar **FINALIZAR PERFORMANCE**.
6. **Paso 5:** ingresar RP (ej: metros=72, cm=00) → tocar **CONFIRMAR MARCA**.
   - Verificar: badge muestra ⏳ 2.
7. **Paso 6:** seleccionar **Tarjeta Blanca** → tocar confirmar.
   - Verificar: badge muestra ⏳ 3.
8. Tocar **SIGUIENTE ATLETA** → volver a GrillaPage.

**Esperado:**
- UI avanza por todos los pasos sin error (INV-4.4.2-01).
- Badge muestra **⏳ 3** al finalizar (3 comandos: llamar + resultado + tarjeta).
- Atleta `e02` aparece en grilla con estado **FINALIZADA** (INV-4.4.2-03).
- `pendingCount` en el badge del header refleja 3.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 2.2 — DNS offline

**Precondición:** WiFi **apagado**, atleta `e03` en `AnunciadaAP`.

1. En GrillaPage DNF, tocar atleta `e03`.
2. **Paso 1:** tocar **LLAMAR ATLETA**.
3. **Paso 2:** tocar **DNS — NO SE PRESENTA**.
4. Volver a GrillaPage.

**Esperado:**
- UI muestra confirmación de DNS y botón "SIGUIENTE ATLETA".
- Badge aumenta en 2 (llamar + dns para `e03`).
- Atleta `e03` aparece como **FINALIZADA** con badge ⏳ en grilla.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 2.3 — Badge ⏳ acumulativo y FIFO

**Precondición:** tras Casos 2.1 y 2.2, la cola tiene ≥ 5 comandos. WiFi **apagado**.

1. Observar el badge en el header: debe mostrar el total acumulado (⏳ 5 o más).
2. Navegar a GrillaPage y volver a Mis disciplinas → el badge se mantiene en todas las pantallas.
3. (Con iPad + Remote Web Inspector): verificar que `comando_queue` está ordenada por `id` ascendente, y el primero es `tipo: 'llamar'` de `e02`.

**Esperado:**
- Badge muestra **⏳ N** con el total correcto (INV-4.4.2-02).
- Badge visible en todas las pantallas del juez.
- (Opcional) Orden FIFO confirmado en IndexedDB.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

## US-4.4.3 — Sincronización automática al reconectar

> **Precondición de toda la sección:** Casos 2.1 y 2.2 ejecutados — ≥ 5 comandos encolados, badge muestra ⏳ N.

### Caso 3.1 — Sincronización exitosa al reconectar

1. Verificar que el badge muestra **⏳ N pendientes**.
2. `Configuración` → `WiFi` → **encender**.
3. Volver rápidamente a Safari y observar el header durante los siguientes 5 segundos.

**Esperado:**
- En ≤ 2s aparece **↻ Sincronizando** (INV-4.4.3-01).
- Badge transiciona a **✓ Sincronizado** cuando la cola queda en 0.
- Badge desaparece después de ~3 segundos.
- No queda badge ⏳ ni ⚠.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 3.2 — Estado final consistente post-sync

**Precondición:** Caso 3.1 ejecutado exitosamente.

1. Navegar a GrillaPage DNF.
2. Observar el estado de `e02` y `e03`.

**Esperado:**
- `e02` en estado **FINALIZADA** (tarjeta blanca asignada).
- `e03` en estado **FINALIZADA** (DNS).
- No hay badge de pendientes.
- Los estados coinciden con lo que se registró offline (INV-4.4.3-06).

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

### Caso 3.3 — Error 4xx en comando de cola

**Preparación — crear conflicto (dos opciones):**

**Opción A (desde Mac, Postman/curl):**
```bash
# Obtener token
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"juez@uat-sp4.test","password":"juezsp4uat2025"}'

# Avanzar e04 directamente en el servidor
curl -X POST http://localhost:8000/competencia/{dnf_id}/llamar \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"participante_id":"e04","disciplina":"DNF"}'
```

**Opción B (más simple — solo observar):** si algún comando de la cola fue rechazado con 409 durante el sync del Caso 3.1, observar el badge ⚠.

1. Con WiFi **apagado**, intentar llamar `e04` desde la UI (su estado en cache es `AnunciadaAP` pero en el servidor ya fue avanzado).
2. Encender WiFi y observar la sincronización.

**Esperado:**
- Badge muestra **⚠ Error (1)** (INV-4.4.3-03).
- Al tocar el badge, se muestra el mensaje de error del servidor.
- Los comandos **siguientes** en la cola **no** se envían (cola pausada).

**Resultado:** `PASS / FAIL / N/A`  
**Evidencia:**

---

### Caso 3.4 — Badge visible en todas las pantallas del juez

**Precondición:** tener ≥ 1 comando encolado (repetir inicio de Caso 2.1 si es necesario).

1. Navegar entre: **Mis disciplinas** → **GrillaPage** → **PerformanceFlowPage** → volver.
2. Verificar que el badge ⏳ es visible en el header en todas las pantallas (INV-4.4.3-05).

**Esperado:**
- Badge visible y consistente en todas las rutas del juez.
- El contador no se resetea al cambiar de pantalla.

**Resultado:** `PASS / FAIL`  
**Evidencia:**

---

## Resumen Final

| US | Caso | Resultado | Observaciones |
|----|------|-----------|---------------|
| US-4.4.1 | 1.1 Precarga online | `PASS / FAIL` | |
| US-4.4.1 | 1.2 Offline + cache válido | `PASS / FAIL` | |
| US-4.4.1 | 1.3 Offline sin cache | `PASS / FAIL` | usar STA si no hay Remote Inspector |
| US-4.4.1 | 1.4 Cache > 24h | `PASS / FAIL / N/A` | iPad + Remote Web Inspector para editar cached_at |
| US-4.4.2 | 2.1 Flujo completo offline | `PASS / FAIL` | iPhone |
| US-4.4.2 | 2.2 DNS offline | `PASS / FAIL` | iPhone |
| US-4.4.2 | 2.3 Badge acumulativo + FIFO | `PASS / FAIL` | FIFO verificable con iPad + Remote Web Inspector |
| US-4.4.3 | 3.1 Sync al reconectar | `PASS / FAIL` | iPhone — encender WiFi y observar badge |
| US-4.4.3 | 3.2 Estado final consistente | `PASS / FAIL` | iPhone |
| US-4.4.3 | 3.3 Error 4xx en cola | `PASS / FAIL / N/A` | Opción A (curl desde Mac) + observar en iPhone |
| US-4.4.3 | 3.4 Badge en todas las pantallas | `PASS / FAIL` | |

**Conclusión general INC-4.4:** `PASS / FAIL`  
**Bloqueantes detectados:**  
**Acciones posteriores requeridas:**  
**Fecha de ejecución:**  
**Ejecutado por:** Victor Valotto  
**Dispositivo principal (juez):** iPhone (Safari iOS)  
**Dispositivo secundario (Remote Web Inspector):** iPad (Safari iPadOS)
