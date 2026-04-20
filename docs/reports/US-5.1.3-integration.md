# US-5.1.3 — Integracion

## Superficie Integrada

- `frontend/src/api/registro.ts`
- `frontend/src/components/organizador/EstadoAPBadge.tsx`
- `frontend/src/components/organizador/TablaInscriptos.tsx`
- `frontend/src/components/organizador/InscriptosPanel.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`

## Comportamiento Integrado

- El tab `Inscriptos` carga inscripciones del torneo.
- Para cada inscripto se carga el atleta asociado.
- Se cargan competencias del torneo y grillas por disciplina en paralelo.
- La UI cruza `atleta_id` + disciplina para mostrar AP registrado o Sin AP.
- El filtro de disciplina permite ver `Todas` o una disciplina especifica.
- Si no hay inscriptos se muestra mensaje vacio.

## Limitacion Documentada

El contrato actual de Registro no expone genero del atleta. La columna `Genero` muestra `Sin dato`.

## Validacion Ejecutada

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
