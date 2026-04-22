# US-ADJ-8.1 — Tests automatizados acotados

**Fases:** 4, 5 y 6
**Estado:** Omitidas como ejecucion automatizada de UI
**Fecha:** 2026-04-22

## Motivo

La US modifica mensajes, estados visuales y jerarquia de componentes React del panel
organizador. El repositorio no tiene harness automatizado de componentes/browser para
assertions de DOM.

## Evidencia sustituida

- Feature BDD creado en `tests/features/US-ADJ-8.1-claridad-operativa-panel-organizador.feature`.
- Validacion estatica con `npm run lint`.
- Build TypeScript/Vite con `npm run build`.

## Pendiente si se agrega harness UI

Crear tests de componentes para `InscriptosPanel`, `JuecesPanel`, `TablaJueces` y
`EjecucionPanel`.
