# US-5.1.7: Política de tabs por fase y estado CANCELADO

**Estado**: `Done`
**Sprint**: SP5 — La Puesta en Marcha
**Incremento**: INC-5.1-ADJ
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/organizador/DetalleTorneoPage.tsx`

---

## Descripción

Como **organizador**,
quiero que las pestañas del panel de torneo reflejen la fase real del torneo
para **no ver opciones operativas que no corresponden al estado actual**.

---

## Contexto del dominio

### Modelo involucrado

| Elemento | Nombre | Responsabilidad |
|---|---|---|
| Page | `DetalleTorneoPage` | Renderiza tabs y paneles del torneo según fase |
| Tipo | `EstadoTorneo` | Enum: `CREADO`, `INSCRIPCION_ABIERTA`, `PREPARACION`, `EJECUCION`, `PREMIACION`, `CERRADO`, `CANCELADO` |
| Política | `TABS_POR_ESTADO` | Mapeo estado → tabs habilitadas |

### Hallazgos UAT origen

- **UAT-5.1-03:** torneo `CANCELADO` muestra tabs operativas activas en lugar de solo el resumen.
- **UAT-5.1-05:** torneo en `INSCRIPCION_ABIERTA` muestra las pestañas `Grilla`, `Jueces` y `Ejecucion` habilitadas, aunque esas fases todavía no corresponden.

---

## Especificación del comportamiento

### Política de tabs por estado

| Estado | Tabs habilitadas |
|--------|-----------------|
| `CREADO` | `Detalle` |
| `INSCRIPCION_ABIERTA` | `Detalle`, `Inscriptos` |
| `PREPARACION` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces` |
| `EJECUCION` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion` |
| `PREMIACION` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion` |
| `CERRADO` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion` (solo lectura) |
| `CANCELADO` | ninguna — se reemplaza el contenido del panel por resumen de cancelación |

### Invariantes

- **INV-5.1.7-01:** Un tab deshabilitado no puede ser activado por click ni conservado como `activeTab` si el torneo recarga en un estado incompatible.
- **INV-5.1.7-02:** En estado `CANCELADO`, ningún panel hijo (Inscriptos, Grilla, Jueces, Ejecucion) debe renderizarse — se muestra solo resumen básico y mensaje de cancelación.
- **INV-5.1.7-03:** Un tab deshabilitado se muestra visualmente diferenciado (opacidad reducida, cursor `not-allowed`), no se oculta.
- **INV-5.1.7-04:** El `activeTab` por defecto es siempre `Detalle` al cargar por primera vez.

### Comportamiento de reset de activeTab

Si el torneo recarga (por `refetch`) y `activeTab` ya no está en las tabs habilitadas para el nuevo estado, `activeTab` se resetea automáticamente a `Detalle`.

### Operación principal

| | Descripción |
|---|---|
| **Precondición** | `torneoQuery.data` disponible con campo `estado: EstadoTorneo` |
| **Postcondición** | Solo los tabs permitidos para `estado` son clickeables; `activeTab` nunca apunta a un tab inhabilitado |

---

## Criterios de aceptación (BDD)

```gherkin
Feature: US-5.1.7 — Política de tabs por fase y estado CANCELADO

  Background:
    Given el organizador "org@ataraxia.com" está autenticado con rol ORGANIZADOR

  Scenario: torneo en INSCRIPCION_ABIERTA solo habilita Detalle e Inscriptos
    Given el torneo "BA 2026" está en estado INSCRIPCION_ABIERTA
    When el organizador navega a la página de detalle
    Then las tabs "Detalle" e "Inscriptos" están habilitadas
    And las tabs "Grilla", "Jueces" y "Ejecucion" están visibles pero deshabilitadas

  Scenario: tab deshabilitada no responde a click
    Given el torneo está en INSCRIPCION_ABIERTA
    When el organizador hace click en la tab "Grilla"
    Then el activeTab sigue siendo "Detalle"
    And el panel Grilla no se renderiza

  Scenario: torneo en PREPARACION habilita hasta Jueces
    Given el torneo está en estado PREPARACION
    When el organizador navega a la página de detalle
    Then las tabs "Detalle", "Inscriptos", "Grilla" y "Jueces" están habilitadas
    And la tab "Ejecucion" está visible pero deshabilitada

  Scenario: torneo CANCELADO reemplaza panel por mensaje de cancelación
    Given el torneo está en estado CANCELADO
    When el organizador navega a la página de detalle
    Then se muestra el nombre del torneo y el mensaje "Torneo cancelado"
    And las tabs "Inscriptos", "Grilla", "Jueces" y "Ejecucion" no están presentes
    And AccionesPanel no muestra acciones (solo lectura)

  Scenario: activeTab se resetea si torneo recarga en estado incompatible
    Given el organizador está en la tab "Grilla" del torneo en PREPARACION
    When el torneo transiciona a INSCRIPCION_ABIERTA y la página refresca
    Then el activeTab vuelve a "Detalle"
    And el panel Grilla no se renderiza
```

---

## Impacto arquitectónico

- [x] No — modificación exclusiva de lógica de presentación en `DetalleTorneoPage`.

**Capa(s) afectadas:**
- [x] Frontend — `DetalleTorneoPage.tsx`: agregar `tabsHabilitadas(estado)` y aplicarla al render de tabs y al `activeTab`

---

## Referencias

- Hallazgos UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md` §UAT-5.1-03 y §UAT-5.1-05
- Plan: `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md §US-5.1.7`
- Código fuente: `frontend/src/pages/organizador/DetalleTorneoPage.tsx` línea 13

---

*Redactado: 2026-04-21 — INC-5.1-ADJ ajuste post-UAT panel organizador*
