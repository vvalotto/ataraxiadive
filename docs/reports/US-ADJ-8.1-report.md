# US-ADJ-8.1 — Reporte de Implementacion

**Fecha:** 2026-04-22
**Sprint:** SP-ADJ-08
**Estado:** Implementada

## Resumen

Se clarificaron estados, mensajes y jerarquia visual del panel organizador sin cambios
de reglas backend.

## Cambios principales

- Estado vacio de inscriptos: `Todavia no hay inscriptos para este torneo`.
- Panel de jueces diferencia carga, error y ausencia de asignaciones.
- Bloqueos de jueces y ejecucion indican accion concreta y tab destino.
- La seleccion de disciplina en ejecucion queda asociada visualmente con el detalle.

## Validaciones

- `npm run lint` — OK.
- `npm run build` — OK.

## Fases acotadas

- Tests unitarios/integracion omitidos por falta de harness React.
- BDD UI omitido como ejecucion automatizada; feature creado en
  `tests/features/US-ADJ-8.1-claridad-operativa-panel-organizador.feature`.

## Notas

- El texto `Pasar a premiacion` ya habia quedado aplicado en `US-ADJ-8.2`.
- Las acciones de habilitar/finalizar disciplina no cambiaron su comportamiento.
