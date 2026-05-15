# Plan de Implementación: US-ADJ-10.1

**Historia:** US-ADJ-10.1 — Edición completa del torneo (H-02-06 UAT SP6)
**Estimación:** 2 puntos
**Estado:** ✅ COMPLETADO
**Fecha completado:** 2026-05-15

---

## Contexto

Fix funcional post-UAT INC-6.5. La pantalla de edición de torneo solo permitía modificar
disciplinas; los campos de metadatos (nombre, sede, fechas, categorías) estaban deshabilitados
y no existía endpoint `PUT /torneos/{id}`. Hallazgo H-02-06 UAT SP6 F-02.

---

## Invariantes

| ID | Invariante | Implementado en |
|----|------------|-----------------|
| INV-ADJ-10.1-01 | Solo `CREADO` o `INSCRIPCION_ABIERTA` permiten edición | `Torneo.actualizar()` + handler |
| INV-ADJ-10.1-02 | La edición de metadatos no afecta disciplinas | Scope del endpoint y del método de dominio |
| INV-ADJ-10.1-03 | Estado no editable → 409 en API, botón oculto en frontend | Router + `DetalleTorneoPage` |
| INV-ADJ-10.1-04 | Todos los campos editables son obligatorios (no PATCH parcial) | `ActualizarTorneoRequest` con campos requeridos |

---

## Tareas de Implementación

| ID | Tarea | Estimado | Real | Estado |
|----|-------|----------|------|--------|
| T1 | Agregar `EdicionNoPermitida` en `torneo/domain/exceptions.py` | 5 min | 5 min | ✅ |
| T2 | Agregar `Torneo.actualizar()` con precondición de estado | 20 min | 20 min | ✅ |
| T3 | `ActualizarTorneoCommand` + `ActualizarTorneoHandler` | 20 min | 20 min | ✅ |
| T4 | Endpoint `PUT /torneos/{torneo_id}` + `ActualizarTorneoRequest` | 20 min | 25 min | ✅ |
| T5 | `actualizarTorneo()` en `frontend/src/api/torneo.ts` | 10 min | 10 min | ✅ |
| T6 | `CrearTorneoPage` modo dual (crear / editar-disciplinas / editar-torneo) | 40 min | 50 min | ✅ |
| T7 | Botón "Editar torneo" en `DetalleTorneoPage` + ruta en `App.tsx` | 10 min | 10 min | ✅ |

---

## Métricas de Tiempo

| Fase | Estimado | Real | Varianza |
|------|----------|------|----------|
| BDD Scenarios | 15 min | 15 min | 0 min |
| Plan | 10 min | 10 min | 0 min |
| Implementation | 125 min | 140 min | +15 min |
| Unit Tests | 20 min | 25 min | +5 min |
| Integration Tests | 15 min | 20 min | +5 min |
| BDD Validation | 15 min | 15 min | 0 min |
| Quality Gates | 10 min | 10 min | 0 min |
| Documentation | 10 min | 10 min | 0 min |
| **Total** | **220 min** | **245 min** | **+25 min** |

---

## Lecciones Aprendidas

- ✅ Reutilizar `CrearTorneoPage` en modo dual evitó duplicar 200+ líneas de formulario
- ⚠️ `detectMode(pathname, torneoId)` debe leer `window.location.pathname` antes del render; el parámetro `torneoId` no distingue `/editar` de `/disciplinas`
- 💡 La precondición de estado en dominio Y en frontend (botón oculto) es doble garantía correcta: no depender solo de frontend para enforcement
