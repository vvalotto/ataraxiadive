# US-6.2.6: Crear Página de Podios

**Estado**: `Done`
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-08  
**Bounded Context**: `frontend`  
**Capas afectadas**: `frontend/src/pages/organizador/ResultadosPage.tsx`, `frontend/src/App.tsx`, nueva página `frontend/src/pages/organizador/PodiosPage.tsx`

---

## Descripción

Como **organizador revisando el cierre de un torneo**,
quiero **ver los podios en una página dedicada separada de los rankings por disciplina**
para **navegar más fácilmente entre la vista de resultados técnicos y la vista de premiación**.

---

## Contexto del Hallazgo

### UI-ORG-08 — Podios embebidos dentro de Resultados

**Ubicación**: `frontend/src/pages/organizador/ResultadosPage.tsx`

`PodiosSection` (podios por disciplina + overall) está embebida dentro de `ResultadosPage`, lo que hace la página muy larga y dificulta llegar al contenido de premiación. El componente `PodiosSection` ya está extraído y es reutilizable — solo hay que moverlo a su propia página y ruta.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md` — contrato visual aprobado del portal organizador; define `S-04 Resultados` como pantalla de rankings técnicos con navegación sticky y ancho máximo de 1100 px.
- `docs/design/ux/prototipos/prototipo-organizador.html` — prototipo navegable aprobado para el rol organizador y base de navegación del panel.
- `docs/design/ux/flujos-por-rol.md` — flujo del organizador; ubica resultados, overall y publicación oficial dentro del cierre del torneo.
- `docs/design/ux/decisiones-frontend.md` — decisiones de React Router, React Query y Tailwind aplicables a la nueva ruta.
- `docs/plans/sp6/PLAN-SP6.md` — hallazgos UI-ORG-05 y UI-ORG-08 de validación SP5; UI-ORG-08 especializa el wireframe original separando la vista de premiación en una página propia.
- `frontend/src/pages/organizador/ResultadosPage.tsx`, `frontend/src/components/organizador/PodiosSection.tsx` y `frontend/src/components/organizador/OrganizadorLayout.tsx` — implementación React actual comparada contra el hallazgo.

**Lectura UX aplicada:** el wireframe original `S-04 Resultados` combinaba ranking por disciplina y overall en una pantalla. La validación SP5 refinó ese contrato: `Resultados` queda como vista técnica de rankings por disciplina, y `Podios` pasa a ser la vista dedicada de premiación. Esta US implementa esa separación sin cambiar tokens visuales, layout base, guards ni patrón de navegación del organizador.

---

## Especificación

### Tarea 1: Crear PodiosPage

| | |
|---|---|
| **Precondición** | No existe `frontend/src/pages/organizador/PodiosPage.tsx` |
| **Postcondición** | Existe la página con la misma lógica de datos que `ResultadosPage` usa para `PodiosSection` + `overallQuery` |
| **Invariante** | La página requiere `?torneo_id=` en la URL; sin él, redirige al selector de torneo (mismo patrón que `ResultadosPage`) |

La nueva página extrae de `ResultadosPage` exactamente:
- Las queries: `overallQuery`, `inscriptosQuery`, la lógica de `podioDisciplina` y `podioOverall`
- El render de `PodiosSection` (ambos groups: disciplina y overall)
- El wrapper `OrganizadorLayout` con título "Podios"

### Tarea 2: Registrar ruta en App.tsx

| | |
|---|---|
| **Precondición** | No existe ruta `/organizador/podios` |
| **Postcondición** | `App.tsx` registra `<Route path="/organizador/podios" element={<PodiosPage />} />` con el mismo auth guard que el resto de rutas organizador |
| **Invariante** | La ruta nueva queda dentro del `PrivateRoute` de organizador |

### Tarea 3: Eliminar PodiosSection de ResultadosPage

| | |
|---|---|
| **Precondición** | `ResultadosPage.tsx` renderiza `<PodiosSection ... />` y tiene las queries de overall/podios |
| **Postcondición** | `ResultadosPage.tsx` no renderiza `PodiosSection` ni mantiene las queries de podio (`overallQuery`, `podioOverall`, `podioDisciplina`) |
| **Invariante** | El resto de `ResultadosPage` (rankings por disciplina, selector de disciplina, estado de ranking) permanece intacto |

### Tarea 4: Agregar enlace de navegación hacia Podios

| | |
|---|---|
| **Precondición** | No hay forma de navegar a la página de Podios desde el panel del torneo |
| **Postcondición** | En `TorneoRouteSelector` o en la navegación del `OrganizadorLayout`, aparece un ítem "Podios" que navega a `/organizador/podios?torneo_id={torneoId}` |
| **Invariante** | El ítem solo aparece cuando hay un `torneo_id` activo en contexto |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.2.6 — Página de Podios separada de Resultados

  Scenario: Acceder a la página de Podios con torneo_id válido
    Given un torneo con resultados calculados
    When el organizador navega a /organizador/podios?torneo_id={id}
    Then ve la PodiosSection con los podios por disciplina y overall

  Scenario: La página de Resultados ya no muestra los podios
    Given el mismo torneo
    When el organizador navega a /organizador/resultados?torneo_id={id}
    Then no ve ninguna sección de podios — solo rankings por disciplina

  Scenario: Sin torneo_id, la página de Podios redirige al selector
    Given el organizador navega a /organizador/podios sin query params
    Then ve el selector de torneo (igual que Resultados sin torneo_id)

  Scenario: Existe enlace de navegación hacia Podios en el panel
    Given un torneo activo seleccionado
    When el organizador ve la navegación del torneo
    Then hay un ítem "Podios" que lo lleva a la nueva página
```

---

## Notas de implementación

- `PodiosSection` y sus tipos (`PodioCategoriaGroup`) se importan desde `components/organizador/PodiosSection.tsx` — no hay que moverlos ni duplicarlos
- Las queries de `overallQuery` e `inscriptosQuery` son idénticas a las de `ResultadosPage` — se pueden copiar directamente a `PodiosPage`; si en el futuro se quiere deduplicar, hacerlo en un custom hook (fuera de scope de esta US)
- Verificar que la eliminación de podios de `ResultadosPage` no rompe ningún tipo ni import huérfano (ej: `fetchOverall`, `PodiosSection`, `PodioCategoriaGroup`)

---

## Referencias

- Hallazgo: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-08
- Páginas: `frontend/src/pages/organizador/ResultadosPage.tsx`
- Componente: `frontend/src/components/organizador/PodiosSection.tsx`
- Rutas: `frontend/src/App.tsx`

---

*Redactado: 2026-05-05 — SP6 INC-6.2*
