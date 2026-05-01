# US-5.1.3 — Reporte Final

**US:** Vista de inscriptos en Preparacion — estado de AP por atleta  
**Sprint:** SP5  
**Incremento:** INC-5.1  
**Branch:** `feature/US-5.1.3-vista-inscriptos`  
**Producto:** frontend  
**Estado:** Implementada

## Resultado

Se implemento el tab `Inscriptos` del detalle del torneo:

- Cliente `registro.ts` para listar inscriptos y obtener datos de atleta.
- `InscriptosPanel` que cruza inscripciones, atletas, competencias y grillas.
- `TablaInscriptos` read-only con filtro por disciplina.
- `EstadoAPBadge` para AP registrado o Sin AP.
- Mensajes de carga, error y estado vacio.
- Integracion en `DetalleTorneoPage`.

## Archivos Principales

- `frontend/src/api/registro.ts`
- `frontend/src/components/organizador/EstadoAPBadge.tsx`
- `frontend/src/components/organizador/TablaInscriptos.tsx`
- `frontend/src/components/organizador/InscriptosPanel.tsx`
- `frontend/src/pages/organizador/DetalleTorneoPage.tsx`

## Artefactos del Pipeline

- `docs/reports/US-5.1.3-context.md`
- `tests/features/US-5.1.3-vista-inscriptos-ap.feature`
- `docs/plans/sp5/US-5.1.3-plan.md`
- `docs/reports/US-5.1.3-test-strategy.md`
- `docs/reports/US-5.1.3-integration.md`
- `docs/reports/US-5.1.3-bdd-waiver.md`
- `quality/reports/codeguard/US-5.1.3-quality.json`
- `docs/traceability/matrix.md`
- `.claude/tracking/US-5.1.3-tracking.json`

## Validacion

- `npm run build`: aprobado.
- `npx eslint src`: aprobado.
- `npm run lint`: no aprobado por archivos generados preexistentes en `frontend/.vite/deps/react-router-dom.js`, fuera del codigo fuente modificado.

## Decisiones

- No se modifico backend. La vista usa contratos existentes.
- El campo `Genero` muestra `Sin dato` porque Registro no expone genero en `GET /registro/atletas/{id}`.
- Si no existe competencia o grilla para una disciplina, la UI muestra `Sin AP`.

## Pendientes Para US Posteriores

- Exponer genero desde Registro cuando se implemente el formulario completo de inscripcion.
- `US-5.1.4`: usar el estado AP para habilitar flujo de grilla.
