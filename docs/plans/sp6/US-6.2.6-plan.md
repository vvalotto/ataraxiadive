# Plan de Implementacion — US-6.2.6

**US:** US-6.2.6 — Crear pagina de Podios  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** frontend  
**Branch:** `feature/US-6.2.6-podios`  
**Estimacion:** 70 min  
**Estado:** Implementado — pendiente de Fase 9  
**Fecha plan:** 2026-05-06  

---

## Contexto Validado

- Spec fuente: `docs/specs/sp6/US-6.2.6.md`
- Hallazgo fuente: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-08
- Fuente UX consultada:
  - `docs/design/ux/wireframes-organizador.md`
  - `docs/design/ux/prototipos/prototipo-organizador.html`
  - `docs/design/ux/flujos-por-rol.md`
  - `docs/design/ux/decisiones-frontend.md`
- Feature BDD creada:
  - `tests/features/US-6.2.6-pagina-podios.feature`
- Componentes afectados:
  - `frontend/src/pages/organizador/ResultadosPage.tsx`
  - `frontend/src/pages/organizador/PodiosPage.tsx`
  - `frontend/src/components/organizador/OrganizadorLayout.tsx`
  - `frontend/src/App.tsx`
- Gates frontend disponibles:
  - `cd frontend && npm run build`
  - `cd frontend && npm run lint`

---

## Decisiones Tecnicas

- Crear `PodiosPage.tsx` como pagina React separada y protegida por el mismo `RequireRole role="organizador"` que el resto de rutas del organizador.
- Reutilizar `PodiosSection` sin duplicar UI de podios.
- Copiar la logica de datos de podios desde `ResultadosPage` a `PodiosPage` dentro del alcance de esta US. No crear custom hook compartido ahora; la spec lo declara fuera de scope.
- Mantener `ResultadosPage` enfocada en ranking tecnico por disciplina: selector de disciplina, grilla, ranking y estado de publicacion.
- Agregar `Podios` a la navegacion de `OrganizadorLayout`, visible solo cuando exista `activeTournamentId`, igual que otras rutas de torneo activo.
- Mantener selector de torneo para `/organizador/podios` sin `torneo_id`, siguiendo el patron ya usado por `ResultadosPage`.
- No tocar backend ni contratos API.

---

## Tareas

### 1. Preparacion documental y BDD (10 min)

- [x] Agregar `## Fuente de verdad UX` a `docs/specs/sp6/US-6.2.6.md`.
- [x] Ajustar politica de tracking para usar `.venv/bin/python` y evitar `uv run`.
- [x] Crear `tests/features/US-6.2.6-pagina-podios.feature`.
- [x] Crear este plan de implementacion.

### 2. Pagina Podios (20 min)

- [x] Crear `frontend/src/pages/organizador/PodiosPage.tsx`.
- [x] Implementar lectura de `torneo_id` con `useSearchParams`.
- [x] Implementar selector de torneo cuando falta `torneo_id`, con CTA a `/organizador/podios?torneo_id=...`.
- [x] Cargar torneos, competencias, estados, rankings, overall e inscriptos con React Query.
- [x] Construir `podioDisciplina` y `podioOverall` con la logica existente de `ResultadosPage`.
- [x] Renderizar `OrganizadorLayout` con titulo `Podios`, subtitulo del torneo y navegacion activa.
- [x] Renderizar `PodiosSection` por disciplina seleccionada y `Overall`.

### 3. Limpieza de ResultadosPage (15 min)

- [x] Remover imports de `fetchOverall`, `PodiosSection` y `PodioCategoriaGroup` de `ResultadosPage.tsx`.
- [x] Remover `PODIO_CATEGORIAS`, `nombreVisible`, `buildPodioGroups`, `overallQuery`, `podioDisciplina` y `podioOverall` de `ResultadosPage.tsx`.
- [x] Remover el bloque visual de podios/overall al final de `ResultadosPage`.
- [x] Mantener intactos ranking por disciplina, selector de disciplina, grilla, estados de carga y boton `Publicar resultados`.

### 4. Rutas y navegacion (10 min)

- [x] Importar `PodiosPage` en `frontend/src/App.tsx`.
- [x] Registrar ruta `/organizador/podios` dentro de `RequireRole role="organizador"`.
- [x] Agregar `podios` al tipo `NavItem['key']`.
- [x] Agregar item `Podios` en `NAV_ITEMS`.
- [x] Actualizar `currentSection()` para marcar `/organizador/podios` como activo.
- [x] Verificar que `navHref()` conserva `torneo_id` para el item `Podios`.

### 5. Validacion frontend (10 min)

- [x] Ejecutar `cd frontend && npm run build`.
- [x] Ejecutar `cd frontend && npm run lint`.
- [x] Ejecutar `git diff --check`.
- [x] Revisar manualmente que `/organizador/resultados?torneo_id=...` ya no renderiza podios.
- [x] Revisar manualmente que `/organizador/podios?torneo_id=...` mantiene podios por disciplina y overall.

### 6. Cierre documental (5 min)

- [x] Actualizar estado de `docs/specs/sp6/US-6.2.6.md` a `Done` si la validacion pasa.
- [x] Actualizar `docs/specs/sp6/README.md`.
- [x] Generar waiver BDD/manual si no hay harness UI browser automatizado.
- [ ] Generar `docs/reports/US-6.2.6-report.md`.
- [ ] Cerrar tracker.
- [ ] Commit atomico con referencia `[US-6.2.6]`.

---

## Validacion Esperada

- `/organizador/podios?torneo_id={id}` muestra podios por disciplina y overall.
- `/organizador/resultados?torneo_id={id}` no muestra ninguna seccion de podios ni overall de premiacion.
- `/organizador/podios` sin query params muestra selector de torneo.
- La navegacion del torneo activo muestra `Podios` y preserva `torneo_id`.
- `Resultados` y `Podios` mantienen layout, tokens y guards del portal organizador.
- `npm run build`, `npm run lint` y `git diff --check` pasan.

---

## Riesgos

- Duplicar la logica de podios en `PodiosPage` puede generar deuda menor, pero evita un hook prematuro y respeta la nota de implementacion de la spec.
- `ResultadosPage` contiene selector de torneo local; duplicarlo en `PodiosPage` puede generar repeticion. Se acepta por alcance acotado de US.
- La BDD de frontend no tiene harness browser automatizado evidente en el repo; si no se incorpora uno, la Fase 6 debe documentarse con waiver/manual UI.
- El texto visible de podios menciona `puntaje FAAS` en la seccion por disciplina; esta US no cambia copy ni reglas de puntaje salvo que el build/lint exponga una inconsistencia.

---

## Punto de Aprobacion

Fase 2 queda detenida aca. No avanzar a implementacion hasta recibir aprobacion explicita del plan.

---

## Resultado de Validacion

| Gate | Resultado |
|---|---|
| `cd frontend && npm run build` | OK |
| `cd frontend && npm run lint` | OK |
| `git diff --check` | OK |
| BDD UI | Waiver documentado en `docs/reports/US-6.2.6-bdd-waiver.md` |

Notas:
- `ResultadosPage.tsx` ya no importa ni renderiza `PodiosSection`.
- `PodiosPage.tsx` concentra podios por disciplina y overall.
- La ruta `/organizador/podios` queda protegida por `RequireRole role="organizador"`.
