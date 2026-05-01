# Fase 0 - Validacion de Contexto - US-ADJ-9.6

## Contexto Validado

**Historia de Usuario:** `US-ADJ-9.6` - Reubicar Grilla, Jueces, Torneo y Audit Log en la arquitectura UX correcta
**Producto:** `ataraxiadive`
**Puntos estimados:** 3
**Prioridad:** Media-Alta
**Tipo:** ajuste transversal frontend

## Fuentes verificadas

- `docs/specs/sp-adj-09/US-ADJ-9.6.md`
- `docs/plans/sp-adj-09/PLAN-SP-ADJ-09.md`
- `docs/contexto/ATARAXIADIVE-CONTEXT.md`
- `docs/adr/ADR-005-bounded-contexts-ddd-estrategico.md`
- `docs/adr/ADR-006-estructura-bc-first.md`
- `docs/design/architecture.md`
- `docs/design/domain-model.md`
- `CLAUDE.md`

## Arquitectura y convenciones

- El proyecto mantiene arquitectura hexagonal DDD BC-first, pero esta US afecta solo el frontend del organizador.
- La spec confirma que no hay cambios de backend ni dominio.
- El shell del organizador ya existe y la US cierra la migracion UX de secciones primarias pendientes.
- La regla funcional central para esta US es separar navegacion primaria del shell vs vistas contextuales/detalle.

## Alcance tecnico confirmado

Artefactos de mayor impacto identificados en el repo:

- `frontend/src/components/organizador/OrganizadorLayout.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`
- `frontend/src/pages/organizador/OrganizadorGrillaPage.tsx`
- `frontend/src/pages/organizador/OrganizadorJuecesPage.tsx`
- `frontend/src/pages/organizador/TorneoCompetenciasPage.tsx`
- `frontend/src/pages/organizador/AuditoriaCompetenciaPage.tsx`
- `frontend/src/pages/organizador/AuditoriaPerformancePage.tsx`

Hallazgos iniciales:

- `DetalleTorneoPage` todavia concentra accesos primarios a `Grilla`, `Jueces`, `Resultados` y `Audit Log`.
- Las vistas de auditoria ya usan `OrganizadorLayout`, pero todavia muestran acciones redundantes de retorno.
- El shell ya tiene navbar persistente, por lo que la US deberia terminar de reasignar jerarquia y limpiar duplicaciones locales.

## Quality Gates del frontend

- `frontend/package.json` define `npm run build` y `npm run lint`.
- `frontend/eslint.config.js` existe y el workspace frontend tiene `tsconfig.json`.
- `tests/` existe con `features/`, `integration/`, `unit/` y `conftest.py`.
- Para esta US aplican validaciones de frontend manual + `npm run build` + `npm run lint`.

## Riesgos y focos de implementacion

- Evitar romper el flujo sin `torneo_id` que ya fue ajustado en `US-ADJ-9.3` a `US-ADJ-9.5`.
- Mantener visible la navbar principal incluso al entrar a auditorias contextuales.
- Reducir responsabilidad de `DetalleTorneoPage` sin perder acciones utiles de operacion sobre el torneo.

## Listo para Fase 1

- Spec localizada y consistente con el plan del sprint.
- Contexto de arquitectura y calidad validado.
- Alcance tecnico identificado sobre layout, rutas primarias y vistas detalle del organizador.
