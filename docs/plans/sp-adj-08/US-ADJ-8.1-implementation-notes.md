# US-ADJ-8.1 — Notas de implementacion

**Fecha:** 2026-04-22
**Fase:** 8 — Documentacion

## Cambios realizados

- `TablaInscriptos`
  - cambia el estado vacio a `Todavia no hay inscriptos para este torneo`.

- `JuecesPanel` / `TablaJueces`
  - diferencia error real con `No se pudieron cargar los jueces`;
  - muestra `Todavia no hay jueces asignados` cuando ninguna disciplina tiene juez;
  - expresa bloqueo por grilla con accion y tab destino.

- `EjecucionPanel`
  - refuerza seleccion visual de item maestro y detalle;
  - reemplaza labels tecnicos por estados operativos;
  - convierte bloqueos a mensajes accionables con tab destino.

## Validaciones

- `npm run lint` — OK.
- `npm run build` — OK.

## Fases acotadas

- Sin tests unitarios/integracion por falta de harness React.
- BDD UI no ejecutado; feature creado como especificacion.
