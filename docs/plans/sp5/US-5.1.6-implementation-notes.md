# Notas de Implementacion — US-5.1.6

## Frontend

Se implemento el tab `Ejecucion` del detalle de torneo con:

- `ProgressBar`: barra visual de completadas sobre total.
- `MonitorDisciplina`: card por disciplina activa con progreso, atleta en curso y proximos.
- `EjecucionPanel`: orquestacion de carga y refresco cada 30 segundos.

## API Client

Se extendio `frontend/src/api/competencia.ts` con:

- `ProgresoCompetenciaDto`.
- `ProximoAtletaDto`.
- `fetchProgresoCompetencia`.
- `fetchProximasPerformances`.

## Integracion

`DetalleTorneoPage` ahora renderiza `EjecucionPanel` en el tab `Ejecucion`.

## Decisiones

- `GET /competencia?torneo_id={id}` no expone estado, por lo que `EjecucionPanel`
  consulta `fetchEstadoCompetencia` por cada competencia antes de filtrar.
- La spec menciona `/competencia/{id}/proximas`, pero el router real expone
  `/competencia/{id}/performance/proximas?disciplina=...`.
- El OT se obtiene cruzando los datos de performance/proximos con la grilla, porque los
  endpoints de monitor no devuelven `ot_programado` directamente.
- El boton real para transicionar a premiacion queda delegado a `AccionesPanel`, como
  indica la spec.

## Validaciones

- `npm run build`: aprobado.
- `npx eslint src vite.config.ts`: aprobado.
- `npm run lint`: bloqueado por `frontend/.vite/deps/react-router-dom.js`, artefacto
  generado preexistente y fuera del alcance de la US.
