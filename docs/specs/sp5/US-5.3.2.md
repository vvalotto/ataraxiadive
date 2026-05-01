# US-5.3.2: Vista del atleta

**Estado**: `To Do`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.3
**Bounded Context**: `frontend` (consume `torneo/api/` y `registro/api/`)
**Capas afectadas**: `frontend/src/App.tsx`, `frontend/src/types/auth.ts`, `frontend/src/pages/atleta/`

---

## Descripcion

Como **atleta**,
quiero **ver mi perfil y los torneos disponibles para inscripcion**
para **saber donde puedo participar y acceder a mi informacion personal en la plataforma**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Tipo | `RolUsuario` | Extiende con `'atleta'` ademas de `'juez'` y `'organizador'` |
| Guard | `RequireRole` | Protege las rutas `/atleta/*` — redirige si el rol no es `atleta` |
| Query | `GET /torneos` | Lista torneos; el atleta filtra los que estan en estado `INSCRIPCION` |
| Pagina nueva | `AtletaDashboardPage` | Perfil del atleta + torneos disponibles para inscripcion |

### Lenguaje ubicuo relevante

- **Atleta:** usuario con rol ATLETA; accede a su propio perfil e inscripcion.
- **Torneo disponible:** torneo en estado `INSCRIPCION` — puede recibir nuevas inscripciones.
- **Perfil del atleta:** email y rol leidos del JWT en memoria (sin llamada adicional al backend).

---

## Especificacion del comportamiento

### Invariantes

- **INV-5.3.2-01:** Solo usuarios con rol `ATLETA` pueden acceder a `/atleta/*`; cualquier otro rol es redirigido a su ruta correspondiente por `RequireRole`.
- **INV-5.3.2-02:** Un atleta autenticado no puede navegar a `/organizador/*` ni `/juez/*`; `RequireRole` bloquea el acceso y redirige a `/`.
- **INV-5.3.2-03:** La seccion "Torneos disponibles" muestra solo torneos con estado `INSCRIPCION`; los torneos en otros estados no se muestran.
- **INV-5.3.2-04:** El perfil se construye con los claims del JWT en memoria (email, rol); no requiere llamada adicional al backend.
- **INV-5.3.2-05:** Esta vista es de solo lectura — la inscripcion efectiva se implementa en INC-5.4.

### Operacion principal — cargar dashboard del atleta

| | Descripcion |
|---|---|
| **Precondicion** | Usuario autenticado con rol ATLETA. |
| **Postcondicion** | Se muestra perfil (email + rol) y lista de torneos en estado INSCRIPCION con nombre, sede y fechas. |

**Flujo de datos:**

```
1. Perfil: leer email y rol del authStore (JWT en memoria)
2. Torneos disponibles:
   GET /torneos -> filtrar client-side por estado == "INSCRIPCION"
3. Renderizar:
   - Seccion "Mi perfil": email, rol "Atleta"
   - Seccion "Torneos disponibles": lista con nombre, sede, fecha_inicio
   - Si no hay torneos en INSCRIPCION: mensaje "No hay torneos disponibles en este momento"
```

### Routing y tipos

**Cambios en `frontend/src/types/auth.ts`:**

```typescript
// Antes
export type RolUsuario = 'juez' | 'organizador'

// Despues
export type RolUsuario = 'juez' | 'organizador' | 'atleta'
```

**Cambios en `frontend/src/App.tsx`:**

```typescript
// RootRedirect agrega rama atleta
if (rol === 'atleta') return <Navigate to="/atleta/dashboard" replace />

// Nueva ruta protegida
<Route
  path="/atleta/dashboard"
  element={
    <RequireRole role="atleta">
      <AtletaDashboardPage />
    </RequireRole>
  }
/>
```

**Ejemplo concreto:**

```
Atleta "atleta1@email.com" inicia sesion.
JWT contiene: { sub: "atleta1@email.com", rol: "ATLETA" }.
RootRedirect -> /atleta/dashboard

Dashboard muestra:
  Mi perfil: atleta1@email.com — Atleta
  Torneos disponibles:
    "Buenos Aires Open 2026" — Piscina Municipal — 10 jun 2026
    "Campeonato Patagonia" — Mar del Plata — 15 jul 2026

Atleta navega manualmente a /organizador/dashboard.
RequireRole role="organizador" -> redirige a / -> RootRedirect -> /atleta/dashboard
```

---

## Criterios de aceptacion (BDD)

```gherkin
Feature: US-5.3.2 — Vista del atleta

  Background:
    Given el sistema tiene los torneos:
      | nombre                  | estado       |
      | Buenos Aires Open 2026  | INSCRIPCION  |
      | Campeonato Patagonia    | INSCRIPCION  |
      | Torneo BA 2025          | FINALIZADO   |

  Scenario: atleta autenticado es redirigido a su dashboard
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When navega a "/"
    Then es redirigido a "/atleta/dashboard"

  Scenario: dashboard muestra perfil del atleta
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When accede a "/atleta/dashboard"
    Then ve su email "atleta1@email.com"
    And ve su rol como "Atleta"

  Scenario: dashboard muestra solo torneos en INSCRIPCION
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When accede a "/atleta/dashboard"
    Then ve "Buenos Aires Open 2026" en la lista de torneos disponibles
    And ve "Campeonato Patagonia" en la lista de torneos disponibles
    And no ve "Torneo BA 2025" en la lista

  Scenario: sin torneos disponibles muestra mensaje informativo
    Given no existen torneos en estado INSCRIPCION
    And "atleta1@email.com" esta autenticado con rol ATLETA
    When accede a "/atleta/dashboard"
    Then ve el mensaje "No hay torneos disponibles en este momento"

  Scenario: atleta no puede acceder a rutas del organizador
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When intenta navegar a "/organizador/dashboard"
    Then es redirigido a "/atleta/dashboard"

  Scenario: atleta no puede acceder a rutas del juez
    Given "atleta1@email.com" esta autenticado con rol ATLETA
    When intenta navegar a "/juez/disciplinas"
    Then es redirigido a "/atleta/dashboard"
```

---

## Impacto arquitectonico

- [x] No — solo frontend; reutiliza `GET /torneos` existente.

**Capa(s) afectadas:**
- [x] `frontend/src/types/auth.ts` — agregar `'atleta'` a `RolUsuario`.
- [x] `frontend/src/App.tsx` — `RootRedirect` para atleta + ruta `/atleta/dashboard`.
- [x] `frontend/src/pages/atleta/AtletaDashboardPage.tsx` — nueva pagina (perfil + torneos disponibles).
- [x] `frontend/src/api/torneo.ts` — reutilizar `listarTorneos()`; filtrado client-side por estado.

---

## Referencias

- Plan SP5: `docs/plans/sp5/PLAN-SP5.md §INC-5.3`
- Tipos de auth: `frontend/src/types/auth.ts`
- Routing actual: `frontend/src/App.tsx`
- Guard de rol: `frontend/src/components/RequireRole.tsx`
- API torneos: `frontend/src/api/torneo.ts`
- INC-5.4 (inscripcion completa): especificara la accion de inscribirse desde esta vista

---

## Notas de implementacion

- El `RequireRole` existente ya funciona con strings; agregar `'atleta'` al tipo es suficiente para que el guard funcione sin modificarlo.
- La vista es intencionalmente minima — un placeholder con alcance claro para INC-5.4. No implementar botones de inscripcion ni flujos que correspondan a INC-5.4.
- Usar el mismo patron de layout que el organizador (sidebar o header con logout) para coherencia visual.
- El filtrado por estado `INSCRIPCION` es client-side sobre la respuesta de `GET /torneos`; no requiere nuevo endpoint.

---

*Redactado: 2026-04-23 — INC-5.3 Gestion de usuarios y roles*
