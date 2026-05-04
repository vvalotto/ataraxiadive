# US-6.1.4: Rediseño Inicio Juez + STA mm:ss + Tarjeta Amarilla Simplificada

**Estado**: `Pending`  
**Incremento**: INC-6.1 — Ajustes Juez  
**Hallazgos**: UI-JUE-01 · MUX-08 · MUX-07  
**Bounded Context**: `competencia` · `identidad`  
**Capas afectadas**: `frontend/pages/juez`, `frontend/components/juez`, `frontend/utils`

---

## Descripción

Como **juez accediendo al portal**,
quiero **que la pantalla de inicio muestre mis asignaciones organizadas claramente, las marcas de STA en formato legible (mm:ss), y que la revisión de tarjeta amarilla sea un proceso simplificado**
para **concentrarme en la competencia sin distracciones ni confusiones de formato**.

---

## Contexto del Hallazgo

### UI-JUE-01 — Inicio confuso + información dispersa

**Ubicación**: `frontend/src/pages/juez/HomePage.tsx`

Elementos a cambiar:
1. "Mis disciplinas" → renombrar a "Mis asignaciones" (más preciso)
2. Datos del torneo (nombre, fecha, sede) deben aparecer PRIMERO antes de las asignaciones
3. Botón "Password" no debería estar en la página principal
4. Header confuso — "En línea" debería ser subtítulo de "Mis asignaciones", no encabezado global

### MUX-08 — STA marcas sin formato mm:ss

**Ubicación**: `frontend/src/components/juez/AtletaCard.tsx` · `frontend/src/pages/juez/GrillaPage.tsx`

Las marcas de STA (segundos) se muestran como número crudo (ej: `120 Segundos`) en la grilla y en la `AtletaCard`. El formato correcto es `mm:ss` (ej: `2:00 min`).

**Impacto**: Difícil lectura — los jueces están acostumbrados a `mm:ss` en apnea estática.

### MUX-07 — UI tarjeta amarilla demasiado compleja

**Ubicación**: `frontend/src/components/juez/StepRevision.tsx`

La pantalla de resolución de tarjeta amarilla (paso 7) muestra la misma estructura compleja que el paso 6 (asignar tarjeta). El juez solo necesita decidir entre Blanca y Roja.

**Solución**: Simplificar a un formulario mínimo con solo nombre + estado "EN REVISIÓN" + dos botones de tarjeta + dos botones de acción.

---

## Especificación

### Tarea 1: Rediseño página inicio juez

| | |
|---|---|
| **Precondición** | HomePage actual muestra componentes sin jerarquía clara; "Mis disciplinas" es confuso |
| **Postcondición** | HomePage nueva: Datos torneo (primero) → Mis asignaciones (con header "En línea") → sin botón Password |
| **Invariante** | Todos los links a torneo/disciplina siguen funcionando |

**Estructura nueva de HomePage.tsx**:
```tsx
<Container>
  {/* SECCIÓN 1: Datos del torneo */}
  <section className="mb-6">
    <h2 className="text-xl font-bold">{torneo.nombre}</h2>
    <p className="text-sm text-gray-600">{formatDate(torneo.fecha_inicio)} · {torneo.sede}</p>
  </section>

  {/* SECCIÓN 2: Mis asignaciones */}
  <section>
    <div className="flex items-center justify-between mb-4">
      <h3 className="text-lg font-semibold">Mis asignaciones</h3>
      <span className="text-xs text-green-600">En línea</span>
    </div>
    {/* listar disciplinas asignadas */}
  </section>

  {/* Eliminar: botón Password */}
</Container>
```

### Tarea 2: Crear función utilitaria `formatMarca(valor, unidad)`

| | |
|---|---|
| **Precondición** | Marcas STA se muestran como número crudo (ej: "120 Segundos") |
| **Postcondición** | Marcas STA formateadas a `mm:ss` (ej: "2:00 min"); marcas dinámicas sin cambios |
| **Invariante** | Funciona para cualquier valor en segundos; no pierde precisión decimal |

```typescript
// utils/formatMarca.ts
export const formatMarca = (valor: number, unidad: string): string => {
  if (unidad === 'Segundos') {
    const minutes = Math.floor(valor / 60);
    const seconds = Math.round((valor % 60) * 100) / 100; // preservar 2 decimales
    return `${minutes}:${seconds.toString().padStart(5, '0')} min`;
  }
  // Para metros (dinámicas): devolver como está
  return `${valor.toFixed(1)} m`;
};

// Ejemplo:
formatMarca(120, 'Segundos') // "2:00.00 min"
formatMarca(75.5, 'Metros')  // "75.5 m"
```

Aplicar en:
- `AtletaCard.tsx` — línea que muestra el AP (Announced Performance)
- `GrillaPage.tsx` — si muestra marcas en columnas

### Tarea 3: Simplificar UI tarjeta amarilla (StepRevision)

| | |
|---|---|
| **Precondición** | StepRevision muestra estructura completa como StepTarjeta (display, presets, ajustes, penalizaciones) |
| **Postcondición** | StepRevision simplificada: nombre atleta + estado "EN REVISIÓN" + dos botones tarjeta (Blanca/Roja) coloreados + dos botones acción |
| **Invariante** | La resolución guarda solo tarjeta (Blanca o Roja) sin penalizaciones; UI refleja que es una decisión binaria |

```tsx
// Estructura nueva de StepRevision.tsx:
export const StepRevision = ({ atleta, onResolve }) => {
  const [selectedCard, setSelectedCard] = useState<'blanca' | 'roja' | null>(null);

  return (
    <div className="space-y-6">
      {/* Identificación */}
      <div>
        <p className="text-sm text-gray-600">Atleta</p>
        <p className="text-xl font-bold">{atleta.nombre}</p>
        <span className="inline-block mt-2 px-3 py-1 bg-amber-100 text-amber-900 text-xs rounded">
          EN REVISIÓN
        </span>
      </div>

      {/* Selector tarjeta — solo Blanca y Roja */}
      <div className="space-y-2">
        <p className="text-sm font-semibold">¿Cuál es tu resolución?</p>
        <div className="flex gap-3">
          {/* Botón Blanca */}
          <button
            onClick={() => setSelectedCard('blanca')}
            className={`flex-1 py-3 px-4 rounded border-2 transition
              ${selectedCard === 'blanca'
                ? 'border-emerald-300 bg-emerald-400/15 ring-2 ring-emerald-300'
                : 'border-white/30 bg-white/5'}`}
          >
            BLANCA
          </button>
          {/* Botón Roja */}
          <button
            onClick={() => setSelectedCard('roja')}
            className={`flex-1 py-3 px-4 rounded border-2 transition
              ${selectedCard === 'roja'
                ? 'border-red-300 bg-red-400/15 ring-2 ring-red-300'
                : 'border-red-300/30 bg-red-500/5'}`}
          >
            ROJA
          </button>
        </div>
      </div>

      {/* Botones acción */}
      <div className="flex gap-3">
        <button
          onClick={() => onResolve(null)}
          className="flex-1 py-2 px-4 bg-gray-200 text-gray-800 rounded"
        >
          VOLVER A LA GRILLA
        </button>
        <button
          onClick={() => onResolve(selectedCard)}
          disabled={!selectedCard}
          className="flex-1 py-2 px-4 bg-blue-600 text-white rounded disabled:opacity-50"
        >
          CONFIRMAR RESOLUCIÓN
        </button>
      </div>
    </div>
  );
};
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.1.4 — Rediseño inicio + STA mm:ss + tarjeta amarilla

  Scenario: HomePage muestra datos torneo primero
    Given un juez logueado en un torneo
    When accede a la página de inicio
    Then aparece: Nombre del torneo | Fecha | Sede
    And debajo: "Mis asignaciones" con disciplinas asignadas
    And no hay botón de Password

  Scenario: formatMarca convierte STA a mm:ss
    Given una marca STA de 120 segundos
    When se llama a formatMarca(120, 'Segundos')
    Then retorna "2:00.00 min"

  Scenario: formatMarca preserva marcas dinámicas
    Given una marca dinámica de 75.5 metros
    When se llama a formatMarca(75.5, 'Metros')
    Then retorna "75.5 m"

  Scenario: AtletaCard muestra STA en mm:ss
    Given un atleta con AP de 90 segundos en STA
    When se renderiza AtletaCard
    Then muestra "AP: 1:30.00 min" (no "90 Segundos")

  Scenario: StepRevision solo muestra Blanca y Roja
    Given un juez en paso de revisión (tarjeta amarilla)
    When se renderiza StepRevision
    Then aparecen solo dos botones: Blanca | Roja
    And no hay campos de distancia, presets ni penalizaciones

  Scenario: StepRevision deshabilitada sin selección
    Given StepRevision sin tarjeta seleccionada
    When se intenta confirmar sin seleccionar
    Then el botón "CONFIRMAR RESOLUCIÓN" está deshabilitado

  Scenario: StepRevision guarda resolución como Blanca o Roja
    Given un juez selecciona "BLANCA" y confirma
    When se envía la resolución
    Then el backend recibe { tarjeta_final: 'BLANCA', sin_penalizaciones: true }
```

---

## Notas de implementación

- **formatMarca**: Ubicar en `frontend/src/utils/formatMarca.ts` — reutilizable en toda la app
- **Testing**: Verificar que `formatMarca` maneja edge cases (0 segundos, valores fraccionarios, etc.)
- **HomePage**: Mantener links a disciplinas activos tras rediseño
- **StepRevision**: Eliminar componentes `RpSelector`, `PenalizacionesSelector` de este paso
- **CSS**: Reutilizar colores y estilos de buttons de `StepTarjeta.tsx` para consistencia

---

## Referencias

- Hallazgo: `docs/design/ux/mejoras-ux.md` — UI-JUE-01 · MUX-08 · MUX-07
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.1
- Componentes: `frontend/src/pages/juez/HomePage.tsx` · `frontend/src/components/juez/AtletaCard.tsx` · `frontend/src/components/juez/StepRevision.tsx`

---

*Redactado: 2026-05-03 — SP6 INC-6.1*
