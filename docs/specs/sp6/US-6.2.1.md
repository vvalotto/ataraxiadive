# US-6.2.1: Inicio Organizador — Ordenar Torneos por Fecha + Mostrar Fecha

**Estado**: `Done`
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-01  
**Bounded Context**: `frontend`  
**Capas afectadas**: `frontend/pages/organizador/DashboardPage.tsx`

---

## Descripción

Como **organizador en la pantalla de inicio**,
quiero **ver los torneos ordenados por fecha de inicio y con la fecha visible en cada tarjeta**
para **identificar rápidamente el próximo torneo sin tener que abrir cada uno**.

---

## Contexto del Hallazgo

### UI-ORG-01 — Torneos sin orden ni fecha visible

**Ubicación**: `frontend/src/pages/organizador/DashboardPage.tsx`

La función `filtrarTorneos` filtra por estado (vigentes/histórico) pero no aplica ningún ordenamiento. Las tarjetas muestran: nombre, sede, ciudad y estado — pero omiten `fecha_inicio` y `fecha_fin`, que ya están disponibles en el DTO (`TorneoDto.fecha_inicio: string`, `TorneoDto.fecha_fin: string`).

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md` — navegación y estructura base del portal organizador.
- `docs/design/ux/prototipos/prototipo-organizador.html` — prototipo navegable aprobado para el rol organizador.
- `docs/plans/sp6/PLAN-SP6.md` — hallazgo UI-ORG-01 detectado en validación SP5.
- `frontend/src/pages/organizador/DashboardPage.tsx` — implementación React actual comparada contra el hallazgo.

---

## Especificación

### Tarea 1: Ordenar torneos por fecha de inicio

| | |
|---|---|
| **Precondición** | `filtrarTorneos` retorna los torneos en el orden que llegan del backend, sin orden definido |
| **Postcondición** | Los torneos se ordenan por `fecha_inicio` descendente (más próximo primero) dentro de cada filtro |
| **Invariante** | El orden aplica tanto al filtro "Vigentes" como "Histórico"; torneos con misma fecha mantienen el orden relativo del backend |

```typescript
// En DashboardPage.tsx:
function filtrarTorneos(torneos: TorneoDto[], filtro: FiltroTorneos): TorneoDto[] {
  const filtrados = filtro === 'vigentes'
    ? torneos.filter((t) => esTorneoVigente(t.estado))
    : torneos.filter((t) => esTorneoHistorico(t.estado))
  return filtrados.sort((a, b) => b.fecha_inicio.localeCompare(a.fecha_inicio))
}
```

### Tarea 2: Mostrar fecha en la tarjeta

| | |
|---|---|
| **Precondición** | La tarjeta muestra `sede.nombre, sede.ciudad · estado` pero no la fecha |
| **Postcondición** | La tarjeta muestra la fecha de inicio en formato legible (ej: `1 dic 2025`) junto a los datos existentes |
| **Invariante** | Si `fecha_inicio === fecha_fin`, mostrar solo una fecha; si difieren, mostrar rango (`1–3 dic 2025`) |

```typescript
// Función helper:
function formatFechaTorneo(inicio: string, fin: string): string {
  // fecha_inicio y fecha_fin llegan como "YYYY-MM-DD"
  const ini = new Date(inicio + 'T00:00:00')
  const end = new Date(fin + 'T00:00:00')
  const fmt = (d: Date) =>
    d.toLocaleDateString('es-AR', { day: 'numeric', month: 'short', year: 'numeric' })
  if (inicio === fin) return fmt(ini)
  return `${ini.toLocaleDateString('es-AR', { day: 'numeric', month: 'short' })}–${fmt(end)}`
}

// En la tarjeta (bajo la línea de sede/estado):
<p className={`mt-1 text-xs ${historicalTextClass(torneo.estado)}`}>
  {formatFechaTorneo(torneo.fecha_inicio, torneo.fecha_fin)}
</p>
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.2.1 — Ordenar torneos por fecha + mostrar fecha en inicio organizador

  Scenario: Torneos vigentes ordenados por fecha descendente
    Given el organizador tiene torneos vigentes con distintas fechas de inicio
    When accede a la pantalla de inicio
    Then los torneos se muestran de mayor a menor fecha de inicio

  Scenario: Fecha visible en cada tarjeta
    Given un torneo con fecha_inicio="2025-12-01" y fecha_fin="2025-12-01"
    When el organizador ve la tarjeta del torneo
    Then la tarjeta muestra "1 dic 2025"

  Scenario: Rango de fechas cuando son distintas
    Given un torneo con fecha_inicio="2025-12-01" y fecha_fin="2025-12-03"
    When el organizador ve la tarjeta del torneo
    Then la tarjeta muestra "1–3 dic 2025" o equivalente legible

  Scenario: El ordenamiento aplica también al histórico
    Given el organizador filtra por "Histórico"
    Then los torneos históricos también aparecen ordenados por fecha descendente
```

---

## Notas de implementación

- El DTO ya incluye `fecha_inicio` y `fecha_fin` — no requiere cambios de backend
- El locale `es-AR` produce "dic", "ene", etc. — verificar en mobile que no se corte
- No usar `new Date(fecha)` sin zona horaria — agregar `T00:00:00` para evitar off-by-one por UTC

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-01
- Componente: `frontend/src/pages/organizador/DashboardPage.tsx`
- Tipo: `frontend/src/api/torneo.ts` — `TorneoDto`

---

*Redactado: 2026-05-05 — SP6 INC-6.2*
