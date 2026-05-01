# US-5.1.3 — Contexto Validado

**Historia de Usuario:** Vista de inscriptos con estado de AP por atleta  
**Sprint:** SP5 — La Puesta en Marcha  
**Incremento:** INC-5.1  
**Producto:** frontend  
**Puntos:** 3  
**Estado inicial:** To Do

## Arquitectura

- Contexto obligatorio leido: `docs/contexto/ATARAXIADIVE-CONTEXT.md`.
- US-IEDD encontrada: `docs/specs/sp5/US-5.1.3.md`.
- Patron vigente: frontend React/Vite consumiendo BCs existentes.
- No requiere cambios backend segun spec.

## Alcance Validado

- Crear `frontend/src/api/registro.ts`.
- Reutilizar `frontend/src/api/competencia.ts`:
  - `fetchCompetenciasPorTorneo`
  - `fetchGrillaCompetencia`
- Extender el tab `Inscriptos` de `DetalleTorneoPage`.
- Crear componentes:
  - `TablaInscriptos`
  - `EstadoAPBadge`

## Contratos Disponibles

- `GET /registro/torneos/{torneo_id}/inscriptos`
  - Devuelve `inscripcion_id`, `atleta_id`, `torneo_id`, `disciplinas`, `estado`, `fecha_inscripcion`.
- `GET /registro/atletas/{atleta_id}`
  - Devuelve nombre, apellido, email, categoria, club y brevet.
- `GET /competencia?torneo_id={id}`
  - Devuelve competencias por torneo con disciplina.
- `GET /competencia/{competencia_id}/grilla?disciplina={disciplina}`
  - Devuelve entradas de grilla con `atleta_id`, `ap_declarado` y `unidad`.

## Brecha Detectada

La spec pide columna `Genero`, pero el endpoint `GET /registro/atletas/{id}` no expone genero.
La UI mostrara `Sin dato` para no inventar informacion ni cambiar backend fuera del alcance.

## Quality Gates

- `CLAUDE.md` presente.
- `tests/features/` presente.
- `frontend/package.json` presente.
- `pyproject.toml` contiene `tool.coverage`, `tool.codeguard` y `tool.designreviewer`.

## Listo Para Fase 1

Se puede proceder con escenarios BDD en `tests/features/US-5.1.3-vista-inscriptos-ap.feature`.
