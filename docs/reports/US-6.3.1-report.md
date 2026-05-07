# Reporte de Implementación — US-6.3.1

**US:** Inicio Atleta — "En línea" en Header + Sin "Hola" + Torneos en Curso Ordenados
**Incremento:** INC-6.3 — Ajustes Atleta
**Producto:** frontend
**Branch:** `feature-US-6.3.1-ajustes-inicio-atleta`
**Fecha:** 2026-05-07
**Estado:** Implementada, pendiente de PR

---

## Resumen

`US-6.3.1` ajusta la pantalla inicial del atleta sin tocar backend ni contratos HTTP.
La implementación agrega estado visual de conexión en el shell, elimina el saludo
redundante de la home y ordena las disciplinas de cada torneo activo según OT.

---

## Cambios Implementados

| Archivo | Cambio |
|---|---|
| `frontend/src/components/atleta/AtletaShell.tsx` | Agregado indicador estático "En línea" con punto verde junto a "AtaraxiaDive". |
| `frontend/src/pages/atleta/AtletaHomePage.tsx` | Eliminado "Hola"; agregado ordenamiento local de disciplinas por OT dentro de cada torneo. |
| `docs/plans/sp6/US-6.3.1-plan.md` | Plan generado y marcado como completado. |
| `docs/reports/US-6.3.1-bdd-waiver.md` | Waiver BDD por US frontend-only. |
| `docs/traceability/matrix.md` | Registrado INC-6.3 y evidencia de tests para `US-6.3.1`. |

---

## Criterios de Aceptación

| Criterio | Estado | Evidencia |
|---|---|---|
| Header muestra "En línea" con punto verde | ✅ Cumplido | `AtletaShell.tsx` |
| No aparece "Hola" antes del nombre | ✅ Cumplido | `AtletaHomePage.tsx` |
| Disciplinas con OT futuro se ordenan ascendente | ✅ Cumplido | `sortDisciplinasPorOt` |
| Disciplinas ya realizadas aparecen al final | ✅ Cumplido | `sortDisciplinasPorOt` |
| Disciplinas sin OT van antes de realizadas | ✅ Cumplido | `sortDisciplinasPorOt` |

---

## Validación

| Gate | Resultado |
|---|---|
| `npm run build` (`frontend/`) | ✅ Pasa |
| `npm run lint` (`frontend/`) | ✅ Pasa |
| BDD | Waiver formal por frontend puro |

El build emitió únicamente la advertencia existente de chunk mayor a 500 kB de Vite.

---

## Notas

- El indicador "En línea" es visual y estático, según la spec.
- El orden entre torneos no cambia; solo se ordena la lista interna de disciplinas de cada tarjeta.
- El working tree contiene cambios no relacionados en `.work/formacion/`; no forman parte de esta US.

---

## Artefactos

- Spec: `docs/specs/sp6/US-6.3.1.md`
- Plan: `docs/plans/sp6/US-6.3.1-plan.md`
- Waiver BDD: `docs/reports/US-6.3.1-bdd-waiver.md`
- Tracking: `.claude/tracking/US-6.3.1-tracking.json`

---

*Generado por Fase 9 `/implement-us` — US-6.3.1*
