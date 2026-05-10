# US-6.6.2: Página pública de torneos — lista con tarjetas y acciones contextuales

**Estado**: `Pending`
**Incremento**: INC-6.6 — Portal Público
**Bounded Context**: frontend
**Capas afectadas**:
- `frontend/src/pages/PublicTorneosPage.tsx` (nueva)
- `frontend/src/App.tsx`

---

## Descripción

Como **visitante del portal** (puede o no estar autenticado),
quiero **ver una lista de torneos con sus datos básicos y una acción contextual según el estado del torneo**
para **conocer el calendario y acceder al torneo que me interesa según mi rol**.

---

## Contexto

Actualmente no existe ninguna ruta pública en el frontend. El `/` redirige a `/login` si el usuario no tiene sesión. Esta US crea la página pública `/torneos` accesible sin autenticación, que actúa como punto de entrada al sistema.

**Acciones contextuales por estado:**

| Estado | Acción | Requiere auth | Destino |
|--------|--------|:---:|---------|
| `CREADO` | — (solo informativo) | No | — |
| `INSCRIPCION_ABIERTA` | "Inscribirse" | Sí (atleta) | `/atleta/torneos/:id/inscripcion` |
| `PREPARACION` | — (solo informativo) | No | — |
| `EJECUCION` | "Ver panel" | Sí (juez/organizador) | según rol |
| `PREMIACION` | "Ver resultados" | No | `/torneos/:id/resultados` (futura) |
| `CERRADO` | "Ver resultados" | No | `/torneos/:id/resultados` (futura) |
| `CANCELADO` | — (no aparece en lista pública) | — | — |

> Los estados `PREMIACION`/`CERRADO` con "Ver resultados" apuntan a una página futura. En v1.0 mostrar el botón pero deshabilitado o navegar a resultados si existe endpoint público — decidir durante implementación.

---

## Especificación

### Tarea 1 — Agregar ruta pública `/torneos` en `App.tsx`

| | |
|---|---|
| **Precondición** | `App.tsx` solo tiene rutas protegidas (sin `RequireRole`) excepto `/login`, `/registro` |
| **Postcondición** | Existe una ruta `/torneos` accesible sin autenticación |
| **Invariante** | Las rutas existentes no cambian |

```tsx
// En App.tsx — sin RequireRole ni RequireAuth:
<Route path="/torneos" element={<PublicTorneosPage />} />
```

### Tarea 2 — Crear `PublicTorneosPage.tsx`

| | |
|---|---|
| **Precondición** | `GET /api/torneos` devuelve lista pública (US-6.6.1) |
| **Postcondición** | Página muestra lista de tarjetas de torneos con acción contextual |
| **Invariante** | La página es accesible sin token; el visitante autenticado ve las mismas tarjetas |

**Estructura de la página:**

```
PublicTorneosPage
├── Header simple (nombre del sistema + botón "Iniciar sesión" si no hay token)
├── Título "Torneos de Apnea"
└── Lista de TorneoCard (por cada torneo)
    ├── Nombre del torneo
    ├── Fechas (fecha_inicio — fecha_fin)
    ├── Sede (ciudad, país)
    ├── Badge de estado (chip con color)
    └── Botón de acción contextual (si aplica al estado)
```

**Colores de badge por estado:**

| Estado | Color sugerido |
|--------|---------------|
| `CREADO` | gris |
| `INSCRIPCION_ABIERTA` | azul |
| `PREPARACION` | amarillo |
| `EJECUCION` | verde |
| `PREMIACION` | dorado |
| `CERRADO` | gris oscuro |

**Llamada a la API:**

```tsx
// Reutilizar el mismo endpoint del organizador — ya existe fetcher en el proyecto
const { data: torneos } = useQuery({
  queryKey: ['torneos-publicos'],
  queryFn: () => fetch('/api/torneos').then(r => r.json()),
})
```

### Tarea 3 — Lógica de acción contextual por estado

| | |
|---|---|
| **Precondición** | Cada torneo tiene `estado` en la respuesta de la API |
| **Postcondición** | El botón de acción refleja el estado y dispara la navegación correcta |
| **Invariante** | Si el usuario no está autenticado y la acción requiere auth → US-6.6.3 maneja el redirect |

```tsx
function accionPorEstado(torneo: TorneoPublico, rol: string | null) {
  switch (torneo.estado) {
    case 'INSCRIPCION_ABIERTA':
      return { label: 'Inscribirse', destino: `/atleta/torneos/${torneo.torneo_id}/inscripcion` }
    case 'EJECUCION':
      if (rol === 'juez') return { label: 'Ver panel', destino: `/juez/disciplinas` }
      if (rol === 'organizador') return { label: 'Ver panel', destino: `/organizador/torneo` }
      return { label: 'Ver panel', destino: `/torneos/${torneo.torneo_id}/panel` }
    case 'PREMIACION':
    case 'CERRADO':
      return { label: 'Ver resultados', destino: null, deshabilitado: true } // futuro
    default:
      return null
  }
}
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.6.2 — Página pública de torneos

  Scenario: Visitante sin login accede a /torneos
    Given el usuario no está autenticado
    When navega a /torneos
    Then ve la lista de torneos sin ser redirigido a /login
    And cada torneo muestra nombre, fechas, sede y estado

  Scenario: Torneo en INSCRIPCION_ABIERTA muestra botón "Inscribirse"
    Given existe un torneo con estado INSCRIPCION_ABIERTA
    When el visitante ve la lista de torneos
    Then hay un botón "Inscribirse" en la tarjeta de ese torneo

  Scenario: Torneo en EJECUCION muestra botón "Ver panel"
    Given existe un torneo con estado EJECUCION
    When el visitante ve la lista de torneos
    Then hay un botón "Ver panel" en la tarjeta de ese torneo

  Scenario: Torneo en CREADO no muestra acción
    Given existe un torneo con estado CREADO
    When el visitante ve la lista de torneos
    Then la tarjeta de ese torneo no tiene botón de acción (solo informativo)

  Scenario: Torneos CANCELADOS no aparecen en la lista
    Given existe un torneo con estado CANCELADO
    When el visitante navega a /torneos
    Then ese torneo no aparece en la lista

  Scenario: Usuario autenticado ve las mismas tarjetas
    Given un atleta autenticado navega a /torneos
    Then ve la misma lista de torneos que un visitante sin login
```

---

## Notas de implementación

- **Reutilizar estilos existentes:** usar los mismos Tailwind classes que `AtletaTorneosPage` o `DashboardPage` para tarjetas — no crear un sistema nuevo.
- **Header mínimo:** si el usuario no está autenticado, mostrar un botón "Iniciar sesión" que navega a `/login?redirect=/torneos`. Si está autenticado, mostrar un botón que lleva a su portal (`/atleta`, `/organizador`, `/juez/disciplinas`).
- **Orden:** torneos por `fecha_inicio` ascendente (los más próximos primero).
- **Estado vacío:** si no hay torneos, mostrar mensaje "No hay torneos programados próximamente".
- **"Ver resultados" en v1.0:** si no existe endpoint público de resultados, deshabilitar el botón con tooltip "Resultados disponibles próximamente" — no bloquear el despliegue por esto.

---

## Referencias

- US-6.6.1: endpoint `GET /api/torneos` público
- US-6.6.3: lógica de redirect al login guardando destino
- `frontend/src/App.tsx`: routing
- `frontend/src/components/RequireAuth.tsx`: patrón de auth guard
- Plan: `docs/plans/sp6/PLAN-SP6.md` — §3 INC-6.6

---

*Redactado: 2026-05-10 — SP6 INC-6.6*
