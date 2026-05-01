# US-5.2.2 — Documentacion de Cambios

**Fecha:** 2026-04-22
**Incremento:** INC-5.2 — Ejecucion por Disciplina

## Contrato API agregado

```http
POST /competencia/{competencia_id}/finalizar
Content-Type: application/json

{
  "disciplina": "DNF"
}
```

Respuesta exitosa: `204 No Content`.

Errores esperados:

- `409` si la competencia no esta en `EnEjecucion`.
- `409` si quedan performances pendientes.
- `204` sin duplicar eventos si la competencia ya estaba finalizada.

## Evento extendido

`CompetenciaFinalizada` agrega:

- `origen`: `automatico` o `manual`;
- `finalizada_por`: email/id del organizador cuando el origen es manual.

Eventos historicos sin esos campos siguen siendo validos y se leen como
`origen="automatico"`.

## UI

El tab `Ejecucion` del panel organizador muestra la accion `Finalizar prueba`
cuando la disciplina seleccionada esta en ejecucion.

La accion queda habilitada solo si:

- `progreso.total > 0`;
- `progreso.completadas == progreso.total`.

Si quedan pendientes, el detalle muestra la cantidad pendiente y no dispara el
endpoint.
