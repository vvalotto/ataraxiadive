# US-6.1.5: AtletaCard Compacta en Paso 5

**Estado**: `Pending`  
**Incremento**: INC-6.1 — Ajustes Juez  
**Hallazgo**: MUX-06  
**Bounded Context**: `competencia`  
**Capas afectadas**: `frontend/components/juez`, `frontend/pages/juez`

---

## Descripción

Como **juez ingresando el RP de un atleta en móvil**,
quiero **que la tarjeta del atleta sea compacta y no ocupe el espacio del teclado**
para **poder ver y usar completamente el selector de marcas sin scroll constante**.

---

## Contexto del Hallazgo

### MUX-06 — AtletaCard completa ocupa espacio del RpSelector

**Ubicación**: `frontend/src/components/juez/AtletaCard.tsx` · `frontend/src/pages/juez/PerformanceFlowPage.tsx`

En el paso 5 (ingreso del RP), la `AtletaCard` completa se muestra sobre el `RpSelector`. La tarjeta incluye: nombre + AP + andarivel + OT + estado. En pantalla móvil esto reduce drásticamente el espacio disponible para el keypad.

**Impacto**: En móvil (viewport < 812px), el keypad es invisible sin scroll; ralentiza la entrada de datos.

---

## Especificación

### Tarea 1: Crear variante compacta de AtletaCard

| | |
|---|---|
| **Precondición** | AtletaCard siempre muestra todos los campos (nombre, AP, andarivel, OT, estado) |
| **Postcondición** | Variante `compact: true` muestra solo nombre + estado "EN CURSO"; AP, andarivel, OT quedan ocultos |
| **Invariante** | El componente acepta prop `variant='compact' | 'full'`; default es `'full'` |

```tsx
// Estructura nueva de AtletaCard.tsx:
interface AtletaCardProps {
  atleta: Atleta;
  variant?: 'full' | 'compact'; // default 'full'
  estado?: string;
}

export const AtletaCard: React.FC<AtletaCardProps> = ({
  atleta,
  variant = 'full',
  estado = 'PENDIENTE',
}) => {
  if (variant === 'compact') {
    return (
      <div className="rounded-lg border border-gray-200 bg-white p-3">
        <p className="text-sm font-semibold text-gray-900">{atleta.nombre}</p>
        <span className="inline-block mt-1 px-2 py-1 bg-blue-100 text-blue-900 text-xs rounded">
          {estado}
        </span>
      </div>
    );
  }

  // Variante full (actual):
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-lg font-bold text-gray-900">{atleta.nombre}</p>
      <div className="mt-3 space-y-2 text-sm">
        <p><span className="text-gray-600">AP:</span> {formatMarca(atleta.ap, atleta.unidad)}</p>
        <p><span className="text-gray-600">Andarivel:</span> {atleta.andarivel}</p>
        <p><span className="text-gray-600">OT:</span> {formatTime(atleta.ot_programado)}</p>
        <span className="inline-block px-2 py-1 bg-blue-100 text-blue-900 text-xs rounded">
          {estado}
        </span>
      </div>
    </div>
  );
};
```

### Tarea 2: Usar variante compacta en paso 5 del flujo

| | |
|---|---|
| **Precondición** | PerformanceFlowPage usa `<AtletaCard />` sin prop `variant` en todos los pasos |
| **Postcondición** | Paso 5 (RpSelector) usa `<AtletaCard variant="compact" />` |
| **Invariante** | Otros pasos (4, 6, 7) continúan usando variante `'full'` |

```tsx
// En PerformanceFlowPage.tsx:
{step === 4 && (
  <>
    <AtletaCard variant="compact" estado={flow.estado} />
    <StepMarca {...marksProps} />
  </>
)}

{step === 5 && (
  <>
    <AtletaCard variant="compact" estado="EN CURSO" />
    <StepRpSelector {...rpSelectorProps} />
  </>
)}

{step === 6 && (
  <>
    <AtletaCard variant="full" estado={flow.estado} />
    <StepTarjeta {...tarjetaProps} />
  </>
)}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.1.5 — AtletaCard compacta en paso 5

  Scenario: AtletaCard variant="compact" muestra solo nombre + estado
    Given una AtletaCard renderizada con variant="compact"
    When se renderiza el componente
    Then aparece solo el nombre del atleta
    And aparece el estado (ej: "EN CURSO")
    And NO aparecen: AP, andarivel, OT

  Scenario: AtletaCard variant="full" muestra todos los campos
    Given una AtletaCard renderizada con variant="full"
    When se renderiza el componente
    Then aparecen: nombre, AP, andarivel, OT, estado
    And la tarjeta tiene estilo expandido

  Scenario: AtletaCard default es variant="full"
    Given una AtletaCard sin prop variant
    When se renderiza el componente
    Then muestra todos los campos (comportamiento anterior)

  Scenario: Paso 5 usa variante compacta
    Given un juez en paso 5 (RpSelector) en iPhone 12
    When se renderiza PerformanceFlowPage
    Then la AtletaCard es compacta (solo nombre + estado)
    And el RpSelector ocupa más espacio vertical
    And el keypad es completamente visible sin scroll

  Scenario: Otros pasos usan variante completa
    Given un juez en pasos 4, 6, 7
    When se renderiza PerformanceFlowPage
    Then la AtletaCard muestra todos los campos
```

---

## Notas de implementación

- **Paso 4 vs Paso 5**: Aclaración — ¿paso 4 es `StepMarca` o `RpSelector`? Ajustar según configuración actual en `PerformanceFlowPage`.
- **Altura estimada**: Variante `full` ≈ 120px; variante `compact` ≈ 60px — ganancia de ~60px para RpSelector.
- **Testing**: Validar que la altura total (AtletaCard compacta + RpSelector) < 812px en iPhone 12.
- **No regresión**: Todos los pasos excepto 5 deben continuar con variante full.

---

## Referencias

- Hallazgo: `docs/design/ux/mejoras-ux.md` — MUX-06
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.1
- Componentes: `frontend/src/components/juez/AtletaCard.tsx` · `frontend/src/pages/juez/PerformanceFlowPage.tsx`

---

*Redactado: 2026-05-03 — SP6 INC-6.1*
