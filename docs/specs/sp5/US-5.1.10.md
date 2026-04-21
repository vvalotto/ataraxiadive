# US-5.1.10: Corregir acciones de fase en AccionesPanel

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1-ADJ
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/components/organizador/AccionesPanel.tsx`

---

## Descripción

Como **organizador**,
quiero ver solo las acciones que corresponden a la fase actual del torneo
para **no ver "Iniciar Ejecución" cuando el torneo ya está en ejecución**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Componente | `AccionesPanel` | Muestra acciones de transición de fase del torneo |
| Mapa | `ACCIONES_POR_ESTADO` | `Partial<Record<EstadoTorneo, AccionFase[]>>` |
| Estado `EJECUCION` | acción esperada | `Iniciar premiacion` (no `Iniciar ejecucion`) |

### Hallazgo UAT origen

- **UAT-5.1-04:** El torneo `UAT SP4 — Flujo de Performance` está en `EJECUCION`. El panel muestra `Iniciar Ejecución` en lugar de la acción de avanzar hacia `PREMIACION`.

### Diagnóstico

Al revisar `AccionesPanel.tsx`, el mapa `ACCIONES_POR_ESTADO[EJECUCION]` ya tiene definidas las acciones correctas:
```typescript
EJECUCION: [
  { label: 'Volver a preparacion', run: volverPreparacion, variant: 'secondary' },
  { label: 'Iniciar premiacion', run: iniciarPremiacion, variant: 'primary' },
],
```

El bug no está en el mapa sino en que el valor de `estado` recibido por `AccionesPanel` no coincide con `'EJECUCION'` como string exacto. Posibles causas:
1. El backend devuelve `"En ejecución"` o `"EJECUCION"` con otro formato.
2. `fetchTorneo` no mapea correctamente el campo `estado`.
3. El torneo afectado tiene un estado guardado antes de que se normalizara el enum.

Esta US debe verificar la causa exacta y aplicar el fix correspondiente.

---

## Especificación del comportamiento

### Invariantes

- **INV-5.1.10-01:** `AccionesPanel` con `estado === 'EJECUCION'` muestra solo `Volver a preparacion` e `Iniciar premiacion`. Nunca muestra `Iniciar ejecucion`.
- **INV-5.1.10-02:** `AccionesPanel` con `estado === 'PREPARACION'` muestra solo `Iniciar ejecucion`. Nunca muestra `Iniciar premiacion`.
- **INV-5.1.10-03:** El campo `estado` que llega a `AccionesPanel` coincide exactamente con los valores de `EstadoTorneo`.

### Investigación y fix requeridos

1. Hacer `console.log(estado)` en `AccionesPanel` con el torneo afectado para confirmar el valor real recibido.
2. Comparar con `GET /torneos/{id}` en backend: verificar campo y formato del `estado` retornado.
3. Si hay mismatch de string, corregirlo en `fetchTorneo` o en el tipo `EstadoTorneo`.
4. Si el torneo tiene estado inconsistente en DB, documentar como dato corrupto y verificar si el backend acepta `EJECUCION` como valor canónico.

### Operación principal

| | Descripción |
|---|---|
| **Precondición** | `AccionesPanel` recibe `estado: EstadoTorneo` con valor `'EJECUCION'` |
| **Postcondición** | Se renderizan las acciones `Volver a preparacion` e `Iniciar premiacion`; `Iniciar ejecucion` no aparece |

**Ejemplo concreto:**

```
GET /torneos/T1 → { estado: "EJECUCION", ... }

AccionesPanel con estado="EJECUCION":
  ✓ botón "Volver a preparacion" (secondary)
  ✓ botón "Iniciar premiacion" (primary)
  ✗ botón "Iniciar ejecucion" — NO debe aparecer
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.10 — Acciones correctas de fase en AccionesPanel

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR

  Scenario: torneo en EJECUCION muestra Iniciar premiacion, no Iniciar ejecucion
    Given el torneo T1 está en estado EJECUCION
    When el organizador navega a la página de detalle de T1
    Then AccionesPanel muestra "Iniciar premiacion"
    And AccionesPanel muestra "Volver a preparacion"
    And AccionesPanel NO muestra "Iniciar ejecucion"

  Scenario: torneo en PREPARACION muestra Iniciar ejecucion
    Given el torneo T1 está en estado PREPARACION
    When el organizador navega a la página de detalle de T1
    Then AccionesPanel muestra "Iniciar ejecucion"
    And AccionesPanel NO muestra "Iniciar premiacion"

  Scenario: acción Iniciar premiacion ejecuta transición exitosa
    Given el torneo T1 está en estado EJECUCION
    When el organizador hace click en "Iniciar premiacion"
    Then el backend recibe POST /torneos/T1/iniciar-premiacion
    And el torneo recarga en estado PREMIACION
    And AccionesPanel muestra "Cerrar torneo"

  Scenario: campo estado del torneo llega como string exacto del enum
    Given el backend devuelve { estado: "EJECUCION" } para el torneo T1
    When fetchTorneo(T1) resuelve
    Then el valor de estado es exactamente el string "EJECUCION"
    And coincide con la clave del mapa ACCIONES_POR_ESTADO
```

---

## Impacto arquitectónico

- [x] No — corrección en `AccionesPanel` y/o `fetchTorneo`. Sin cambios de dominio.

**Capa(s) afectadas:**
- [x] Frontend — `AccionesPanel.tsx`: verificar condición de renderizado por estado
- [x] Frontend — `api/torneo.ts`: verificar que `fetchTorneo` retorna `estado` normalizado como `EstadoTorneo`

---

## Notas de implementación

- Verificar con `GET /torneos/{id}` en swagger/curl qué valor exacto devuelve el campo `estado` para un torneo en ejecución.
- `ACCIONES_POR_ESTADO` en `AccionesPanel.tsx` línea 19 ya tiene el mapa correcto. El fix probable es en el mapping de la respuesta HTTP.
- Si el dato en DB es inconsistente (torneo creado antes de que se normalizara el enum), evaluar reset de fixture de prueba — no es un bug del código sino del seed.

---

## Referencias

- Hallazgo UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md` §UAT-5.1-04
- Plan: `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md §US-5.1.10`
- Código fuente: `frontend/src/components/organizador/AccionesPanel.tsx` línea 19
- Código fuente: `frontend/src/api/torneo.ts` — `fetchTorneo`

---

*Redactado: 2026-04-21 — INC-5.1-ADJ ajuste post-UAT panel organizador*