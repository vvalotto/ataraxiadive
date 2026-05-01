# Integracion - US-5.1.7

## Estado

Waiver de automatizacion.

La US afecta una page React que consume `GET /torneos/{id}`. El repositorio no tiene
harness E2E/browser configurado para montar `DetalleTorneoPage` con React Query y Router
en escenarios de estados simulados.

## Flujo critico a validar manualmente

- `INSCRIPCION_ABIERTA`: tabs `Detalle` e `Inscriptos` habilitadas; `Grilla`, `Jueces`
  y `Ejecucion` visibles pero deshabilitadas.
- `PREPARACION`: `Detalle`, `Inscriptos`, `Grilla` y `Jueces` habilitadas;
  `Ejecucion` deshabilitada.
- `CANCELADO`: no se muestran tabs ni paneles operativos; aparece `Torneo cancelado`.
- Transicion/refetch hacia un estado menos avanzado: `activeTab` vuelve a `Detalle`.

## Gates sustitutos

- `npm run build`
- `npm run lint`
