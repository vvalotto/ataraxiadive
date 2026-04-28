# US-5.6.6 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-28
**Producto:** `frontend`
**Incremento:** INC-5.6 - Resultados y podios por categoria/genero
**Spec canonica:** `docs/specs/sp5/US-5.6.6.md`

---

## Historia

**US:** US-5.6.6 - UI podios por categoria y genero

Como **organizador**, quiero **ver los podios de cada disciplina separados por las 6 categorias y el overall del torneo cuando todas las disciplinas esten cerradas**, para **proclamar los campeones por division al cierre de cada disciplina y del torneo**.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp5/US-5.6.6.md`
- `docs/specs/sp5/US-5.6.5.md`
- `docs/plans/sp5/PLAN-SP5.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/decisiones-frontend.md`

---

## Contexto Relevante

### Frontend actual

- `frontend/src/pages/organizador/ResultadosPage.tsx` ya implementa `US-5.6.5`.
- La pantalla actual resuelve:
  - selector de torneo;
  - selector de disciplina;
  - tabla de ejecucion por OT;
  - polling del ranking por disciplina.
- `frontend/src/components/organizador/TablaDisciplinaResultados.tsx` ya combina grilla, ranking e inscriptos por `atleta_id`.
- `frontend/src/components/organizador/FilaResultado.tsx` ya define parte del lenguaje visual de resultados: chips, tipografia mono y puntos destacados.

### API disponible

- `frontend/src/api/resultados.ts` ya expone:
  - `fetchRankingCompetencia()`
  - `fetchOverall()`
- El tipo `OverallDto` ya contempla `rankings` por categoria con `puntos_overall`.

### Datos auxiliares

- `listarInscriptosDetalle()` aporta `nombre`, `apellido`, `categoria` y `club`.
- Para podios por disciplina hay que enriquecer el ranking con `club` y nombre visible desde inscriptos.
- Para overall no existe `RP`; la spec pide mantener la misma grilla de podios, por lo que la fila overall debera mostrar `RP` vacio o placeholder no disponible.

### UX aprobada

- La spec de `US-5.6.6` ubica los podios dentro de la misma `ResultadosPage`, debajo de la tabla.
- `wireframes-organizador.md` para `S-04` define una segunda vista de resultados y un estado vacio de overall:
  - "Disponible al cerrar todas las disciplinas"
- La implementacion real del repo ya diverge del layout two-column del wireframe; esta US debe integrarse sobre la pagina existente sin rehacer el shell.

---

## Gaps Detectados

1. No existe ninguna seccion de podios en `ResultadosPage`.
2. No existen componentes `PodiosSection`, `PanelCategoria` ni `FilaPodio`.
3. `fetchOverall()` esta disponible pero no se consume en la pagina.
4. Falta la logica de visibilidad:
   - podios solo con disciplina finalizada;
   - overall bloqueado mientras no todas las disciplinas esten cerradas.
5. Falta una definicion UI concreta para `RP` en overall, ya que el DTO no lo expone.

---

## Riesgos Detectados

- El estado real de cierre de una disciplina debe inferirse desde la lista de competencias; si la API usa estados heterogeneos, hay que normalizar la deteccion en frontend.
- El overall puede devolver error o no existir aun aunque todas las disciplinas figuren finalizadas; la UI debe degradar sin romper la pagina.
- La spec de podios exige 6 divisiones fijas; no hay que generar paneles dinamicos desde el payload.
- El repo tiene trackers viejos abiertos; el tracking de esta US debe escribirse por ID explicito para no corromper otros archivos.

---

## Quality Gates Esperables

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- validacion BDD documental/manual para la UI
- reporte final en `docs/reports/US-5.6.6-report.md`

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. Espera de aprobacion explicita antes de Fase 3
