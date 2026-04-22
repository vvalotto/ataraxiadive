# Reporte de Implementacion: US-5.2.1

## Resumen Ejecutivo

- **Historia de Usuario:** US-5.2.1 — Vista maestro-detalle de disciplinas en ejecucion
- **Incremento:** INC-5.2 — Ejecucion por Disciplina
- **Producto:** `frontend`
- **Puntos estimados:** 3
- **Tiempo real tracker:** ~14 min al iniciar Fase 9
- **Estado:** Completado
- **Fecha:** 2026-04-22

---

## Componentes Implementados

- `frontend/src/api/competencia.ts`
  - Agregado `iniciarCompetencia()`.
  - Integra `POST /competencia/{competencia_id}/iniciar`.
  - Envia `disciplina` y `juez_id` usando headers autenticados existentes.

- `frontend/src/components/organizador/EjecucionPanel.tsx`
  - Convertido de monitor de disciplinas activas a vista maestro-detalle.
  - Maestro basado en disciplinas configuradas del torneo.
  - Enrichment con competencias materializadas, estado de competencia y progreso.
  - Detalle con grilla OT, progreso, atleta actual/proximos y hash de cierre si existe.
  - Accion `Habilitar disciplina` solo para disciplinas listas para iniciar.

---

## Artefactos Creados

- `docs/plans/sp5/US-5.2.1-fase0.md`
- `docs/plans/sp5/US-5.2.1-plan.md`
- `docs/plans/sp5/US-5.2.1-implementation-notes.md`
- `docs/plans/sp5/US-5.2.1-test-notes.md`
- `docs/plans/sp5/US-5.2.1-docs.md`
- `tests/features/US-5.2.1-ejecucion-disciplinas.feature`
- `docs/reports/US-5.2.1-report.md`

---

## Criterios de Aceptacion

- [x] El maestro muestra todas las disciplinas configuradas del torneo.
- [x] Cada disciplina muestra estado operativo derivado.
- [x] La seleccion de una disciplina abre detalle operativo.
- [x] El detalle muestra grilla, progreso y datos de ejecucion cuando hay competencia.
- [x] `Habilitar disciplina` se muestra solo cuando hay competencia, grilla confirmada y juez asignado.
- [x] La accion llama `POST /competencia/{id}/iniciar` con `disciplina` y `juez_id`.
- [x] Disciplinas sin juez o sin grilla quedan bloqueadas visualmente.
- [x] Disciplinas finalizadas se muestran en modo lectura con hash si esta disponible.

---

## Validaciones

| Validacion | Resultado |
|---|---|
| `npm run lint` | OK |
| `npm run build` | OK |
| BDD feature creado | OK |
| BDD automatizado UI | No disponible en el repo |

El frontend no tiene runner unitario ni harness browser configurado. Segun el ajuste local de
`implement-us`, la validacion tecnica para producto `frontend` se realizo con build/lint y la
validacion BDD queda como manual UI.

---

## Decisiones de Implementacion

- No se modifico backend: el endpoint de inicio ya existia.
- No se extrajo logica compartida con `JuecesPanel`; la duplicacion todavia es baja y especifica.
- El estado operativo se deriva localmente en `EjecucionPanel` para mantener el cambio acotado.
- La fuente primaria del maestro es `listarDisciplinasTorneo()`, no la proyeccion de competencias.

---

## Fuera de Alcance

- Cierre manual de disciplina (`Finalizar prueba`) queda para US-5.2.2.
- Tests automatizados de UI quedan pendientes hasta incorporar un harness frontend.
- No se agregan dependencias nuevas.

---

## Archivos de Codigo Modificados

- `frontend/src/api/competencia.ts`
- `frontend/src/components/organizador/EjecucionPanel.tsx`

---

## Proximos Pasos

- Ejecutar UAT manual del tab `Ejecucion` con un torneo en estado `EJECUCION`.
- Continuar con US-5.2.2 para cierre manual de prueba.
- Considerar Vitest/Testing Library o Playwright si SP5 requiere regresion frontend automatizada.
