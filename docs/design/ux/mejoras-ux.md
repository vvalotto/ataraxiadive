# Mejoras UX — AtaraxiaDive

Registro de ajustes de experiencia de usuario identificados durante el desarrollo y las sesiones de UAT.
Cada entrada incluye el componente afectado, la descripción del problema y la solución propuesta.

---

## Pendientes

### MUX-01 — Paso 5: keypad fuera de la región visible del teléfono

**Componente:** `frontend/src/components/juez/RpSelector.tsx`
**Detectado en:** UAT SP4 — smoke test INC-4.3

El `RpSelector` apila display + 5 presets + 4 botones de ajuste + teclado 3×4. En móvil la suma supera la altura visible y el teclado queda fuera de pantalla.

**Solución propuesta:** compactar padding y gaps internos del componente, especialmente en los botones del keypad (reducir `py-3` → `py-2`, `space-y-4` → `space-y-3`).

---

### MUX-02 — Paso 6: botones de tarjeta sin color identificatorio

**Componente:** `frontend/src/components/juez/StepTarjeta.tsx`
**Detectado en:** UAT SP4 — smoke test INC-4.3

Los tres botones (Blanca, Roja, Amarilla) tienen color idéntico cuando no están seleccionados. Un juez sin experiencia no puede distinguir cuál es cada tarjeta.

**Solución propuesta:** mostrar siempre el color distintivo de cada tarjeta con menor opacidad cuando no está seleccionada, y opacidad plena al seleccionarse:
- Blanca no seleccionada: `border-white/30 bg-white/5` → seleccionada: `border-emerald-300 bg-emerald-400/15`
- Roja no seleccionada: `border-red-300/30 bg-red-500/5` → seleccionada: `border-red-300 bg-red-400/15`
- Amarilla no seleccionada: `border-amber-300/30 bg-amber-400/5` → seleccionada: `border-amber-300 bg-amber-400/15`

---

### MUX-03 — Grilla: el próximo atleta no aparece primero

**Componente:** `frontend/src/pages/juez/GrillaPage.tsx`
**Detectado en:** UAT SP4 — smoke test INC-4.3

La grilla se renderiza en el orden que llega del backend (por `posicion` de competencia). El atleta marcado como `SIGUIENTE` puede estar en cualquier posición de la lista.

**Solución propuesta:** ordenar client-side antes de renderizar según prioridad de estado:
`SIGUIENTE` → `EN_CURSO` → `REVISION` → `PENDIENTE` → `FINALIZADA`

---

### MUX-04 — BKO: campo distanciaBlackout duplicado + bug canSubmitBko ⚠️ REVISADO

**Componente:** `frontend/src/components/juez/StepBKO.tsx`, `frontend/src/hooks/usePerformanceFlow.ts`
**Detectado en:** UAT SP4 — smoke test INC-4.3 / UAT SP4 — ronda 2

**Diseño correcto:** el `RpSelector` de metros permanece en `StepBKO`. La distancia del BKO ES la distancia del selector — no son dos valores distintos. El campo de texto `distanciaBlackout` era el duplicado redundante.

Primera iteración: se eliminó el campo de texto `distanciaBlackout`. Correcto en concepto, pero introdujo una regresión:

**Regresión — Bug:** el botón "Confirmar BKO" nunca se habilita. `canSubmitBko` en `usePerformanceFlow.ts` aún requiere `distanciaBlackout.trim().length > 0`, que ya no se setea desde la UI (el campo fue eliminado).

**Solución propuesta:**
1. Mantener el `RpSelector` en `StepBKO` — el juez ingresa la distancia alcanzada antes del BKO.
2. Corregir `canSubmitBko` en `usePerformanceFlow.ts`: para no-STA, solo requiere `!rpConfirmDisabled && motivoDq.length > 0` (sin chequear `distanciaBlackout`).
3. En `bkoMutation`, derivar `distanciaBlackout` directamente de `metros` dentro de `mutationFn` — no desde estado React (que puede no haberse actualizado aún).

---

### MUX-05 — Pantalla completada: siempre verde aunque la tarjeta sea roja

**Componente:** `frontend/src/pages/juez/PerformanceFlowPage.tsx`
**Detectado en:** UAT SP4 — smoke test INC-4.3

La sección "completada" usa siempre clases `emerald` (verde) sin importar el resultado final de la performance.

**Solución propuesta:** aplicar colores condicionales según `flow.resultKind`:
- Tarjeta roja / BKO → clases `red`
- DNS → clases `slate`
- Tarjeta amarilla → clases `amber`
- Tarjeta blanca / blanca con penalizaciones → clases `emerald`

---

### MUX-06 — Paso 5: AtletaCard completa ocupa espacio del RpSelector

**Componente:** `frontend/src/pages/juez/PerformanceFlowPage.tsx`, `frontend/src/components/juez/AtletaCard.tsx`
**Detectado en:** UAT SP4 — ronda 2

En el paso 5 (ingreso del RP), la `AtletaCard` completa (nombre + AP + andarivel + OT + estado) se muestra sobre el `RpSelector`. En pantalla móvil esto reduce el espacio disponible para el keypad.

**Solución propuesta:** en el paso 5, reemplazar la `AtletaCard` completa por una versión compacta que muestre solo el nombre del atleta y el estado `EN CURSO`, sin los datos auxiliares (AP, andarivel, OT).

---

### MUX-07 — Tarjeta amarilla en revisión: UI demasiado compleja

**Componente:** `frontend/src/components/juez/StepRevision.tsx`
**Detectado en:** UAT SP4 — ronda 2

La pantalla de resolución de tarjeta amarilla (paso 7) muestra la misma estructura compleja que el paso 6. El juez solo necesita decidir entre Blanca y Roja.

**Solución propuesta:**
- Mostrar solo el nombre del atleta con badge `EN REVISIÓN`
- Selector de tarjeta en columna (Blanca / Roja), coloreados sin texto (misma lógica que MUX-02)
- Dos botones únicamente: `VOLVER A LA GRILLA` y `CONFIRMAR RESOLUCIÓN`
- Sin penalizaciones (no aplica en resolución)

---

### MUX-08 — STA: marcas no se muestran en formato mm:ss

**Componente:** `frontend/src/components/juez/AtletaCard.tsx`, `frontend/src/pages/juez/GrillaPage.tsx`
**Detectado en:** UAT SP4 — ronda 2

Las marcas de STA (segundos) se muestran como número crudo (ej: `120 Segundos`) en la grilla y en la `AtletaCard`. El formato correcto es `mm:ss` (ej: `2:00 min`).

**Solución propuesta:** crear una función utilitaria `formatMarca(valor, unidad)` que convierta automáticamente a `mm:ss` cuando `unidad === 'Segundos'`. Aplicarla en `AtletaCard` y en la grilla.

---

## Bugs detectados en UAT

### BUG-01 — INV-DQ-01 se activa erróneamente en BKO para STA

**Componente:** `src/competencia/domain/aggregates/competencia.py` (backend)
**Detectado en:** UAT SP4 — ronda 2 — escenario T-02 (BKO STA)

El invariante INV-DQ-01 exige `distancia_blackout > 0` para cualquier BKO, incluyendo STA. Para STA (apnea estática), no existe desplazamiento — el concepto de `distancia_blackout` no aplica.

**Impacto:** el escenario T-02 no puede completarse. BKO en STA siempre falla con error de dominio.

**Solución propuesta:** condicionar INV-DQ-01 a disciplinas dinámicas. Para STA, permitir `distancia_blackout = None`.

---

## Resueltos

*(vacío — se irán moviendo aquí los ítems una vez implementados)*

---

*Creado: 2026-04-12 — UAT SP4 smoke test INC-4.3*
*Actualizado: 2026-04-12 — UAT SP4 ronda 2: MUX-04 revisado, MUX-06..08 agregados, BUG-01*
