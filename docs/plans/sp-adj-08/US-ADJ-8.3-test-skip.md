# US-ADJ-8.3 — Tests automatizados acotados

**Fases:** 4, 5 y 6
**Estado:** Omitidas como ejecucion automatizada de UI
**Fecha:** 2026-04-22

## Motivo

La US modifica una interaccion modal React y el repositorio no tiene harness de componentes
o browser para validar clicks, inputs y estado disabled.

## Evidencia sustituida

- Feature BDD creado en `tests/features/US-ADJ-8.3-cancelacion-fuerte-torneo.feature`.
- Validacion estatica con `npm run lint`.
- Build TypeScript/Vite con `npm run build`.
