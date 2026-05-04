# US-6.1.1: Fix BUG canSubmitBko + Corrección Secuencia Tarjeta→Marca

**Estado**: `Pending`  
**Incremento**: INC-6.1 — Ajustes Juez  
**Hallazgos**: MUX-04 · UI-JUE-02  
**Bounded Context**: `competencia`  
**Capas afectadas**: `frontend/hooks`, `frontend/components/juez`, `domain/aggregates` (validación)

---

## Descripción

Como **juez ejecutando una performance**,
quiero **que el flujo de competencia tenga una secuencia correcta de pasos y que el botón "Confirmar BKO" se habilite apropiadamente**
para **poder finalizar una performance incluso en caso de BKO sin fricciones**.

---

## Contexto del Bug

### MUX-04 — Bug: canSubmitBko nunca se habilita

**Ubicación**: `frontend/src/hooks/usePerformanceFlow.ts` + `frontend/src/components/juez/StepBKO.tsx`

El `RpSelector` permanece en `StepBKO`. La distancia del BKO ES la distancia del selector — no son dos valores distintos. El campo de texto `distanciaBlackout` fue eliminado en una iteración anterior, pero `canSubmitBko` aún chequea `distanciaBlackout.trim().length > 0`, que ya no se setea desde la UI.

**Regresión**: El botón "Confirmar BKO" nunca se habilita porque la condición es imposible de cumplir.

### UI-JUE-02 — Secuencia incorrecta del flujo

**Ubicación**: `frontend/src/pages/juez/PerformanceFlowPage.tsx`

Orden actual: `inicializar` → `RpSelector` → `tarjeta` → `marca` → `confirmar`

Orden correcto: `inicializar` → `RpSelector` → `confirmar marca` → `asignar tarjeta` → `confirmar`

El juez debe confirmar la marca antes de asignar una tarjeta, para que ambos datos sean definitivos cuando se guarden.

---

## Especificación

### Tarea 1: Corregir lógica canSubmitBko

| | |
|---|---|
| **Precondición** | En `usePerformanceFlow.ts`, `canSubmitBko` requiere un campo `distanciaBlackout` que no existe en estado React |
| **Postcondición** | `canSubmitBko` verifica solo: `!rpConfirmDisabled && motivoDq.length > 0` (para no-STA); para STA: solo `motivoDq.length > 0` |
| **Invariante** | Derivar `distanciaBlackout` en `bkoMutation.mutationFn` directamente de `metros` (state), no desde estado React |

```typescript
// En usePerformanceFlow.ts:
const canSubmitBko = 
  isDisciplinaSTA 
    ? motivoDq.length > 0
    : !rpConfirmDisabled && motivoDq.length > 0;

// En bkoMutation.mutationFn:
const bkoPayload = {
  distancia_blackout: metros, // derivar desde el state actual
  motivo_dq: motivoDq,
  ...
};
```

### Tarea 2: Reordenar secuencia del flujo

| Concepto | Descripción |
|---|---|
| **Precondición** | Secuencia actual (Paso 4→5→6→7): Performance → **confirmar marca** → **asignar tarjeta** → revisión |
| **Postcondición** | Nueva secuencia (Paso 4→5→6→7): Performance → **asignar tarjeta** → **confirmar marca** → revisión |
| **Invariante** | Una vez asignada la tarjeta, se confirma la marca; ambos datos son definitivos al guardar |

Cambios en `PerformanceFlowPage.tsx`:
1. **Paso 5:** mover `StepTarjeta` (hoy en Paso 6)
2. **Paso 6:** mover RpSelector + "CONFIRMAR MARCA" (hoy en Paso 5)
3. El contenido de ambos pasos se intercambia — no cambia la lógica, solo el orden visual

### Tarea 3: Validación BKO en STA

| | |
|---|---|
| **Precondición** | INV-DQ-01 en `competencia/domain/aggregates` requiere `distancia_blackout > 0` para cualquier BKO |
| **Postcondición** | Para STA (apnea estática), permitir `distancia_blackout = None`; para dinámicas, exigir `> 0` |
| **Invariante** | Todos los tests BKO dinámicos y STA pasan sin violación de invariantes |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.1.1 — Fix BUG canSubmitBko + Secuencia tarjeta→marca

  Scenario: BKO en disciplina dinámica habilita botón al ingresar distancia + motivo
    Given un juez en paso BKO de una performance dinámico (ej: DYN)
    When ingresa un valor de distancia en RpSelector (ej: 50 metros)
    And selecciona un motivo de descalificación (ej: BKO_SUPERFICIE)
    Then el botón "Confirmar BKO" se habilita
    And al clickearlo, la mutation envía { distancia_blackout: 50, motivo_dq: "BKO_SUPERFICIE" }

  Scenario: BKO en STA no requiere distancia
    Given un juez en paso BKO de una performance STA
    When selecciona un motivo de descalificación
    Then el botón "Confirmar BKO" se habilita sin necesidad de ingresar distancia
    And la mutation envía { distancia_blackout: None, motivo_dq: "..." }

  Scenario: Secuencia correcta: Performance → asignar tarjeta → confirmar marca
    Given un flujo iniciado en una performance nueva
    When el juez termina la performance y asigna la tarjeta
    Then se pasa a confirmar la marca / RP (paso 6)
    And la tarjeta no puede editarse de nuevo

  Scenario: Asignar tarjeta antes que marca preserva datos
    Given tarjeta asignada y marca confirmada
    When se guarda la performance
    Then el backend recibe { ..., tarjeta: [asignada], rp: [confirmada] } en orden correcto
```

---

## Notas de implementación

- **Dependencias**: Requiere validación de INV-DQ-01 en el agregado `Competencia` que permita BKO sin distancia en STA
- **Testing**: UAT sobre móvil y desktop — verificar que el keypad de RpSelector sea accesible en ambos pasos
- **Merge order**: Este US debe completarse antes de cualquier UAT del rol juez (INC-6.1 es bloqueante para validación)

---

## Referencias

- Hallazgo: `docs/design/ux/mejoras-ux.md` — MUX-04 · MUX-08 (BUG-01 STA distancia)
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.1
- Agregado: `src/competencia/domain/aggregates/competencia.py` — `INV-DQ-01`

---

*Redactado: 2026-05-03 — SP6 INC-6.1*
