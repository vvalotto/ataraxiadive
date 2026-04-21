# US-5.1.7: Politica de tabs por fase y estado CANCELADO

**Estado**: `Done`
**Sprint**: SP5 - La Puesta en Marcha
**Incremento**: INC-5.1-ADJ
**Bounded Context**: `frontend`
**Capas afectadas**: `frontend/src/pages/organizador/DetalleTorneoPage.tsx`

---

## Descripcion

Como **organizador**,
quiero que las pestanas del panel de torneo reflejen la fase real del torneo
para **no ver opciones operativas que no corresponden al estado actual**.

---

## Hallazgos UAT origen

- **UAT-5.1-03:** torneo `CANCELADO` muestra tabs operativas activas en lugar de solo el resumen.
- **UAT-5.1-05:** torneo en `INSCRIPCION_ABIERTA` muestra las pestanas `Grilla`, `Jueces` y `Ejecucion` habilitadas.

---

## Politica de tabs por estado

| Estado | Tabs habilitadas |
|--------|------------------|
| `CREADO` | `Detalle` |
| `INSCRIPCION_ABIERTA` | `Detalle`, `Inscriptos` |
| `PREPARACION` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces` |
| `EJECUCION` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion` |
| `PREMIACION` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion` |
| `CERRADO` | `Detalle`, `Inscriptos`, `Grilla`, `Jueces`, `Ejecucion` |
| `CANCELADO` | ninguna; se reemplaza por resumen de cancelacion |

---

## Invariantes

- **INV-5.1.7-01:** Un tab deshabilitado no puede ser activado por click ni conservarse como vista efectiva si el torneo recarga en un estado incompatible.
- **INV-5.1.7-02:** En estado `CANCELADO`, ningun panel hijo operativo (`Inscriptos`, `Grilla`, `Jueces`, `Ejecucion`) debe renderizarse.
- **INV-5.1.7-03:** Un tab deshabilitado se muestra visible y diferenciado, no oculto.
- **INV-5.1.7-04:** El `activeTab` por defecto es `Detalle`.

---

## Criterios de aceptacion

- En `INSCRIPCION_ABIERTA`, solo `Detalle` e `Inscriptos` son clickeables.
- En `PREPARACION`, `Ejecucion` permanece visible pero deshabilitada.
- En `CANCELADO`, se muestra el nombre del torneo y el mensaje `Torneo cancelado`.
- En `CANCELADO`, no se muestran tabs ni acciones operativas.
- Si el torneo cambia de estado, el panel operativo vuelve a `Detalle`.

---

## Referencias

- Hallazgos UAT: `.work/revision-sp5/01-hallazgos-uat-inc-5.1.md`
- Plan: `docs/plans/inc-5.1-adj/PLAN-INC-5.1-ADJ.md`
- Feature: `tests/features/US-5.1.7-politica-tabs.feature`
