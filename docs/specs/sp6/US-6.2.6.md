# US-6.2.6: Crear Página de Podios

**Estado**: `Pending`  
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-08  
**Bounded Context**: `frontend`  
**Capas afectadas**: `frontend/pages/organizador/ResultadosPage.tsx`, `frontend/src/App.tsx`, nueva página `frontend/pages/organizador/PodiosPage.tsx`

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
