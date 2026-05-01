# Plan de Implementacion — US-5.1.6 Monitor de ejecucion

**Sprint:** SP5
**Incremento:** INC-5.1
**Producto:** frontend
**Patron:** React/Vite consumiendo APIs existentes de `competencia`
**Estimacion:** 3 puntos

## Alcance

Implementar el tab `Ejecucion` del detalle de torneo para que el organizador vea el avance
de las disciplinas activas, la performance actual y los proximos atletas, con refresco
automatico cada 30 segundos.

## Contratos Disponibles

- `GET /competencia?torneo_id={id}` retorna competencias asociadas al torneo.
- `GET /competencia/{id}/estado?disciplina={disciplina}` retorna estado de la competencia.
- `GET /competencia/{id}/progreso` retorna `total`, `ejecutadas`, `dns_count`, `completadas`.
- `GET /competencia/{id}/performance/actual` retorna performance actual o `null`.
- `GET /competencia/{id}/performance/proximas?disciplina={disciplina}` retorna proximos atletas.

## Tareas

### 1. API Frontend

- [ ] Extender `frontend/src/api/competencia.ts` con:
  - `ProgresoCompetenciaDto`.
  - `ProximoAtletaDto`.
  - `fetchProgresoCompetencia`.
  - `fetchProximasPerformances`.

### 2. Componentes UI

- [ ] Crear `ProgressBar`.
- [ ] Crear `MonitorDisciplina`.
- [ ] Crear `EjecucionPanel`.
  - Carga competencias del torneo.
  - Consulta estado de cada competencia.
  - Filtra competencias en `EnEjecucion`.
  - Carga progreso, performance actual y proximos en paralelo.
  - Refresca cada 30 segundos.
  - Muestra estados vacios y completados.

### 3. Integracion en DetalleTorneo

- [ ] Reemplazar placeholder del tab `Ejecucion`.
- [ ] Pasar `torneoId` a `EjecucionPanel`.
- [ ] Mantener consistencia visual con `GrillaPanel` y `JuecesPanel`.

### 4. Validacion

- [ ] `npm run build`.
- [ ] `npm run lint`.
- [ ] Registrar evidencia en `docs/reports/US-5.1.6-report.md`.

## Riesgos y Decisiones

- El endpoint de listado por torneo no trae `estado`; se resuelve consultando `fetchEstadoCompetencia` por competencia.
- La spec menciona `/competencia/{id}/proximas`; el router real expone `/competencia/{id}/performance/proximas`.
- La transicion a premiacion no se implementa en el monitor; se delega a `AccionesPanel` segun la nota de la spec.

## DoD

- El organizador ve una card por disciplina en ejecucion.
- Cada card muestra progreso `completadas / total`.
- La performance actual se muestra cuando existe.
- Si no hay performance actual, la card muestra `- En espera -`.
- Se muestran proximos atletas.
- Los datos se refrescan cada 30 segundos.
- Los estados vacios y de competencias completas son claros.
