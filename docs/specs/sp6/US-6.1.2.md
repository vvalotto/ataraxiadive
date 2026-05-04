# US-6.1.2: Colores Tarjeta + Pantalla Completada Según Resultado

**Estado**: `Pending`  
**Incremento**: INC-6.1 — Ajustes Juez  
**Hallazgos**: MUX-02 · MUX-05  
**Bounded Context**: `competencia`  
**Capas afectadas**: `frontend/components/juez`, `frontend/pages/juez`

---

## Descripción

Como **juez seleccionando una tarjeta**,
quiero **poder identificar visualmente cada tarjeta (Blanca, Roja, Amarilla) incluso cuando no está seleccionada, y ver que la pantalla de completada refleje el resultado final**
para **reducir errores de selección y confirmar visualmente el resultado de la performance**.

---

## Contexto del Hallazgo

### MUX-02 — Botones de tarjeta sin color identificatorio

**Ubicación**: `frontend/src/components/juez/StepTarjeta.tsx`

Los tres botones (Blanca, Roja, Amarilla) tienen color idéntico cuando no están seleccionados. Un juez sin experiencia no puede distinguir cuál es cada tarjeta hasta hover o click.

**Impacto**: Decisiones más lentas, posibles errores en móvil donde no hay hover visible.

### MUX-05 — Pantalla completada siempre verde

**Ubicación**: `frontend/src/pages/juez/PerformanceFlowPage.tsx`

La sección "completada" usa siempre clases `emerald` (verde) sin importar el resultado final (`resultKind`).

**Impacto**: Confusión visual — una performance roja (descalificada) se muestra con colores verdes.

---

## Especificación

### Tarea 1: Aplicar colores distintivos a botones de tarjeta (no seleccionados)

| | |
|---|---|
| **Precondición** | Botones de tarjeta sin color cuando no están seleccionados |
| **Postcondición** | Cada botón muestra su color distintivo con opacidad reducida cuando no seleccionado, opacidad plena cuando seleccionado |
| **Invariante** | El color no interfiere con la legibilidad del texto; el estado seleccionado es claramente distinguible |

```tsx
// Estilos para StepTarjeta.tsx:

// Blanca
<button className={`
  ${!isBlancaSelected 
    ? 'border-white/30 bg-white/5' 
    : 'border-emerald-300 bg-emerald-400/15 ring-2 ring-emerald-300'}
  // ... resto de clases
`}>
  BLANCA
</button>

// Roja
<button className={`
  ${!isRojaSelected 
    ? 'border-red-300/30 bg-red-500/5' 
    : 'border-red-300 bg-red-400/15 ring-2 ring-red-300'}
  // ...
`}>
  ROJA
</button>

// Amarilla
<button className={`
  ${!isAmarilaSelected 
    ? 'border-amber-300/30 bg-amber-400/5' 
    : 'border-amber-300 bg-amber-400/15 ring-2 ring-amber-300'}
  // ...
`}>
  AMARILLA
</button>
```

### Tarea 2: Aplicar colores condicionales a pantalla completada

| | |
|---|---|
| **Precondición** | `PerformanceFlowPage` siempre usa clases `emerald` en la sección completada |
| **Postcondición** | Colores reflejan `flow.resultKind`: Roja/BKO → `red`, DNS → `slate`, Amarilla → `amber`, Blanca/Penalizaciones → `emerald` |
| **Invariante** | El color de la pantalla completada coincide con el resultado guardado en la performance |

```tsx
// En PerformanceFlowPage.tsx:
const getCompletionColorClasses = () => {
  switch (flow.resultKind) {
    case 'tarjeta_roja':
    case 'bko':
      return 'bg-red-50 border-red-300';
    case 'dns':
      return 'bg-slate-50 border-slate-300';
    case 'tarjeta_amarilla':
      return 'bg-amber-50 border-amber-300';
    case 'tarjeta_blanca':
    case 'tarjeta_blanca_penalizaciones':
    default:
      return 'bg-emerald-50 border-emerald-300';
  }
};

// Aplicar en el div de completada:
<div className={`rounded-lg border-2 p-4 ${getCompletionColorClasses()}`}>
  {/* contenido */}
</div>
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.1.2 — Colores tarjeta + pantalla completada

  Scenario: Botones tarjeta con colores distintivos no seleccionados
    Given el paso 5 (asignar tarjeta) en pantalla
    When se renderiza StepTarjeta
    Then los tres botones tienen colores distintivos:
      | Botón | Color no seleccionado | Color seleccionado |
      | Blanca | border-white/30 bg-white/5 | border-emerald-300 bg-emerald-400/15 |
      | Roja | border-red-300/30 bg-red-500/5 | border-red-300 bg-red-400/15 |
      | Amarilla | border-amber-300/30 bg-amber-400/5 | border-amber-300 bg-amber-400/15 |

  Scenario: Pantalla completada refleja color según resultado
    Given una performance completada con tarjeta roja
    When se llega a la pantalla final
    Then la sección completada usa clases de color rojo (bg-red-50 border-red-300)

  Scenario: BKO muestra color rojo en pantalla completada
    Given una performance completada con BKO
    When se renderiza PerformanceFlowPage en estado completed
    Then la sección usa clases de color rojo (mismo que tarjeta_roja)

  Scenario: DNS muestra color pizarra (slate)
    Given una performance con estado DNS (Did Not Start)
    When se renderiza pantalla completada
    Then la sección usa clases slate (bg-slate-50 border-slate-300)

  Scenario: Tarjeta amarilla muestra color ámbar
    Given una performance completada con tarjeta amarilla (revisión)
    When se renderiza pantalla completada
    Then la sección usa clases ámbar (bg-amber-50 border-amber-300)

  Scenario: Tarjeta blanca / blanca con penalizaciones muestra verde
    Given una performance completada con tarjeta blanca
    When se renderiza pantalla completada
    Then la sección usa clases emerald (bg-emerald-50 border-emerald-300)
```

---

## Notas de implementación

- **CSS Framework**: Usar Tailwind v4 con convenciones existentes (opacity, ring rings)
- **Testing**: Validar en móvil (iPhone 12/14) que los colores sean distinguibles incluso con glare
- **Accesibilidad**: Asegurar suficiente contraste entre background y texto según WCAG AA
- **Testing visual**: Incluir screenshots de antes/después en el commit

---

## Referencias

- Hallazgo: `docs/design/ux/mejoras-ux.md` — MUX-02 · MUX-05
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.1
- Componentes: `frontend/src/components/juez/StepTarjeta.tsx` · `frontend/src/pages/juez/PerformanceFlowPage.tsx`

---

*Redactado: 2026-05-03 — SP6 INC-6.1*
