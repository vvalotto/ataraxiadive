# Plan de Implementación — US-6.2.5

**US:** US-6.2.5 — Nuevo torneo: selección de grupos etarios  
**Incremento:** INC-6.2 — Ajustes Organizador  
**Producto:** torneo + frontend  
**Branch:** `feature-US-6.2.5-grupos-etarios`  
**Estimación:** 85 min  
**Estado:** Implementado — pendiente de Fase 9  
**Fecha plan:** 2026-05-06  

---

## Contexto Validado

- Spec fuente: `docs/specs/sp6/US-6.2.5.md`
- Hallazgo fuente: `docs/plans/sp6/PLAN-SP6.md` — UI-ORG-07
- Fuente UX consultada:
  - `docs/design/ux/wireframes-organizador.md`
  - `docs/design/ux/prototipos/prototipo-organizador.html`
- Feature BDD creada:
  - `tests/features/US-6.2.5-grupos-etarios-torneo.feature`
- Componentes afectados:
  - `src/torneo/domain/value_objects/`
  - `src/torneo/domain/aggregates/torneo.py`
  - `src/torneo/application/commands/crear_torneo.py`
  - `src/torneo/api/router.py`
  - `src/torneo/infrastructure/repositories/sqlite_torneo_repository.py`
  - `frontend/src/api/torneo.ts`
  - `frontend/src/pages/organizador/CrearTorneoPage.tsx`

---

## Decisiones Técnicas

- Crear `GrupoEtario` en `torneo/domain/value_objects/` en vez de importar `Categoria` desde `registro`. Esto evita acoplamiento directo entre bounded contexts.
- Persistir `grupos_etarios` como JSON text en SQLite, igual que `disciplinas_torneo`.
- Default retrocompatible: torneos existentes migran con `["SENIOR"]`.
- El campo será requerido en `CrearTorneoRequest`; payload omitido, vacío o inválido retorna 422.
- `GET /torneos` y `GET /torneos/{id}` retornan `grupos_etarios`.
- La UI inicia con `SENIOR` seleccionado y bloquea submit si el usuario deselecciona todo.

---

## Tareas

### 1. Dominio torneo — GrupoEtario (15 min)

- [x] Crear `src/torneo/domain/value_objects/grupo_etario.py` como `StrEnum` con `JUNIOR`, `SENIOR`, `MASTER`.
- [x] Agregar `grupos_etarios: frozenset[GrupoEtario]` a `Torneo` con default `SENIOR`.
- [x] Validar que la colección no esté vacía.
- [x] Mantener orden determinístico para persistencia/respuesta.

### 2. Application/API torneo (15 min)

- [x] Agregar `grupos_etarios` a `CrearTorneoCommand`.
- [x] Pasar los grupos al aggregate en `CrearTorneoHandler`.
- [x] Agregar `grupos_etarios: list[GrupoEtario]` a `CrearTorneoRequest`.
- [x] Agregar `grupos_etarios` a `TorneoResponse.from_torneo`.
- [x] Verificar 422 automático para omitido, vacío e inválido.

### 3. Persistencia SQLite (15 min)

- [x] Agregar columna `grupos_etarios TEXT NOT NULL DEFAULT '["SENIOR"]'` al create table.
- [x] Agregar migración idempotente `ALTER TABLE`.
- [x] Serializar/deserializar `grupos_etarios`.
- [x] Mantener compatibilidad con DBs existentes.

### 4. Frontend (15 min)

- [x] Agregar tipos `GrupoEtario` y `grupos_etarios` a DTO/payload en `frontend/src/api/torneo.ts`.
- [x] Agregar estado local `gruposSeleccionados` con default `['SENIOR']`.
- [x] Renderizar tres toggles `JUNIOR`, `SENIOR`, `MASTER` solo en alta de torneo.
- [x] Validar al menos un grupo seleccionado.
- [x] Incluir `grupos_etarios` en `crearTorneo(buildPayload())`.

### 5. Tests y BDD (15 min)

- [x] Agregar tests unitarios de dominio para default, selección múltiple y lista vacía.
- [x] Agregar tests de handler para persistir grupos.
- [x] Agregar tests de repositorio para migración/persistencia.
- [x] Agregar test API para POST/GET y rechazos 422.
- [x] Implementar steps BDD para `US-6.2.5-grupos-etarios-torneo.feature`.
- [x] Ejecutar BDD focal de US-6.2.5.

### 6. Validación frontend/backend (10 min)

- [x] Ejecutar tests focales de torneo.
- [x] Ejecutar `cd frontend && npm run build`.
- [x] Ejecutar ESLint focal sobre `CrearTorneoPage.tsx` y `api/torneo.ts`.
- [x] Ejecutar `cd frontend && npm run lint` para registrar estado global.
- [x] Ejecutar `git diff --check`.

### 7. Cierre documental (5 min)

- [x] Actualizar estado de `docs/specs/sp6/US-6.2.5.md` a `Done`.
- [x] Actualizar `docs/specs/sp6/README.md`.
- [ ] Generar `docs/reports/US-6.2.5-report.md`.
- [ ] Cerrar tracker.
- [ ] Commit atómico con referencia `[US-6.2.5]`.

---

## Validación Esperada

- `POST /torneos` con `grupos_etarios=["JUNIOR","MASTER"]` crea torneo.
- `GET /torneos/{id}` retorna `["JUNIOR","MASTER"]`.
- `POST /torneos` sin `grupos_etarios` retorna 422.
- `POST /torneos` con `grupos_etarios=[]` retorna 422.
- `POST /torneos` con valor inválido retorna 422.
- La UI muestra toggles de grupos etarios y default `SENIOR`.
- El submit queda bloqueado si no hay grupos.

---

## Riesgos

- Tests existentes que crean torneos vía API sin `grupos_etarios` deberán actualizarse, porque la US exige que el campo sea requerido.
- Tests o fixtures que instancian `Torneo` directamente no deberían romperse por el default `SENIOR`.
- El lint global frontend conserva un error preexistente en `frontend/src/pages/juez/GrillaPage.tsx`; se registrará si persiste.

---

## Resultado de Validación

| Gate | Resultado |
|---|---|
| `./.venv/bin/pytest tests/unit/torneo/domain/test_torneo.py tests/unit/torneo/application/test_crear_torneo.py tests/integration/torneo/test_sqlite_torneo_repository.py tests/integration/torneo/test_grupos_etarios_api.py tests/features/steps/grupos_etarios_torneo_steps.py` | OK — 41 passed |
| Regresión backend afectada (`identidad`, `torneo`, E2E US-3.3.2, BDD torneo API) | OK — 49 passed |
| `cd frontend && npm run build` | OK |
| `cd frontend && npm run lint` | OK |
| `git diff --check` | OK |

Notas:
- Se actualizó `frontend/src/pages/juez/GrillaPage.tsx` para corregir una dependencia faltante de `useMemo` que bloqueaba `npm run lint`.
- Se actualizaron helpers E2E de US-3.3.2 para usar el contrato vigente de `PerformancesAPAdapter` con proyección `competencias_por_torneo` e inscripciones como fuente de AP.
