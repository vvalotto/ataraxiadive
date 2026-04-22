# US-ADJ-8.2 — Validacion BDD acotada

**Fase:** 6 — Validacion BDD
**Estado:** Omitida como ejecucion automatizada
**Fecha:** 2026-04-22

## Motivo

La US cubre comportamiento observable de frontend organizador:

- selector de grilla filtrado por disciplinas del torneo;
- bloqueo visual de `Pasar a premiacion`;
- no disparar la transicion si hay disciplinas pendientes.

El repositorio no tiene harness automatizado de browser/DOM para ejecutar steps BDD de
componentes React. Crear ese harness excede el alcance de esta US de ajuste.

## Evidencia sustituida

- Se creo el feature BDD:
  `tests/features/US-ADJ-8.2-restringir-operaciones-torneo-fase.feature`.
- La regla backend critica queda cubierta por tests unitarios e integracion HTTP.
- La validacion frontend se cubre con `npm run build` y `npm run lint`.

## Pendiente si se agrega harness UI

Implementar steps para verificar selectores, botones bloqueados y mensajes visibles
en `DetalleTorneoPage`, `GrillaPanel` y `AccionesPanel`.
