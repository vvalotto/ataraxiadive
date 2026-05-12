# US-6.6.4: Página pública de torneo en ejecución — info y grilla del día

**Estado**: `Pending`
**Incremento**: INC-6.6 — Portal Público
**Bounded Context**: frontend + (backend sin cambios — endpoints ya son públicos)
**Capas afectadas**:
- `frontend/src/pages/PublicTorneoDetallePage.tsx` (nuevo)
- `frontend/src/App.tsx` — nueva ruta `/portalapnea/:torneoId`
- `frontend/src/pages/PublicTorneosPage.tsx` — fix destino "Ver panel" → `/portalapnea/:torneoId`

---

## Descripción

Como **visitante del portal**,
quiero **ver un resumen del torneo en ejecución sin iniciar sesión**
para **seguir la competencia en tiempo real — qué atletas compiten, en qué orden y con qué resultado**.

---

## Contexto

Los endpoints necesarios ya existen y son públicos (sin auth):
- `GET /api/torneos/:torneoId` → nombre, fecha, sede, entidad organizadora, estado
- `GET /api/competencia?torneo_id=:torneoId` → lista de competencias (por disciplina)
- `GET /api/competencia/:competenciaId/grilla?disciplina=:disciplina` → grilla ordenada de atletas

El botón "Ver panel" en `PublicTorneosPage` para torneos en `EJECUCION` ya genera el destino
`/portalapnea/:torneoId` (sin `/panel` — se corrige el sufijo innecesario).

La página es completamente pública — no requiere `RequireAuth` ni `RequireRole`.

---

## Especificación

### Tarea 1 — Nueva página `PublicTorneoDetallePage`

| | |
|---|---|
| **Precondición** | Ruta `/portalapnea/:torneoId` no existe |
| **Postcondición** | La ruta existe y muestra info del torneo + grilla |
| **Invariante** | No requiere autenticación; funciona para cualquier visitante |

**Layout de la página:**

```
┌─────────────────────────────────────────────┐
│ AtaraxiaDive            [Iniciar sesión / Mi portal] │  ← header igual a PublicTorneosPage
├─────────────────────────────────────────────┤
│ ← Volver a torneos                          │
│                                             │
│  [nombre del torneo]                        │
│  fecha_inicio — fecha_fin · ciudad, pais    │
│  Organiza: entidad_organizadora.nombre      │
│  Estado: EN EJECUCIÓN  (badge)              │
├─────────────────────────────────────────────┤
│  [Disciplina: STA / DYN / DNF / ...]  ← tab o sección por competencia
│                                             │
│  Pos  Atleta              AP     OT     Estado   Tarjeta  │
│   1   Juan Pérez          5:30   09:00  PENDIENTE  —      │
│   2   Ana García          6:00   09:05  REALIZADO  Blanca │
│  ...                                        │
└─────────────────────────────────────────────┘
```

**Comportamiento por estado de performance:**
- `PENDIENTE` → gris, sin tarjeta
- `EN_PROGRESO` → resaltado (badge "En curso")
- `REALIZADO` → muestra tarjeta (blanca / roja / amarilla) y resultado

### Tarea 2 — Registrar ruta en `App.tsx`

| | |
|---|---|
| **Precondición** | No existe `<Route path="/portalapnea/:torneoId">` |
| **Postcondición** | La ruta existe, sin RequireAuth |

```tsx
<Route path="/portalapnea/:torneoId" element={<PublicTorneoDetallePage />} />
```

### Tarea 3 — Corregir destino "Ver panel" en `PublicTorneosPage`

| | |
|---|---|
| **Precondición** | `accionPorEstado` retorna `/portalapnea/${torneo_id}/panel` para EJECUCION (ruta inexistente) |
| **Postcondición** | Retorna `/portalapnea/${torneo_id}` (ruta de la nueva página) |

```tsx
case 'EJECUCION':
  if (rol === 'juez') return { label: 'Ver panel', destino: '/juez/disciplinas' }
  if (rol === 'organizador') return { label: 'Ver panel', destino: '/organizador/torneo' }
  return { label: 'Ver panel', destino: `/portalapnea/${torneo.torneo_id}` }
```

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.6.4 — Página pública de torneo en ejecución

  Scenario: Visitante accede a la página del torneo sin sesión
    Given el torneo "abc-123" está en estado EJECUCION
    And el usuario no está autenticado
    When navega a /portalapnea/abc-123
    Then ve el nombre del torneo, fecha y sede
    And ve la grilla de atletas ordenada por posición
    And no se le pide autenticación

  Scenario: La página muestra una sección por disciplina activa
    Given el torneo "abc-123" tiene dos competencias: STA y DYN
    When navega a /portalapnea/abc-123
    Then ve dos secciones de grilla, una por disciplina

  Scenario: La grilla muestra estado y tarjeta de cada atleta
    Given la grilla de STA tiene atletas con estados PENDIENTE, EN_PROGRESO y REALIZADO
    When navega a /portalapnea/abc-123
    Then el atleta PENDIENTE aparece sin tarjeta
    And el atleta EN_PROGRESO aparece resaltado como "En curso"
    And el atleta REALIZADO muestra su tarjeta asignada

  Scenario: Botón "Ver panel" en torneos EJECUCION navega a /portalapnea/:torneoId
    Given el torneo "abc-123" está en EJECUCION en la lista pública
    When el visitante pulsa "Ver panel"
    Then navega a /portalapnea/abc-123

  Scenario: Visitante autenticado ve también su portal en el header
    Given el usuario tiene sesión como atleta
    When navega a /portalapnea/abc-123
    Then el header muestra "Mi portal" en lugar de "Iniciar sesión"
```

---

## Notas de implementación

- **Polling opcional**: la grilla cambia durante la competencia. Un `refetchInterval: 30_000` en el query es suficiente para actualizaciones en vivo sin websockets.
- **Múltiples disciplinas**: si hay varias competencias, mostrarlas como secciones separadas con el nombre de la disciplina como título. Si solo hay una, sin tabs.
- **Estado de torneo**: si el torneo no está en `EJECUCION`, mostrar igualmente la grilla (útil en `PREMIACION` para ver resultados). Solo mostrar "No disponible" si el torneo no existe o está en `CREADO`/`INSCRIPCION_ABIERTA`/`CANCELADO`.
- **Sin auth en backend**: los tres endpoints usados ya no requieren token. No hay cambios de backend.
- **`fetchCompetenciasPorTorneo`** ya existe en `frontend/src/api/competencia.ts:174`.
- **`fetchGrillaCompetencia`** ya existe en `frontend/src/api/competencia.ts:222`.
- **`fetchTorneo`** ya existe en `frontend/src/api/torneo.ts:180`.

---

## Fuente de verdad UX

No existen wireframes ni prototipos aprobados para el rol "visitante" (portal público). La UX fue diseñada de novo en INC-6.6, siguiendo los patrones visuales ya implementados:
- `frontend/src/pages/PublicTorneosPage.tsx` — fuente de verdad de estructura, header y estilo visual del portal público.
- `frontend/src/pages/atleta/AtletaMiGrillaPage.tsx` — referencia de cómo se renderiza la grilla de atletas.

---

## Referencias

- US-6.6.3: navegación contextual — botón "Ver panel" que lleva a esta página
- `frontend/src/pages/PublicTorneosPage.tsx` — página de lista, mismo estilo visual
- `frontend/src/pages/atleta/AtletaMiGrillaPage.tsx` — referencia de cómo se muestra la grilla
- `frontend/src/api/competencia.ts` — `fetchCompetenciasPorTorneo`, `fetchGrillaCompetencia`
- `frontend/src/api/torneo.ts` — `fetchTorneo`

---

*Redactado: 2026-05-10 — SP6 INC-6.6*
