# US-6.2.4: Panel Torneo — Alertas sin "Resolver" + Jueces sin Texto Nombre

**Estado**: `Done`
**Incremento**: INC-6.2 — Ajustes Organizador  
**Hallazgos**: UI-ORG-02 · UI-ORG-06  
**Bounded Context**: `frontend`  
**Capas afectadas**: `frontend/pages/organizador/DashboardOperativoPage.tsx`, `frontend/components/organizador/JuecesPanel.tsx`, `frontend/components/organizador/TablaJueces.tsx`

---

## Descripción

Como **organizador en el panel de torneo**,
quiero **ver las alertas sin un botón "Resolver" que no puedo accionar, y la lista de jueces con solo el selector necesario**
para **tener una interfaz limpia que refleje fielmente mis responsabilidades reales**.

---

## Contexto de los Hallazgos

### UI-ORG-02 — Alertas con botón "Resolver" que no corresponde al rol

**Ubicación**: `frontend/src/pages/organizador/DashboardOperativoPage.tsx` — líneas ~561 y ~577

El panel de alertas activas muestra un botón/texto `Resolver →` junto a cada alerta. El organizador no puede resolver alertas de competencia — eso es responsabilidad del juez. El botón no tiene acción útil y confunde al usuario.

### UI-ORG-06 — Panel de jueces con información redundante

**Ubicación**: `frontend/src/components/organizador/JuecesPanel.tsx`

El panel muestra dos secciones de resumen ("Cobertura Operativa" y "Estado de Asignación") que no aportan valor al organizador en el contexto de validación SP5. Además, en cada fila de la tabla de asignación de juez, se muestra el nombre del juez como texto adicional junto al selector — lo que duplica información ya visible en el selector mismo.

---

## Fuente de verdad UX

- `docs/design/ux/wireframes-organizador.md` — estructura aprobada del portal organizador, incluyendo alertas y flujos de revisión.
- `docs/design/ux/prototipos/prototipo-organizador.html` — prototipo navegable aprobado para el rol organizador.
- `docs/plans/sp6/PLAN-SP6.md` — hallazgos UI-ORG-02 y UI-ORG-06 detectados en validación SP5.
- `frontend/src/pages/organizador/DashboardOperativoPage.tsx`, `frontend/src/components/organizador/JuecesPanel.tsx` y `frontend/src/components/organizador/TablaJueces.tsx` — implementación React actual comparada contra los hallazgos.

---

## Especificación

### Tarea 1: Eliminar "Resolver →" de las alertas activas

| | |
|---|---|
| **Precondición** | `DashboardOperativoPage.tsx` renderiza `Resolver →` como texto/botón junto a cada alerta (~líneas 561 y 577) |
| **Postcondición** | Las alertas se muestran como texto informativo solamente — sin botón ni texto "Resolver" |
| **Invariante** | Las alertas siguen mostrándose; solo se elimina el elemento de acción "Resolver →" |

Localizar ambas ocurrencias en `DashboardOperativoPage.tsx` y eliminar el elemento que renderiza `Resolver →`.

### Tarea 2: Simplificar JuecesPanel — eliminar secciones de resumen

| | |
|---|---|
| **Precondición** | `JuecesPanel.tsx` renderiza secciones "Cobertura operativa" (~línea 224) y "Estado de Asignación" (~línea 235) |
| **Postcondición** | Esas secciones no se renderizan — el panel muestra directamente la tabla de asignación de jueces |
| **Invariante** | La funcionalidad de asignación de juez (selector + guardar) se mantiene íntegra |

### Tarea 3: Simplificar fila de juez — solo selector, sin texto nombre

| | |
|---|---|
| **Precondición** | Junto al `JuezSelector`, la fila muestra el nombre del juez seleccionado como texto separado |
| **Postcondición** | La fila solo contiene el `JuezSelector` — el nombre es visible dentro del selector mismo |
| **Invariante** | La funcionalidad de selección y guardado del juez no cambia |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-6.2.4 — Panel torneo: alertas limpias + jueces simplificados

  Scenario: Las alertas no muestran botón Resolver
    Given un torneo en ejecución con alertas activas
    When el organizador ve el panel de alertas
    Then ninguna alerta tiene un botón o texto "Resolver"
    And la alerta muestra solo la descripción del problema

  Scenario: El panel de jueces no muestra secciones de cobertura/estado
    Given el organizador accede a la sección de Jueces del torneo
    Then no se ve ninguna sección "Cobertura operativa"
    And no se ve ninguna sección "Estado de Asignación"

  Scenario: Fila de juez solo tiene el selector
    Given una entrada de grilla sin juez asignado
    When el organizador ve la fila de asignación
    Then solo aparece el selector de juez, sin texto adicional con el nombre
```

---

## Notas de implementación

- Verificar si "Cobertura operativa" y "Estado de Asignación" son componentes propios o markup inline en `JuecesPanel.tsx` — si son componentes, eliminar la invocación; si son secciones inline, eliminar el bloque
- Las líneas exactas son aproximadas — buscar por string `"Cobertura operativa"` y `"Resolver"` en los archivos indicados
- La funcionalidad de asignación de juez es core del flujo organizador — testear que sigue funcionando tras los cambios

---

## Referencias

- Hallazgos: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-02 · UI-ORG-06
- Archivo: `frontend/src/pages/organizador/DashboardOperativoPage.tsx`
- Componente: `frontend/src/components/organizador/JuecesPanel.tsx`

---

*Redactado: 2026-05-05 — SP6 INC-6.2*
