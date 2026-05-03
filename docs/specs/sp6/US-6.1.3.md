# US-6.1.3: Grilla Ordenada por Estado + Keypad Visible en Móvil

**Estado**: `Pending`  
**Incremento**: INC-6.1 — Ajustes Juez  
**Hallazgos**: MUX-03 · MUX-01  
**Bounded Context**: `competencia`  
**Capas afectadas**: `frontend/pages/juez`, `frontend/components/juez`

---

## Descripción

Como **juez observando la grilla de competencia**,
quiero **que el siguiente atleta a juzgar aparezca siempre en la posición de arriba, y que el teclado de ingreso de marcas sea completamente visible en móvil**
para **ejecutar el flujo rápidamente sin desplazamientos innecesarios**.

---

## Contexto del Hallazgo

### MUX-03 — Grilla sin ordenamiento por estado

**Ubicación**: `frontend/src/pages/juez/GrillaPage.tsx`

La grilla se renderiza en el orden que llega del backend (por `posicion` de competencia). El atleta con estado `SIGUIENTE` puede estar en cualquier posición de la lista.

**Impacto**: El juez debe buscar en la grilla quién es el siguiente atleta; en tournaments grandes (30+ atletas), esto es tedioso.

### MUX-01 — Keypad fuera de región visible en móvil

**Ubicación**: `frontend/src/components/juez/RpSelector.tsx`

El `RpSelector` apila: display + 5 presets + 4 botones de ajuste + teclado 3×4. En móvil, la suma supera la altura visible (viewport < 812px) y el teclado queda fuera de pantalla.

**Impacto**: En móvil, el juez no puede ver los botones del keypad sin scroll; dificulta el ingreso de marcas en campo.

---

## Especificación

### Tarea 1: Ordenar grilla client-side por estado

| | |
|---|---|
| **Precondición** | Grilla renderizada en orden del backend (por `posicion` de competencia) |
| **Postcondición** | Grilla reordenada client-side antes de renderizar según prioridad de estado |
| **Invariante** | El orden es: `SIGUIENTE` → `EN_CURSO` → `REVISION` → `PENDIENTE` → `FINALIZADA`; dentro de cada estado, mantener orden original |

```typescript
// En GrillaPage.tsx, función de ordenamiento:
const sortPerformancesByState = (performances: Performance[]) => {
  const stateOrder = {
    SIGUIENTE: 0,
    EN_CURSO: 1,
    REVISION: 2,
    PENDIENTE: 3,
    FINALIZADA: 4,
  };

  return [...performances].sort((a, b) => {
    const orderA = stateOrder[a.estado] ?? 999;
    const orderB = stateOrder[b.estado] ?? 999;
    return orderA - orderB;
  });
};

// Aplicar antes de renderizar:
const sortedPerfs = sortPerformancesByState(grilla.performances);
```

### Tarea 2: Compactar RpSelector para móvil

| | |
|---|---|
| **Precondición** | `RpSelector` ocupa demasiado espacio vertical en viewport < 812px |
| **Postcondición** | Keypad completamente visible sin scroll en iPhone 12 (812px height) y menores |
| **Invariante** | Funcionalidad idéntica; solo reducidos padding/gaps internos |

Cambios en `RpSelector.tsx`:
- Reducir `py-3` → `py-2` en botones del keypad
- Reducir `space-y-4` → `space-y-2` entre secciones (display, presets, keypad)
- Reducir `gap-2` → `gap-1` en grid del keypad (3×4)
- Mantener `text-sm` o `text-xs` para números del keypad si es necesario

```tsx
// Antes:
<div className="space-y-4">
  <div className="...">Display</div>
  <div className="space-y-2">Presets (5 botones)</div>
  <div className="space-y-3">Ajustes (4 botones)</div>
  <div className="grid grid-cols-3 gap-2">Keypad 3×4</div>
</div>

// Después:
<div className="space-y-2">
  <div className="...">Display</div>
  <div className="space-y-1">Presets (5 botones py-2)</div>
  <div className="space-y-2">Ajustes (4 botones py-2)</div>
  <div className="grid grid-cols-3 gap-1">Keypad 3×4 (py-2)</div>
</div>
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.1.3 — Grilla ordenada + Keypad visible

  Scenario: Grilla renderizada con SIGUIENTE en primer lugar
    Given una competencia con performances en varios estados
    When se carga GrillaPage
    Then el atleta con estado SIGUIENTE aparece en la primera fila
    And el segundo atleta tiene estado EN_CURSO o PENDIENTE (según disponibilidad)

  Scenario: Dentro de SIGUIENTE, mantener orden original
    Given dos atletas con estado SIGUIENTE
    When se ordena la grilla
    Then el orden relativo entre ambos es el del backend (por posicion)

  Scenario: Orden final respeta prioridad de estados
    Given performances con estados: FINALIZADA, SIGUIENTE, EN_CURSO, REVISION, PENDIENTE
    When se renderiza GrillaPage
    Then el orden es: [SIGUIENTE, EN_CURSO, REVISION, PENDIENTE, FINALIZADA]

  Scenario: RpSelector visible en iPhone 12 (812px height)
    Given un juez con iPhone 12 abriendo RpSelector en paso 4
    When se renderiza el componente
    Then todos los botones del keypad son visibles sin scroll vertical
    And el bottom del botón más bajo está a menos de 812px

  Scenario: RpSelector compactado sin perder funcionalidad
    Given cambios de padding y gaps en RpSelector
    When se ingresa una marca (ej: 75.5 metros)
    Then la marca se registra correctamente
    And los presets funcionan igual
```

---

## Notas de implementación

- **Performance**: El ordenamiento client-side es O(n log n) — aceptable para grillas < 200 atletas
- **Testing**: Validar en múltiples breakpoints: iPhone 12 mini (780px), SE (667px), iPad (1024px)
- **No scroll**: Usar `overflow-hidden` en `RpSelector` si es necesario para forzar el comportamiento
- **Accesibilidad**: Mantener suficiente padding para TAP targets (mínimo 44×44px en móvil)

---

## Referencias

- Hallazgo: `docs/design/ux/mejoras-ux.md` — MUX-03 · MUX-01
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.1
- Componentes: `frontend/src/pages/juez/GrillaPage.tsx` · `frontend/src/components/juez/RpSelector.tsx`

---

*Redactado: 2026-05-03 — SP6 INC-6.1*
