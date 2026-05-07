# US-6.3.1: Inicio Atleta — "En línea" en Header + Sin "Hola" + Torneos en Curso Ordenados

**Estado**: `Pending`
**Incremento**: INC-6.3 — Ajustes Atleta
**Hallazgos**: UI-ATL-01
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/components/atleta/AtletaShell.tsx`, `frontend/src/pages/atleta/AtletaHomePage.tsx`

---

## Descripción

Como **atleta en la pantalla de inicio**,
quiero **ver mi estado de conexión en el header y una vista de torneos ordenada de forma útil**
para **saber rápidamente si estoy conectado y ver primero las actividades más relevantes**.

---

## Contexto del Hallazgo

### UI-ATL-01 — Header genérico + saludo redundante + orden de disciplinas sin criterio

**Ubicación**: `AtletaShell.tsx` y `AtletaHomePage.tsx`

**Tres sub-hallazgos:**

1. El header de `AtletaShell` no muestra estado de conexión. Solo dice "AtaraxiaDive" sin indicar si el atleta está en línea.

2. En `AtletaHomePage.tsx` (línea 72), hay un `<p>Hola</p>` sobre el nombre del atleta. Es redundante dado que el nombre completo se muestra inmediatamente debajo.

3. La sección "Mis inscripciones activas" muestra los torneos sin orden interno de las disciplinas: no distingue cuál es la próxima, cuáles son posteriores y cuáles ya se realizaron.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-atleta.md` — contrato visual aprobado del portal atleta.
- `docs/plans/sp6/PLAN-SP6.md` — hallazgo UI-ATL-01 detectado en validación SP5.
- `frontend/src/components/atleta/AtletaShell.tsx` — shell base de todas las páginas del atleta.
- `frontend/src/pages/atleta/AtletaHomePage.tsx` — página de inicio del portal atleta.

---

## Especificación

### Tarea 1: Agregar indicador "En línea" en AtletaShell

| | |
|---|---|
| **Precondición** | El header de `AtletaShell` muestra solo el badge "AtaraxiaDive" sin estado de conexión |
| **Postcondición** | El header muestra un punto verde + texto "En línea" junto al badge "AtaraxiaDive" |
| **Invariante** | El indicador es puramente visual (siempre verde en esta versión — no hay estado offline dinámico); no requiere lógica de conectividad |

```tsx
// En AtletaShell.tsx, dentro del div .flex.items-center.gap-2:
<p className="text-xs font-semibold uppercase tracking-[0.24em] text-sky-400">
  AtaraxiaDive
</p>
<span className="flex items-center gap-1 text-xs font-semibold text-emerald-400">
  <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
  En línea
</span>
```

### Tarea 2: Eliminar "Hola" de AtletaHomePage

| | |
|---|---|
| **Precondición** | Existe `<p className="...text-sky-400">Hola</p>` antes del nombre del atleta |
| **Postcondición** | Esa línea se elimina; el nombre del atleta pasa a ser el título principal de la sección |
| **Invariante** | El resto de la sección (nombre, categoría, club) permanece intacto |

### Tarea 3: Ordenar disciplinas en torneos activos

| | |
|---|---|
| **Precondición** | En la sección "Mis inscripciones activas", las disciplinas de cada torneo se muestran en el orden arbitrario del Set |
| **Postcondición** | Las disciplinas se ordenan: primero la que tiene OT asignado más próximo, luego las posteriores, finalmente las sin OT o ya realizadas |
| **Invariante** | Solo aplica a la lista interna de cada tarjeta de torneo; el orden entre torneos no cambia |

Criterio de orden para disciplinas dentro de cada torneo:
1. Con OT futuro: ordenadas por `ot` ascendente (más próxima primero)
2. Sin OT asignado: al final del grupo con OT futuro
3. Con OT ya pasado (realizadas): al final de todo

```typescript
// En AtletaHomePage.tsx, al construir torneosActivos:
const ahora = new Date()

function sortDisciplinas(entries: typeof query.data.entries): typeof query.data.entries {
  return [...entries].sort((a, b) => {
    const aFutura = a.ot && new Date(a.ot) > ahora
    const bFutura = b.ot && new Date(b.ot) > ahora
    const aRealizada = a.ot && new Date(a.ot) <= ahora
    const bRealizada = b.ot && new Date(b.ot) <= ahora
    if (aFutura && bFutura) return new Date(a.ot!).getTime() - new Date(b.ot!).getTime()
    if (aFutura) return -1
    if (bFutura) return 1
    if (!aRealizada && !bRealizada) return 0  // ambas sin OT
    if (!aRealizada) return -1
    if (!bRealizada) return 1
    return new Date(a.ot!).getTime() - new Date(b.ot!).getTime()
  })
}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.3.1 — Inicio atleta: "En línea" + sin "Hola" + disciplinas ordenadas

  Scenario: Header muestra indicador de conexión
    Given el atleta está en cualquier página del portal atleta
    When carga la página
    Then el header muestra "En línea" con un punto verde junto al badge "AtaraxiaDive"

  Scenario: Sin saludo redundante en inicio
    Given el atleta navega a la pantalla de inicio
    When carga la página
    Then NO aparece el texto "Hola" antes del nombre del atleta
    And el nombre del atleta es el elemento principal de la sección de bienvenida

  Scenario: Disciplinas con OT próximo aparecen primero
    Given un torneo activo con disciplinas DYN (OT: 10:00) y STA (OT: 14:00)
    When el atleta ve la sección "Mis inscripciones activas"
    Then DYN aparece antes que STA en la lista de disciplinas

  Scenario: Disciplinas ya realizadas aparecen al final
    Given un torneo activo con disciplinas DYN (OT: ayer) y STA (OT: mañana)
    When el atleta ve la sección "Mis inscripciones activas"
    Then STA (próxima) aparece antes que DYN (realizada)

  Scenario: Disciplinas sin OT asignado van antes de las realizadas
    Given un torneo activo con disciplinas DYN (sin OT) y STA (OT: ayer)
    When el atleta ve la sección "Mis inscripciones activas"
    Then DYN (sin OT) aparece antes que STA (realizada)
```

---

## Notas de implementación

- El indicador "En línea" es estático en esta versión — no requiere `navigator.onLine` ni listeners
- La prop `actions` de `AtletaShell` pasa a estar junto al indicador; verificar que no se superpongan en pantallas pequeñas (max-w-[430px])
- `query.data.entries` ya incluye el campo `ot` — no hay cambios de backend

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — UI-ATL-01
- Shell: `frontend/src/components/atleta/AtletaShell.tsx`
- Inicio: `frontend/src/pages/atleta/AtletaHomePage.tsx`

---

*Redactado: 2026-05-07 — SP6 INC-6.3*
