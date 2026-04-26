# US-5.5.2 - Fase 0: Validacion de Contexto

**Fecha:** 2026-04-26
**Producto:** `frontend` + `registro` + `competencia`
**Incremento:** INC-5.5 - Portal atleta e inscriptos
**Spec canonica:** `docs/specs/sp5/US-5.5.2.md`

---

## Historia

**US:** US-5.5.2 - Vista del organizador de inscriptos con estado AP

Como **organizador**, quiero **ver a los inscriptos con sus datos completos, disciplinas y estado de AP dentro de la navegacion UX aprobada del panel organizador**, para **controlar quien termino su inscripcion y quien esta listo para pasar a grilla antes de cerrar el periodo de anuncios**.

---

## Fuentes de Verdad Validadas

- `docs/specs/sp5/US-5.5.2.md`
- `docs/design/ux/flujos-por-rol.md`
- `docs/design/ux/wireframes-organizador.md`
- `docs/design/ux/prototipos/prototipo-organizador.html`
- `docs/design/ux/wireframes-atleta.md`
- `.work/revision-sp5/04-hallazgos-ux-portal-atleta.md`

---

## Contexto Relevante

### Frontend organizador

- La vista ya existe dentro de `frontend/src/pages/organizador/DetalleTorneoPage.tsx` como tab `Inscriptos`.
- El panel actual usa `InscriptosPanel` + `TablaInscriptos`, pero la presentacion visible no respeta la semantica de la spec:
  - muestra `Sin AP` / `AP registrado`;
  - no expresa `AP pendiente` / `AP declarado` / `AP cerrado`;
  - no muestra un estado general de inscripcion;
  - no comunica lectura solamente cuando el torneo ya no esta en `INSCRIPCION_ABIERTA`.
- `OrganizadorLayout` y `DashboardPage` hoy usan una UI clara y sin navbar sticky tipo prototipo. La UX aprobada del organizador es dark, desktop-first y con barra superior persistente.

### Registro

- `GET /registro/torneos/{torneo_id}/inscriptos` ya existe, pero devuelve todas las inscripciones del torneo tal como salen del repositorio.
- `SQLiteInscripcionRepository.find_by_torneo()` no filtra `EstadoInscripcion.CANCELADA`.
- Eso viola `INV-5.5.2-05`: una inscripcion cancelada no debe figurar como participante operativo.

### Competencia

- La vista actual intenta inferir AP desde `fetchGrillaCompetencia()`.
- Ese enfoque solo funciona si ya existe competencia y la grilla contiene la performance del atleta.
- Para la necesidad operativa de esta US, el organizador debe poder ver el estado AP antes de depender de la grilla.

### Consistencia con atleta

- En `frontend/src/pages/atleta/portalData.ts`, el atleta ya usa la semantica visible:
  - `AP pendiente` si el torneo esta en `INSCRIPCION_ABIERTA` y no hay AP;
  - `AP declarado` si el torneo esta en `INSCRIPCION_ABIERTA` y hay AP;
  - `AP cerrado` cuando el torneo sale de `INSCRIPCION_ABIERTA`.
- `US-5.5.2` debe reutilizar ese contrato visible para cumplir `INV-5.5.2-04`.

---

## Gaps Detectados

1. Falta filtrar inscripciones canceladas en la consulta operativa del organizador.
2. Falta una composicion de datos que combine:
   - inscripcion activa,
   - datos visibles del atleta,
   - disciplinas,
   - AP declarado por disciplina,
   - estado visible derivado del torneo.
3. La vista actual depende de grilla para AP y por eso no cubre el periodo previo a generar competencias.
4. La UI visible no usa las labels ni badges aprobadas por la spec.
5. El layout del organizador no refleja la barra superior sticky del UX aprobado.

---

## Riesgos Detectados

- Rehacer todo el shell del organizador excede el alcance de esta US. Hay que acotar el ajuste UX a la navegacion y vista del area de torneo/inscriptos tocada por la historia.
- La proyeccion de AP puede requerir leer eventos o una tabla adaptadora de performances si se quiere evitar depender de grilla.
- Cambiar la consulta de inscriptos puede impactar tests de integracion de Registro.
- El worktree contiene cambios ajenos abiertos; esta US debe stagear y commitear solo archivos propios.

---

## Quality Gates Esperables

- `npm run build` en `frontend/`
- `npm run lint` en `frontend/`
- tests unitarios/integracion focalizados para la consulta de inscriptos operativos
- tests focalizados de API/composicion para el estado AP visible
- validacion BDD documental y reporte final

---

## Resultado

Contexto validado. La US queda lista para:

1. Fase 1 - Escenarios BDD
2. Fase 2 - Plan de implementacion
3. Espera de aprobacion explicita antes de Fase 3
