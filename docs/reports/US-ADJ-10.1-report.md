# Reporte de Implementación: US-ADJ-10.1

## Resumen Ejecutivo

- **Historia de Usuario:** US-ADJ-10.1 — Edición completa del torneo (H-02-06 UAT SP6)
- **Puntos estimados:** 2
- **Tiempo estimado:** 220 min
- **Tiempo real:** 245 min
- **Varianza:** +25 min (+11%)
- **Estado:** ✅ COMPLETADO
- **Fecha completado:** 2026-05-15

---

## Componentes Implementados

### Backend — BC `torneo` (Hexagonal DDD)

- ✅ **`EdicionNoPermitida`** (`src/torneo/domain/exceptions.py`)
  - Excepción de dominio para estado inválido de edición

- ✅ **`Torneo.actualizar()`** (`src/torneo/domain/aggregates/torneo.py`)
  - Precondición: estado en `{CREADO, INSCRIPCION_ABIERTA}`
  - Lanza `EdicionNoPermitida` si estado no lo permite
  - Muta: nombre, descripcion, fecha_inicio, fecha_fin, sede, grupos_etarios
  - Re-ejecuta validaciones de nombre, fechas y grupos

- ✅ **`ActualizarTorneoCommand`** (`src/torneo/application/commands/actualizar_torneo.py`)
  - Frozen dataclass con todos los campos de metadata

- ✅ **`ActualizarTorneoHandler`** (`src/torneo/application/commands/actualizar_torneo.py`)
  - Carga torneo por ID, aplica cambios, persiste
  - Lanza `TorneoNoEncontrado` si no existe

- ✅ **`PUT /torneos/{torneo_id}`** (`src/torneo/api/router.py`)
  - 200: metadata actualizada
  - 404: torneo no encontrado
  - 409: estado no permite edición (`EdicionNoPermitida`)

### Frontend — Portal Organizador

- ✅ **`actualizarTorneo()`** (`frontend/src/api/torneo.ts`)
  - Llama `PUT /torneos/{id}` con payload de metadata

- ✅ **`CrearTorneoPage`** en modo dual (`frontend/src/pages/organizador/CrearTorneoPage.tsx`)
  - `detectMode(pathname, torneoId)` → `'crear' | 'editar-disciplinas' | 'editar-torneo'`
  - Modo `editar-torneo`: carga datos actuales, todos los campos habilitados, llama `PUT`
  - Modo `editar-disciplinas`: solo disciplinas editables (comportamiento anterior)

- ✅ **Botón "Editar torneo"** (`frontend/src/pages/organizador/DetalleTorneoPage.tsx`)
  - Visible solo si `estado === 'CREADO' || estado === 'INSCRIPCION_ABIERTA'`
  - Navega a `/organizador/torneos/:torneoId/editar`

- ✅ **Ruta** (`frontend/src/App.tsx`)
  - `/organizador/torneos/:torneoId/editar` → `<CrearTorneoPage />`

---

## API Endpoints

| Método | Ruta | Descripción | Auth |
|--------|------|-------------|------|
| PUT | `/torneos/{torneo_id}` | Actualizar metadata del torneo | organizador |

---

## Métricas de Calidad

| Métrica | Valor | Umbral | Estado |
|---------|-------|--------|--------|
| Pylint | ≥ 8.0/10 | ≥ 8.0 | ✅ |
| Complejidad Ciclomática | ≤ 5 | ≤ 10 | ✅ |
| Cobertura de Tests | ≥ 90% | ≥ 90% | ✅ |

---

## Tests Implementados

### Tests Unitarios (7 tests — `tests/unit/test_actualizar_torneo.py`)

- ✅ Torneo en CREADO permite edición
- ✅ Torneo en INSCRIPCION_ABIERTA permite edición
- ✅ Torneo en EJECUCION lanza EdicionNoPermitida
- ✅ Handler actualiza y persiste torneo
- ✅ Handler lanza TorneoNoEncontrado si no existe
- ✅ Campos mutados correctamente (nombre, sede, fechas)
- ✅ Disciplinas no afectadas por actualización

### Tests de Integración (6 tests — `tests/integration/test_actualizar_torneo_api.py`)

- ✅ PUT /torneos/{id} → 200 para torneo CREADO
- ✅ PUT /torneos/{id} → 200 para torneo INSCRIPCION_ABIERTA
- ✅ PUT /torneos/{id} → 404 para torneo inexistente
- ✅ PUT /torneos/{id} → 409 para torneo en EJECUCION
- ✅ Respuesta incluye datos actualizados
- ✅ Disciplinas no modificadas tras actualización

### Escenarios BDD (4 escenarios — `tests/features/US-ADJ-10.1-edicion-torneo.feature`)

- ✅ El organizador edita el nombre y sede de un torneo en CREADO
- ✅ El organizador corrige las categorías de un torneo en INSCRIPCION_ABIERTA
- ✅ No se puede editar un torneo en EJECUCION
- ✅ La edición no afecta las disciplinas del torneo

**Todos los tests pasando:** ✅ 17 passed, 0 failed

---

## Archivos Creados / Modificados

### Código de Producción

| Archivo | Cambio |
|---------|--------|
| `src/torneo/domain/exceptions.py` | Added `EdicionNoPermitida` |
| `src/torneo/domain/aggregates/torneo.py` | Added `actualizar()` method + `_ESTADOS_EDICION_VALIDOS` |
| `src/torneo/application/commands/actualizar_torneo.py` | **NUEVO** — command + handler |
| `src/torneo/api/router.py` | Added `ActualizarTorneoRequest` + `PUT /torneos/{id}` |
| `frontend/src/api/torneo.ts` | Added `ActualizarTorneoPayload` + `actualizarTorneo()` |
| `frontend/src/pages/organizador/CrearTorneoPage.tsx` | Rewrite con modo dual (3 modos) |
| `frontend/src/pages/organizador/DetalleTorneoPage.tsx` | Added "Editar torneo" button |
| `frontend/src/App.tsx` | Added route `/organizador/torneos/:torneoId/editar` |

### Tests

| Archivo | Cambio |
|---------|--------|
| `tests/features/US-ADJ-10.1-edicion-torneo.feature` | **NUEVO** — 4 escenarios |
| `tests/unit/test_actualizar_torneo.py` | **NUEVO** — 7 tests |
| `tests/integration/test_actualizar_torneo_api.py` | **NUEVO** — 6 tests |
| `tests/features/steps/edicion_torneo_steps.py` | **NUEVO** — step definitions |

### Documentación

| Archivo | Cambio |
|---------|--------|
| `docs/plans/sp-adj-10/US-ADJ-10.1-plan.md` | **NUEVO** — plan COMPLETADO |
| `docs/reports/US-ADJ-10.1-report.md` | **NUEVO** — este reporte |

---

## Criterios de Aceptación

- [x] El organizador puede editar nombre, sede, fechas y categorías desde la UI
- [x] La edición está disponible en estados CREADO e INSCRIPCION_ABIERTA
- [x] El botón "Editar torneo" no aparece en estado EJECUCION
- [x] `PUT /torneos/{id}` retorna 409 si el estado no lo permite
- [x] Las disciplinas configuradas no se alteran por la edición de metadata

**Todos los criterios cumplidos:** ✅

---

## Próximos Pasos

- Continuar con US-ADJ-10.3 y US-ADJ-10.4 del SP-ADJ-10
- Validar UI manualmente en entorno de staging antes de INC-6.7 Despliegue

---

**Reporte generado:** 2026-05-15
