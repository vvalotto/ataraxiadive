# Reporte de Implementación — US-6.2.5

**US:** US-6.2.5 — Nuevo torneo: selección de grupos etarios  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** torneo + frontend  
**Branch:** `feature-US-6.2.5-grupos-etarios`  
**Fecha:** 2026-05-06  

---

## Resumen

Se agregó selección de grupos etarios al alta de torneo. El organizador puede
seleccionar `JUNIOR`, `SENIOR` y/o `MASTER`; `SENIOR` queda seleccionado por
defecto. El backend valida, persiste y expone los grupos en las respuestas de
torneo.

---

## Cambios Implementados

| Archivo | Cambio |
|---|---|
| `src/torneo/domain/value_objects/grupo_etario.py` | Nuevo value object `GrupoEtario` con orden determinístico |
| `src/torneo/domain/aggregates/torneo.py` | Agregado `grupos_etarios` con default `SENIOR` y validación no vacía |
| `src/torneo/application/commands/crear_torneo.py` | `CrearTorneoCommand` recibe y pasa grupos etarios al aggregate |
| `src/torneo/api/router.py` | `POST /torneos` valida `grupos_etarios`; responses incluyen el campo |
| `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py` | Nueva columna SQLite con migración idempotente y serialización JSON |
| `frontend/src/api/torneo.ts` | Tipos `GrupoEtario`, DTO y payload de creación actualizados |
| `frontend/src/pages/organizador/CrearTorneoPage.tsx` | Toggles de grupos etarios, default `SENIOR`, validación y payload |
| `tests/features/US-6.2.5-grupos-etarios-torneo.feature` | BDD de persistencia y rechazos 422 |
| `tests/features/steps/grupos_etarios_torneo_steps.py` | Steps BDD ejecutables para la US |
| `tests/integration/torneo/test_grupos_etarios_api.py` | Cobertura API POST/GET y validación |
| `docs/specs/sp6/US-6.2.5.md` | Estado `Done` y resultado de implementación |
| `docs/plans/sp6/US-6.2.5-plan.md` | Plan actualizado con checklist y validación real |

---

## BDD

Se generó y ejecutó BDD porque la US toca backend, API y persistencia.

Feature:
- `tests/features/US-6.2.5-grupos-etarios-torneo.feature`

Scenarios cubiertos:
- Crear torneo persiste `JUNIOR` y `MASTER`.
- Payload sin `grupos_etarios` retorna 422.
- Payload con lista vacía retorna 422.
- Payload con grupo inválido retorna 422.

---

## Validación

| Gate | Resultado |
|---|---|
| Tests focales torneo + BDD US-6.2.5 | OK — 41 passed |
| Regresión backend afectada | OK — 49 passed |
| `cd frontend && npm run build` | OK |
| `cd frontend && npm run lint` | OK |
| `git diff --check` | OK |

---

## Ajustes de Compatibilidad

- Tests y seeds existentes que crean torneos ahora envían `grupos_etarios`.
- DBs SQLite existentes migran con default `["SENIOR"]`.
- Se corrigió una dependencia faltante en `frontend/src/pages/juez/GrillaPage.tsx`
  que bloqueaba el lint global.
- Se actualizaron helpers E2E de US-3.3.2 para usar el contrato vigente de
  `PerformancesAPAdapter`.

---

## Alcance No Modificado

- No se filtran inscripciones por grupo etario.
- No se modifican rankings ni podios.
- No se acopla `torneo` al enum `Categoria` del bounded context `registro`.

---

## Resultado

`US-6.2.5` queda implementada, documentada y validada para el alcance definido.
