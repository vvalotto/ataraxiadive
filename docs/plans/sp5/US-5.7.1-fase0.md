# Fase 0 — Validación de Contexto: US-5.7.1

## Contexto Validado

**Historia de Usuario:** US-5.7.1 — Mis torneos inscriptos con estado actual  
**Producto:** frontend  
**Puntos:** 3  
**Prioridad:** Alta para INC-5.7

## Arquitectura

- **Patrón:** React PWA dentro del producto `frontend`, consumiendo APIs existentes.
- **Scope:** `frontend/src/pages/atleta/AtletaTorneosPage.tsx`.
- **Backend:** sin cambios requeridos.
- **Datos existentes:**
  - `fetchAtletaMe()` obtiene `atleta_id`.
  - `listarInscripcionesDeAtleta(atleta_id)` obtiene torneos y disciplinas inscriptas.
  - `fetchTorneos()` obtiene torneos con estado normalizado.
  - `listarDisciplinasTorneo(torneo_id)` obtiene disciplinas publicadas del torneo.

## Fuente de Verdad UX

- `docs/design/ux/wireframes-atleta.md` — S-02 Torneos Disponibles.
- `docs/design/ux/flujos-por-rol.md` — Rol: Atleta.

## Quality Gates

- `frontend/package.json` define `npm run build` y `npm run lint`.
- `pyproject.toml` mantiene configuración de `codeguard`, `designreviewer` y `coverage` para backend.
- Para esta US frontend, el gate principal será `npm run build`; `npm run lint` se ejecutará si el entorno lo permite.

## Riesgos y Supuestos

- La spec pide badge `EN_EJECUCION`, `FINALIZADO`, `INSCRIPCION_CERRADA`; el tipo actual de `EstadoTorneo` usa `EJECUCION`, `CERRADO`, `PREMIACION`, etc. Se usará el label normalizado existente `getEstadoTorneoLabel`.
- `InscriptoDto.disciplinas` ya trae las disciplinas inscriptas del atleta; la sección "Mis torneos" debe usar ese dato, no todas las disciplinas del torneo.
- La sección "Inscripciones abiertas" debe seguir excluyendo torneos ya inscriptos.

## Listo Para Fase 1

La US está localizada, tiene criterios BDD definidos, fuente UX explícita y no requiere cambios de backend.
