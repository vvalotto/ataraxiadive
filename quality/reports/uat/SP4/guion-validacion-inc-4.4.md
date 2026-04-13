# Guión de Validación UAT — INC-4.4 (US-4.4.1, US-4.4.2, US-4.4.3)

**Fecha:** 2026-04-13  
**Entorno:** local  
**Frontend:** `http://localhost:5173`  
**Backend:** `http://localhost:8000`  
**Usuario juez:** `juez@uat-sp4.test`  
**Password:** `juezsp4uat2025`

---

## 1. Preparación

1. Verificar backend arriba en `http://localhost:8000/health`.
2. Verificar frontend arriba en `http://localhost:5173`.
3. Iniciar sesión con el usuario juez.
4. Confirmar que aparecen disciplinas `DNF` y `STA`.

**Resultado preparación:** `PASS`  
**Notas:**  

---

## 2. US-4.4.1 — Precarga y lectura offline

### Caso 2.1 — Precarga online
1. Con conexión activa, abrir `DNF` desde Mis disciplinas.
2. Entrar a Grilla.

**Esperado:** grilla visible sin error.

**Resultado:** `PASS`  
**Evidencia (captura/nota):**

### Caso 2.2 — Offline con cache existente
1. Con la misma disciplina ya abierta, desactivar red (modo offline).
2. Volver a Grilla DNF.

**Esperado:** grilla visible + aviso de modo offline.

**Resultado:** `PASS`  
**Evidencia (captura/nota):**

### Caso 2.3 — Offline sin cache
1. En un navegador/dispositivo limpio (o limpiando datos del sitio), mantener offline.
2. Abrir una disciplina nunca precargada.

**Esperado:** mensaje “Sin datos disponibles. Conectate a internet para cargar la disciplina por primera vez.”

**Resultado:** `FAIL`  
**Evidencia (captura/nota):*queda en cargando grilla...*

---

## 3. US-4.4.2 — Flujo offline con cola local

### Caso 3.1 — Flujo completo offline
1. Mantener dispositivo offline.
2. En DNF, abrir atleta pendiente.
3. Ejecutar flujo: `LLAMAR` -> `Registrar resultado` -> `Asignar tarjeta`.
4. Volver a Grilla.

**Esperado:** estado optimista aplicado + indicador `⏳` de pendientes.

**Resultado:** `FAIL`  
**Evidencia (captura/nota):* No pasa del Paso 1, no cambia de estado*

### Caso 3.2 — DNS offline
1. Elegir otro atleta pendiente en modo offline.
2. Ejecutar `DNS — NO SE PRESENTA`.
3. Volver a Grilla.

**Esperado:** atleta en DNS optimista + pendiente de sync.

**Resultado:** `PASS / FAIL`  
**Evidencia (captura/nota):**

---

## 4. US-4.4.3 — Sincronización automática al reconectar

### Caso 4.1 — Reconexión y sync
1. Con pendientes acumulados, volver a online.
2. Observar badge en header.

**Esperado:**
- aparece `↻ Sincronizando`,
- luego `✓ Sincronizado` (breve),
- desaparecen pendientes cuando la cola queda en 0.

**Resultado:** `PASS / FAIL`  
**Evidencia (captura/nota):**

### Caso 4.2 — Estado final consistente
1. Revisar grilla luego de sincronizar.
2. Confirmar que estados finales coinciden con acciones realizadas offline.

**Esperado:** datos consistentes post-sync (sin regresiones visibles).

**Resultado:** `PASS / FAIL`  
**Evidencia (captura/nota):**

---

## 5. Resumen Final

| US | Resultado | Observaciones |
|----|-----------|---------------|
| US-4.4.1 | `PASS / FAIL` | |
| US-4.4.2 | `PASS / FAIL` | |
| US-4.4.3 | `PASS / FAIL` | |

**Conclusión general INC-4.4:** `PASS / FAIL`  
**Bloqueantes detectados:**  
**Acciones posteriores requeridas:**  

