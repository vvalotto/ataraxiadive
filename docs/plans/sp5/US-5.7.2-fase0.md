# Fase 0 — Validacion de Contexto: US-5.7.2

## Contexto Validado

**Historia de Usuario:** US-5.7.2 — Mi Grilla: posicion, OT y orden de salida por disciplina  
**Producto:** frontend  
**Puntos:** 5  
**Prioridad:** Alta para INC-5.7

## Arquitectura

- **Patron:** React PWA dentro del producto `frontend`, consumiendo APIs existentes.
- **Scope principal:** nueva pagina `frontend/src/pages/atleta/AtletaMiGrillaPage.tsx`.
- **Rutas:** registrar `/atleta/grilla/:competenciaId` en `frontend/src/App.tsx`.
- **Backend:** sin cambios requeridos.

## Fuente de Verdad UX

- `docs/design/ux/wireframes-atleta.md` — S-07 Mi Grilla.
- `docs/design/ux/flujos-por-rol.md` — Rol: Atleta.

## APIs y Datos Existentes

- `fetchAtletaMe()` obtiene el `atleta_id` real del BC Registro.
- `fetchGrillaCompetencia(competenciaId, disciplina)` obtiene `GrillaAtletaDto[]`.
- `fetchEstadoCompetencia(competenciaId, disciplina)` obtiene `grilla_confirmada`.
- `fetchCompetenciasPorTorneo(torneoId)` ya se usa en `portalData` para resolver links desde inscripciones.
- `loadAtletaPortalSnapshot()` ya compone torneo, inscripcion, competencia, AP, OT, andarivel y posicion.

## Decision Importante

La spec menciona `useAuthStore().userId`, pero ese valor es `usuario_id` de Identidad,
no `atleta_id` de Registro. Para identificar la fila propia y cumplir INV-5.7.2-02,
la implementacion debe usar `fetchAtletaMe().atleta_id`.

## Entradas de Navegacion

- `AtletaHomePage`: el link "Ver grilla" debe apuntar a la competencia concreta si hay `nextOt`.
- `AtletaMisInscripcionesPage`: para disciplinas con `competenciaId`, agregar accion "Ver grilla".

## Quality Gates

- `frontend/package.json` define `npm run build` y `npm run lint`.
- Para esta US frontend, el gate principal sera `npm run build` y ESLint focalizado sobre archivos modificados.
- El lint global ya tiene deuda fuera de scope documentada en US-5.7.1.

## Listo Para Fase 1

La US esta localizada, tiene criterios BDD definidos, fuente UX explicita y no requiere
cambios de backend.
